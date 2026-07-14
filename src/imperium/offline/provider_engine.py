"""Provider-authoritative Stage 5 Gate 2 orchestration.

The existing Stage 4 lifecycle remains the sole lifecycle. This subclass replaces
only provider invocation, debate routing, and evidence-disposition boundaries so
validated provider artifacts—not replay fixtures—control downstream behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from imperium.domain.enums import (
    ArtifactKind,
    ChallengeDisposition,
    ChallengePhase,
    DeliberationStage,
    SessionStatus,
)
from imperium.domain.models import (
    ActionablePlan,
    Adjudication,
    ChallengeResponse,
    EvidenceResolution,
    FrameRegister,
    Interpretation,
    ModelCallRecord,
    Revision,
    StageContext,
    StrategyProposal,
)
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengeAssignment,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
)
from imperium.domain.protocol_trace import ClaimRegisterSnapshot
from imperium.engine.context import ContextBuilder
from imperium.engine.protocol_rules import (
    evidence_session_status,
    validate_challenge_artifact,
    validate_challenge_plan,
    validate_challenge_response,
    validate_challenge_round_outputs,
    validate_continuation_decision,
    validate_evidence_resolutions,
    validate_stage_inputs,
    validate_stage_outputs,
)
from imperium.offline.engine import (
    OfflineDeliberationEngine,
    OfflineInterrupted,
    _append_unique,
    _artifact_id,
    _call_key,
    _context_hash,
    _profile,
    _reference,
    _replace_session,
    _source_reference,
    _update_record,
    _update_trace,
    _validate_visible,
)
from imperium.offline.models import (
    DebateRoundFixture,
    EvidenceDispositionEvent,
    LineageLink,
    OfflineScenario,
    OfflineSession,
    TurnTrace,
)
from imperium.offline.persistence import load_session, write_checkpoint, write_review_artifacts
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import CallMetadata, ModelProvider, ProviderError
from imperium.providers.replay import ReplayProvider

OutputT = TypeVar("OutputT", bound=BaseModel)
ApplyArtifact = Callable[[OfflineSession, OutputT], OfflineSession]


class MissingEvidenceDisposition(ProviderError):
    """Raised when provider-generated evidence lacks an explicit operator disposition."""


class ProviderBoundDeliberationEngine(OfflineDeliberationEngine):
    """Run one deliberation through one provider instance.

    Replay remains the default. The class is intentionally absent from every
    live CLI until failure accounting and cumulative budgets are implemented.
    """

    def __init__(
        self,
        *,
        provider: ModelProvider | None = None,
        model: str = "offline-replay",
        max_context_bytes: int = 262_144,
        evidence_resolutions: Mapping[str, EvidenceResolution] | None = None,
    ) -> None:
        super().__init__(model=model)
        if max_context_bytes <= 0:
            raise ValueError("max_context_bytes must be positive")
        self._configured_provider = provider
        self._configured_evidence_resolutions = dict(evidence_resolutions or {})
        self._session_provider: ModelProvider | None = None
        self._session_evidence_resolutions: dict[str, EvidenceResolution] = {}
        self.max_context_bytes = max_context_bytes

    @property
    def session_provider(self) -> ModelProvider | None:
        """Return the provider selected for the current or most recent run."""

        return self._session_provider

    def _prepare_provider(self, scenario: OfflineScenario) -> None:
        self._session_provider = self._configured_provider or ReplayProvider(
            build_replay_records(scenario, model=self.model)
        )
        defaults = {
            item.evidence_request_id: item
            for item in (
                *scenario.frame_evidence_resolutions,
                *scenario.proposal_evidence_resolutions,
            )
        }
        defaults.update(self._configured_evidence_resolutions)
        self._session_evidence_resolutions = defaults

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
        evidence_replacements: Iterable[EvidenceResolution] = (),
        interrupt_after: str | None = None,
    ) -> OfflineSession:
        """Resume provider state without mapping accepted request IDs through fixtures."""

        source = Path(checkpoint)
        session = load_session(source)
        destination = Path(output_dir) if output_dir is not None else source.parent
        replacements = tuple(evidence_replacements)
        self._prepare_provider(session.scenario)
        if replacements:
            accepted_request_ids = {
                item.evidence_request_id for item in session.record.evidence_requests
            }
            unknown = {
                item.evidence_request_id
                for item in replacements
                if item.evidence_request_id not in accepted_request_ids
            }
            if unknown:
                raise ValueError(
                    "evidence replacements reference requests not accepted in the session: "
                    f"{sorted(unknown)}"
                )
            self._session_evidence_resolutions.update(
                {item.evidence_request_id: item for item in replacements}
            )
            record = _update_record(session.record, status=SessionStatus.ACTIVE)
            session = _replace_session(
                session,
                record=record,
                failure_reason=None,
                pending_call_key=None,
                checkpoint_sequence=session.checkpoint_sequence + 1,
            )
            write_checkpoint(session, destination)
        elif session.status in {SessionStatus.WAITING_FOR_USER, SessionStatus.PAUSED}:
            raise ValueError("waiting or paused sessions require explicit evidence replacements")
        return await self._execute(
            session,
            output_dir=destination,
            interrupt_after=interrupt_after,
        )

    async def _execute(
        self,
        session: OfflineSession,
        *,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        if session.artifact_authority != "provider":
            session = _replace_session(
                session,
                artifact_authority="provider",
                checkpoint_sequence=session.checkpoint_sequence + 1,
            )
            write_checkpoint(session, output_dir)
        return await super()._execute(
            session,
            output_dir=output_dir,
            interrupt_after=interrupt_after,
        )

    def _accepted_output(
        self,
        session: OfflineSession,
        call_key: str,
        output_type: type[OutputT],
    ) -> OutputT:
        try:
            turn = next(item for item in session.turns if item.call_key == call_key)
        except StopIteration as exc:
            raise ProviderError(
                f"completed call {call_key!r} has no committed turn trace"
            ) from exc

        artifact_id = turn.output_artifact_id
        candidates: list[BaseModel] = []
        if output_type is Interpretation:
            candidates.extend(session.record.interpretations)
        elif output_type is FrameRegister and session.record.frame_register is not None:
            candidates.append(session.record.frame_register)
        elif output_type is ClaimRegister:
            candidates.extend(
                snapshot.claim_register
                for snapshot in session.protocol_trace.claim_register_snapshots
            )
        elif output_type is ChallengePlan:
            candidates.extend(session.protocol_trace.challenge_plans)
        elif output_type is ChallengeArtifact:
            candidates.extend(session.protocol_trace.challenges)
        elif output_type is ChallengeResponse:
            candidates.extend(session.record.challenge_responses)
        elif output_type is ContinuationDecision:
            candidates.extend(session.protocol_trace.continuation_decisions)
        elif output_type is StrategyProposal:
            candidates.extend(session.record.proposals)
        elif output_type is Revision:
            candidates.extend(session.record.revisions)
        elif output_type is Adjudication and session.record.adjudication is not None:
            candidates.append(session.record.adjudication)
        elif output_type is ActionablePlan and session.record.plan is not None:
            candidates.append(session.record.plan)

        for candidate in candidates:
            if _artifact_id(candidate) == artifact_id:
                return output_type.model_validate(candidate.model_dump(mode="python"))
        raise ProviderError(
            f"completed call {call_key!r} references missing {output_type.__name__} "
            f"artifact {artifact_id!r}"
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
            return session, self._accepted_output(session, key, type(expected))

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
        if member_id is not None:
            authored_member_id = getattr(result.output, "member_id", None)
            if authored_member_id is not None and authored_member_id != member_id:
                raise ProviderError(
                    f"provider output member {authored_member_id!r} does not match "
                    f"active member {member_id!r} for {key}"
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
            raise OfflineInterrupted(key, checkpoint)
        return committed, result.output

    @staticmethod
    def _template_for_round(
        rounds: tuple[DebateRoundFixture, ...],
        round_number: int,
    ) -> DebateRoundFixture:
        return rounds[min(round_number - 1, len(rounds) - 1)]

    @staticmethod
    def _challenge_exemplar(
        rounds: tuple[DebateRoundFixture, ...],
        assignment: ChallengeAssignment,
    ) -> ChallengeArtifact:
        for fixture in rounds:
            for challenge in fixture.challenges:
                if challenge.challenge_id == assignment.challenge_id:
                    return challenge
        return ChallengeArtifact(
            challenge_id=assignment.challenge_id,
            phase=assignment.phase,
            round_number=assignment.round_number,
            challenger_member_id=assignment.challenger_member_id,
            target_member_id=assignment.target_member_id,
            target_artifact_id=assignment.target_artifact_id,
            target_claim_id=assignment.target_claim_id,
            statement="Schema exemplar for an assigned consequential challenge.",
            failure_consequence="Schema exemplar; the provider must supply the real consequence.",
        )

    @staticmethod
    def _response_exemplar(
        rounds: tuple[DebateRoundFixture, ...],
        assignment: ChallengeAssignment,
    ) -> ChallengeResponse:
        for fixture in rounds:
            for response in fixture.responses:
                if response.challenge_id == assignment.challenge_id:
                    return response
        return ChallengeResponse(
            challenge_id=assignment.challenge_id,
            member_id=assignment.target_member_id,
            disposition=ChallengeDisposition.DEFEND,
            response="Schema exemplar; the assigned target must provide the real response.",
        )

    @staticmethod
    def _snapshot(
        session: OfflineSession,
        phase: ChallengePhase,
        round_number: int,
    ) -> ClaimRegisterSnapshot | None:
        return next(
            (
                item
                for item in session.protocol_trace.claim_register_snapshots
                if item.phase is phase and item.round_number == round_number
            ),
            None,
        )

    @staticmethod
    def _claims_with_new_input(
        previous: ClaimRegister | None,
        current: ClaimRegister,
    ) -> tuple[str, ...]:
        if previous is None:
            return tuple(claim.claim_id for claim in current.claims)
        prior = {claim.claim_id: claim for claim in previous.claims}
        return tuple(
            claim.claim_id
            for claim in current.claims
            if claim.claim_id not in prior or claim != prior[claim.claim_id]
        )

    async def _challenge_phase(
        self,
        session: OfflineSession,
        *,
        rounds: tuple[DebateRoundFixture, ...],
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        """Route debate exclusively from committed provider artifacts."""

        if not rounds:
            raise ValueError("challenge phases require at least one schema/replay template")
        phase = rounds[0].phase
        resulting_stage = (
            DeliberationStage.FRAME_CHALLENGES_COMPLETE
            if phase is ChallengePhase.FRAME
            else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
        )
        contract = session.runtime.protocol.contract_for(resulting_stage)
        policy = session.runtime.protocol.challenge_policy
        prior_plans: list[ChallengePlan] = []

        for round_number in range(1, policy.maximum_rounds_per_phase + 1):
            template = self._template_for_round(rounds, round_number)
            snapshot_round = round_number - 1
            snapshot = self._snapshot(session, phase, snapshot_round)
            previous_snapshot = (
                self._snapshot(session, phase, snapshot_round - 1)
                if snapshot_round > 0
                else None
            )

            if snapshot is None:
                context = ContextBuilder.seneschal_stage(
                    stage=session.record.stage,
                    request=session.record.request,
                    visible_artifacts=self._seneschal_debate_refs(session, phase),
                )

                def apply_register(
                    current: OfflineSession,
                    output: ClaimRegister,
                    snapshot_round: int = snapshot_round,
                    previous_snapshot: ClaimRegisterSnapshot | None = previous_snapshot,
                ) -> OfflineSession:
                    if output.phase is not phase:
                        raise ValueError("provider claim register must match the active phase")
                    accepted = ClaimRegisterSnapshot(
                        phase=phase,
                        round_number=snapshot_round,
                        claim_register=output,
                        supersedes_register_id=(
                            previous_snapshot.claim_register.register_id
                            if previous_snapshot is not None
                            else None
                        ),
                    )
                    trace = _update_trace(
                        current.protocol_trace,
                        claim_register_snapshots=_append_unique(
                            current.protocol_trace.claim_register_snapshots,
                            accepted,
                            identity=lambda item: f"{item.phase.value}:{item.round_number}",
                        ),
                    )
                    return _replace_session(current, protocol_trace=trace)

                session, _ = await self._call(
                    session,
                    expected=template.claim_register,
                    resulting_stage=resulting_stage,
                    procedural_role="seneschal",
                    prompt_path=contract.prompt_template or "",
                    context=context,
                    apply=apply_register,
                    output_dir=output_dir,
                    phase=phase,
                    round_number=round_number,
                    subject="claims",
                    interrupt_after=interrupt_after,
                )
                snapshot = self._snapshot(session, phase, snapshot_round)
                if snapshot is None:
                    raise ProviderError("accepted claim register was not committed")
            claims = snapshot.claim_register
            previous_claims = (
                previous_snapshot.claim_register if previous_snapshot is not None else None
            )
            new_input_claim_ids = self._claims_with_new_input(previous_claims, claims)

            plan_context = ContextBuilder.seneschal_stage(
                stage=session.record.stage,
                request=session.record.request,
                visible_artifacts=self._seneschal_debate_refs(session, phase),
            )

            def apply_plan(current: OfflineSession, output: ChallengePlan) -> OfflineSession:
                if output.phase is not phase or output.round_number != round_number:
                    raise ValueError("provider challenge plan must match active phase and round")
                trace = _update_trace(
                    current.protocol_trace,
                    challenge_plans=_append_unique(
                        current.protocol_trace.challenge_plans,
                        output,
                        identity=lambda item: f"{item.phase.value}:{item.round_number}",
                    ),
                )
                return _replace_session(current, protocol_trace=trace)

            plan_exemplar = template.plan if round_number <= len(rounds) else prior_plans[-1]
            session, plan = await self._call(
                session,
                expected=plan_exemplar,
                resulting_stage=resulting_stage,
                procedural_role="seneschal",
                prompt_path=contract.prompt_template or "",
                context=plan_context,
                apply=apply_plan,
                output_dir=output_dir,
                phase=phase,
                round_number=round_number,
                subject="plan",
                interrupt_after=interrupt_after,
            )
            validate_challenge_plan(
                plan,
                claims=claims,
                council=session.runtime.council,
                policy=policy,
                prior_plans=tuple(prior_plans),
                claims_with_new_input=new_input_claim_ids,
            )

            round_challenges: list[ChallengeArtifact] = []
            round_responses: list[ChallengeResponse] = []
            for assignment in plan.assignments:
                source = _source_reference(session, assignment.target_artifact_id)
                claim_ref = _reference(claims, ArtifactKind.CLAIM_REGISTER)
                plan_ref = _reference(plan, ArtifactKind.CHALLENGE_PLAN)
                turn = contract.challenge_turns[0]
                _validate_visible(
                    label=turn.turn_id,
                    allowed=turn.allowed_input_artifacts,
                    supplied=(
                        ArtifactKind.CLAIM_REGISTER,
                        ArtifactKind.CHALLENGE_PLAN,
                        ArtifactKind(source.artifact_type),
                    ),
                )
                challenge_context = ContextBuilder.member_stage(
                    stage=session.record.stage,
                    request=session.record.request,
                    member=_profile(session, assignment.challenger_member_id),
                    visible_artifacts=(claim_ref, plan_ref, source),
                )

                def apply_challenge(
                    current: OfflineSession,
                    output: ChallengeArtifact,
                ) -> OfflineSession:
                    validate_challenge_artifact(output, assignment=assignment)
                    trace = _update_trace(
                        current.protocol_trace,
                        challenges=_append_unique(
                            current.protocol_trace.challenges,
                            output,
                            identity=lambda item: item.challenge_id,
                        ),
                    )
                    link = LineageLink(
                        source_artifact_id=output.target_claim_id,
                        target_artifact_id=output.challenge_id,
                        relationship="challenged_by",
                    )
                    return _replace_session(
                        current,
                        protocol_trace=trace,
                        lineage=_append_unique(
                            current.lineage,
                            link,
                            identity=lambda item: (
                                f"{item.source_artifact_id}:{item.target_artifact_id}:"
                                f"{item.relationship}"
                            ),
                        ),
                    )

                session, challenge = await self._call(
                    session,
                    expected=self._challenge_exemplar(rounds, assignment),
                    resulting_stage=resulting_stage,
                    procedural_role="challenger",
                    prompt_path=turn.prompt_template,
                    context=challenge_context,
                    apply=apply_challenge,
                    output_dir=output_dir,
                    member_id=assignment.challenger_member_id,
                    phase=phase,
                    round_number=round_number,
                    subject=assignment.challenge_id,
                    interrupt_after=interrupt_after,
                )
                validate_challenge_artifact(challenge, assignment=assignment)
                round_challenges.append(challenge)

                response_turn = contract.challenge_turns[1]
                challenge_ref = _reference(challenge, ArtifactKind.CHALLENGE)
                _validate_visible(
                    label=response_turn.turn_id,
                    allowed=response_turn.allowed_input_artifacts,
                    supplied=(
                        ArtifactKind.CHALLENGE_PLAN,
                        ArtifactKind.CHALLENGE,
                        ArtifactKind(source.artifact_type),
                    ),
                )
                response_context = ContextBuilder.member_stage(
                    stage=session.record.stage,
                    request=session.record.request,
                    member=_profile(session, assignment.target_member_id),
                    visible_artifacts=(plan_ref, challenge_ref, source),
                )

                def apply_response(
                    current: OfflineSession,
                    output: ChallengeResponse,
                ) -> OfflineSession:
                    validate_challenge_response(output, assignment=assignment)
                    responses = _append_unique(
                        current.record.challenge_responses,
                        output,
                        identity=lambda item: item.challenge_id,
                    )
                    requests = current.record.evidence_requests
                    if output.evidence_request is not None:
                        requests = _append_unique(
                            requests,
                            output.evidence_request,
                            identity=lambda item: item.evidence_request_id,
                        )
                    record = _update_record(
                        current.record,
                        challenge_responses=responses,
                        evidence_requests=requests,
                    )
                    links = list(current.lineage)
                    links.append(
                        LineageLink(
                            source_artifact_id=output.challenge_id,
                            target_artifact_id=f"{output.challenge_id}:response",
                            relationship="answered_by",
                        )
                    )
                    if output.evidence_request is not None:
                        links.append(
                            LineageLink(
                                source_artifact_id=f"{output.challenge_id}:response",
                                target_artifact_id=output.evidence_request.evidence_request_id,
                                relationship="requested_evidence",
                            )
                        )
                    unique_links: list[LineageLink] = []
                    seen: set[str] = set()
                    for link in links:
                        identity = (
                            f"{link.source_artifact_id}:{link.target_artifact_id}:"
                            f"{link.relationship}"
                        )
                        if identity not in seen:
                            seen.add(identity)
                            unique_links.append(link)
                    return _replace_session(
                        current,
                        record=record,
                        lineage=tuple(unique_links),
                    )

                session, response = await self._call(
                    session,
                    expected=self._response_exemplar(rounds, assignment),
                    resulting_stage=resulting_stage,
                    procedural_role="target",
                    prompt_path=response_turn.prompt_template,
                    context=response_context,
                    apply=apply_response,
                    output_dir=output_dir,
                    member_id=assignment.target_member_id,
                    phase=phase,
                    round_number=round_number,
                    subject=assignment.challenge_id,
                    interrupt_after=interrupt_after,
                )
                validate_challenge_response(response, assignment=assignment)
                round_responses.append(response)

            validate_challenge_round_outputs(
                plan,
                challenges=tuple(round_challenges),
                responses=tuple(round_responses),
            )

            continuation_context = ContextBuilder.seneschal_stage(
                stage=session.record.stage,
                request=session.record.request,
                visible_artifacts=self._seneschal_debate_refs(session, phase),
            )

            def apply_continuation(
                current: OfflineSession,
                output: ContinuationDecision,
            ) -> OfflineSession:
                if output.phase is not phase or output.completed_round != round_number:
                    raise ValueError(
                        "provider continuation decision must match active phase and round"
                    )
                trace = _update_trace(
                    current.protocol_trace,
                    continuation_decisions=_append_unique(
                        current.protocol_trace.continuation_decisions,
                        output,
                        identity=lambda item: f"{item.phase.value}:{item.completed_round}",
                    ),
                )
                return _replace_session(current, protocol_trace=trace)

            continuation_exemplar = (
                template.continuation
                if round_number <= len(rounds)
                else session.protocol_trace.continuation_decisions[-1]
            )
            session, continuation = await self._call(
                session,
                expected=continuation_exemplar,
                resulting_stage=resulting_stage,
                procedural_role="seneschal",
                prompt_path=contract.prompt_template or "",
                context=continuation_context,
                apply=apply_continuation,
                output_dir=output_dir,
                phase=phase,
                round_number=round_number,
                subject="continuation",
                interrupt_after=interrupt_after,
            )
            validate_continuation_decision(
                continuation,
                claims=claims,
                policy=policy,
            )

            produced = []
            if phase is ChallengePhase.PROPOSAL or snapshot_round > 0:
                produced.append(ArtifactKind.CLAIM_REGISTER)
            produced.extend(
                [
                    ArtifactKind.CHALLENGE_PLAN,
                    *(ArtifactKind.CHALLENGE for _ in round_challenges),
                    *(ArtifactKind.CHALLENGE_RESPONSE for _ in round_responses),
                    ArtifactKind.CONTINUATION_DECISION,
                ]
            )
            validate_stage_outputs(contract, tuple(produced))
            prior_plans.append(plan)

            if not continuation.continue_debate:
                break
        else:
            raise ProviderError("challenge phase exhausted its bounded rounds without stopping")

        return self._advance(session, resulting_stage, output_dir)

    def _seneschal_debate_refs(
        self,
        session: OfflineSession,
        phase: ChallengePhase,
    ) -> tuple:
        refs = list(super()._seneschal_debate_refs(session, phase))
        challenge_phase = {
            item.challenge_id: item.phase for item in session.protocol_trace.challenges
        }
        existing = {item.artifact_id for item in refs}
        for response in session.record.challenge_responses:
            if challenge_phase.get(response.challenge_id) is phase:
                reference = _reference(response, ArtifactKind.CHALLENGE_RESPONSE)
                if reference.artifact_id not in existing:
                    refs.append(reference)
                    existing.add(reference.artifact_id)
        return tuple(refs)

    def _phase_requests(
        self,
        session: OfflineSession,
        phase: ChallengePhase,
    ) -> tuple:
        phase_by_challenge = {
            item.challenge_id: item.phase for item in session.protocol_trace.challenges
        }
        return tuple(
            response.evidence_request
            for response in session.record.challenge_responses
            if response.evidence_request is not None
            and phase_by_challenge.get(response.challenge_id) is phase
        )

    def _resolve_evidence(
        self,
        session: OfflineSession,
        *,
        phase: ChallengePhase,
        resolutions: tuple[EvidenceResolution, ...],
        output_dir: str | Path,
    ) -> OfflineSession:
        """Resolve only accepted provider-generated request IDs through explicit input."""

        del resolutions
        resulting_stage = (
            DeliberationStage.EVIDENCE_RESOLVED
            if phase is ChallengePhase.FRAME
            else DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED
        )
        contract = session.runtime.protocol.contract_for(resulting_stage)
        requests = self._phase_requests(session, phase)
        missing = tuple(
            request.evidence_request_id
            for request in requests
            if request.evidence_request_id not in self._session_evidence_resolutions
        )
        if missing:
            raise MissingEvidenceDisposition(
                "provider-generated evidence requests require explicit matching dispositions: "
                f"{sorted(missing)}"
            )
        accepted_resolutions = tuple(
            self._session_evidence_resolutions[request.evidence_request_id]
            for request in requests
        )
        validate_evidence_resolutions(requests, accepted_resolutions)
        validate_stage_inputs(
            contract,
            tuple(ArtifactKind.EVIDENCE_REQUEST for _ in requests),
        )
        validate_stage_outputs(
            contract,
            tuple(ArtifactKind.EVIDENCE_RESOLUTION for _ in accepted_resolutions),
            supplied_input_artifacts=tuple(
                ArtifactKind.EVIDENCE_REQUEST for _ in requests
            ),
        )

        current = {
            resolution.evidence_request_id: resolution
            for resolution in session.record.evidence_resolutions
        }
        history = list(session.evidence_history)
        links = list(session.lineage)
        for resolution in accepted_resolutions:
            previous = current.get(resolution.evidence_request_id)
            current[resolution.evidence_request_id] = resolution
            history.append(
                EvidenceDispositionEvent(
                    evidence_request_id=resolution.evidence_request_id,
                    outcome=resolution.outcome,
                    replaced_outcome=previous.outcome if previous else None,
                    note=(
                        "Replaced prior evidence disposition during explicit resume."
                        if previous
                        else "Recorded evidence disposition for the current stage."
                    ),
                )
            )
            links.append(
                LineageLink(
                    source_artifact_id=resolution.evidence_request_id,
                    target_artifact_id=f"{resolution.evidence_request_id}:resolution",
                    relationship="resolved_as",
                )
            )

        ordered_resolutions = tuple(
            current[request.evidence_request_id]
            for request in session.record.evidence_requests
            if request.evidence_request_id in current
        )
        stage_status = evidence_session_status(accepted_resolutions)
        record = _update_record(
            session.record,
            evidence_resolutions=ordered_resolutions,
            status=stage_status,
        )
        session = _replace_session(
            session,
            record=record,
            evidence_history=tuple(history),
            lineage=tuple(links),
            checkpoint_sequence=session.checkpoint_sequence + 1,
        )
        write_checkpoint(session, output_dir)
        if stage_status is not SessionStatus.ACTIVE:
            write_review_artifacts(session, output_dir)
            return session
        return self._advance(session, resulting_stage, output_dir)

    def _strategy_refs(self, session: OfflineSession) -> tuple:
        refs = list(super()._strategy_refs(session))
        challenge_phase = {
            item.challenge_id: item.phase for item in session.protocol_trace.challenges
        }
        existing = {item.artifact_id for item in refs}
        for response in session.record.challenge_responses:
            if challenge_phase.get(response.challenge_id) is ChallengePhase.FRAME:
                reference = _reference(response, ArtifactKind.CHALLENGE_RESPONSE)
                if reference.artifact_id not in existing:
                    refs.append(reference)
                    existing.add(reference.artifact_id)
        return tuple(
            item
            for item in refs
            if not (
                item.artifact_type == ArtifactKind.CHALLENGE_RESPONSE.value
                and challenge_phase.get(item.artifact_id.removesuffix(":response"))
                is not ChallengePhase.FRAME
            )
        )

    def _revision_refs(self, session: OfflineSession) -> tuple:
        refs = list(super()._revision_refs(session))
        challenge_phase = {
            item.challenge_id: item.phase for item in session.protocol_trace.challenges
        }
        existing = {item.artifact_id for item in refs}
        for response in session.record.challenge_responses:
            if challenge_phase.get(response.challenge_id) is ChallengePhase.PROPOSAL:
                reference = _reference(response, ArtifactKind.CHALLENGE_RESPONSE)
                if reference.artifact_id not in existing:
                    refs.append(reference)
                    existing.add(reference.artifact_id)
        return tuple(
            item
            for item in refs
            if not (
                item.artifact_type == ArtifactKind.CHALLENGE_RESPONSE.value
                and challenge_phase.get(item.artifact_id.removesuffix(":response"))
                is not ChallengePhase.PROPOSAL
            )
        )
