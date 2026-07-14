"""Session-level provider injection for the Stage 5 Gate 2 refactor.

This adapter proves that one provider instance can serve the complete Stage 4
lifecycle without changing replay output.  It is not yet a live-council engine:
fixture-driven debate routing remains in :mod:`imperium.offline.engine` and must
be removed before Gate 3.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from imperium.domain.enums import ArtifactKind, ChallengePhase, DeliberationStage
from imperium.domain.models import ModelCallRecord, StageContext
from imperium.offline.engine import (
    OfflineDeliberationEngine,
    _append_unique,
    _artifact_id,
    _call_key,
    _context_hash,
    _replace_session,
    _update_record,
)
from imperium.offline.models import OfflineScenario, OfflineSession, TurnTrace
from imperium.offline.persistence import load_session, write_checkpoint
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import CallMetadata, ModelProvider, ProviderError
from imperium.providers.replay import ReplayProvider

OutputT = TypeVar("OutputT", bound=BaseModel)
ApplyArtifact = Callable[[OfflineSession, OutputT], OfflineSession]


class ProviderBoundDeliberationEngine(OfflineDeliberationEngine):
    """Run one deliberation through one provider instance.

    When no provider is supplied, one :class:`ReplayProvider` is constructed
    from the complete scenario script at session start.  A caller may inject a
    simulated provider for Gate 2 tests, but no live CLI entry point exposes
    this class.
    """

    def __init__(
        self,
        *,
        provider: ModelProvider | None = None,
        model: str = "offline-replay",
        max_context_bytes: int = 262_144,
    ) -> None:
        super().__init__(model=model)
        if max_context_bytes <= 0:
            raise ValueError("max_context_bytes must be positive")
        self._configured_provider = provider
        self._session_provider: ModelProvider | None = None
        self.max_context_bytes = max_context_bytes

    @property
    def session_provider(self) -> ModelProvider | None:
        """Return the provider selected for the current or most recent run."""

        return self._session_provider

    def _prepare_provider(self, scenario: OfflineScenario) -> None:
        self._session_provider = self._configured_provider or ReplayProvider(
            build_replay_records(scenario, model=self.model)
        )

    async def run(
        self,
        scenario: OfflineScenario,
        *,
        project_root: str | Path,
        output_dir: str | Path,
        interrupt_after: str | None = None,
    ) -> OfflineSession:
        """Create one session provider, then execute the existing lifecycle."""

        self._prepare_provider(scenario)
        return await super().run(
            scenario,
            project_root=project_root,
            output_dir=output_dir,
            interrupt_after=interrupt_after,
        )

    async def resume(
        self,
        checkpoint: str | Path,
        *,
        output_dir: str | Path | None = None,
        evidence_replacements: Iterable = (),
        interrupt_after: str | None = None,
    ) -> OfflineSession:
        """Recreate replay state or reuse the injected provider before resume."""

        saved = load_session(checkpoint)
        self._prepare_provider(saved.scenario)
        return await super().resume(
            checkpoint,
            output_dir=output_dir,
            evidence_replacements=evidence_replacements,
            interrupt_after=interrupt_after,
        )

    async def _call(
        self,
        session: OfflineSession,
        *,
        expected: OutputT,
        resulting_stage: DeliberationStage,
        procedural_role: str,
        prompt_path: str,
        context: StageContext,
        apply: ApplyArtifact[OutputT],
        output_dir: str | Path,
        member_id: str | None = None,
        phase: ChallengePhase | None = None,
        round_number: int | None = None,
        subject: str | None = None,
        interrupt_after: str | None = None,
    ) -> tuple[OfflineSession, OutputT]:
        """Invoke the session provider while preserving Stage 4 checkpoints."""

        key = _call_key(
            resulting_stage=resulting_stage,
            role=procedural_role,
            output_type=type(expected),
            member_id=member_id,
            phase=phase,
            round_number=round_number,
            subject=subject,
        )
        if key in set(session.completed_call_keys):
            return session, expected

        if context.member is not None:
            if context.member.member_id != member_id:
                raise ValueError("advocate context must contain only the active member profile")
            if any(
                reference.artifact_type == ArtifactKind.COUNCIL_SNAPSHOT.value
                for reference in context.visible_artifacts
            ):
                raise ValueError("advocate context cannot expose the complete council registry")

        input_text = context.model_dump_json()
        input_bytes = len(input_text.encode("utf-8"))
        if input_bytes > self.max_context_bytes:
            raise ProviderError(
                f"context for {key} is {input_bytes} bytes; "
                f"limit is {self.max_context_bytes} bytes"
            )

        provider = self._session_provider
        if provider is None:
            raise ProviderError("session provider was not prepared before model invocation")

        prompt = session.runtime.source(prompt_path)
        pending = _replace_session(
            session,
            pending_call_key=key,
            checkpoint_sequence=session.checkpoint_sequence + 1,
        )
        write_checkpoint(pending, output_dir)

        result = await provider.generate(
            model=self.model,
            instructions=prompt.content,
            input_text=input_text,
            output_type=type(expected),
            metadata=CallMetadata(
                session_id=session.session_id,
                call_key=key,
                stage=session.record.stage,
                member_id=member_id,
            ),
        )

        committed = apply(pending, result.output)
        call_record = ModelCallRecord(
            call_id=key,
            provider=result.provider,
            model=result.model,
            stage=session.record.stage,
            member_id=member_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )
        record = _update_record(
            committed.record,
            model_calls=_append_unique(
                committed.record.model_calls,
                call_record,
                identity=lambda item: item.call_id,
            ),
        )
        trace = TurnTrace(
            call_key=key,
            stage=session.record.stage,
            procedural_role=procedural_role,
            member_id=member_id,
            prompt_path=prompt.path,
            prompt_sha256=prompt.sha256,
            visible_artifact_ids=tuple(
                reference.artifact_id for reference in context.visible_artifacts
            ),
            profile_member_id=context.member.member_id if context.member else None,
            input_sha256=_context_hash(context),
            output_artifact_id=_artifact_id(result.output),
            output_type=type(result.output).__name__,
            provider=result.provider,
            model=result.model,
        )
        committed = _replace_session(
            committed,
            record=record,
            turns=(*committed.turns, trace),
            completed_call_keys=(*committed.completed_call_keys, key),
            pending_call_key=None,
            checkpoint_sequence=committed.checkpoint_sequence + 1,
        )
        checkpoint = write_checkpoint(committed, output_dir)
        if interrupt_after == key:
            from imperium.offline.engine import OfflineInterrupted

            raise OfflineInterrupted(key, checkpoint)
        return committed, result.output
