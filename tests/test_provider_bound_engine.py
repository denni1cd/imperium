"""Gate 2 tests for session-level provider injection."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import DeliberationRecord
from imperium.offline.engine import OfflineDeliberationEngine
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.provider_engine import ProviderBoundDeliberationEngine
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import CallMetadata, ModelResult, ProviderError
from imperium.providers.replay import ReplayProvider

ROOT = Path(__file__).resolve().parents[1]
OutputT = TypeVar("OutputT", bound=BaseModel)


def _deterministic_record(record: DeliberationRecord) -> dict[str, object]:
    payload = record.model_dump(mode="json")
    for call in payload["model_calls"]:
        call.pop("created_at", None)
    return payload


class RecordingProvider:
    """Delegate to replay while proving one injected instance handles every turn."""

    def __init__(self, replay: ReplayProvider) -> None:
        self.replay = replay
        self.calls: list[CallMetadata] = []

    async def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        output_type: type[OutputT],
        metadata: CallMetadata,
    ) -> ModelResult[OutputT]:
        self.calls.append(metadata)
        result = await self.replay.generate(
            model=model,
            instructions=instructions,
            input_text=input_text,
            output_type=output_type,
            metadata=metadata,
        )
        return ModelResult[OutputT](
            output=result.output,
            provider="gate2-injected-replay",
            model=result.model,
            response_id=result.response_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )


class FailingIfCalledProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, **kwargs):
        del kwargs
        self.calls += 1
        raise AssertionError("provider must not run after context preflight fails")


@pytest.mark.asyncio
async def test_default_replay_provider_preserves_complete_stage4_result(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    baseline = await OfflineDeliberationEngine(model="gate2-default-replay").run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "baseline",
    )
    engine = ProviderBoundDeliberationEngine(model="gate2-default-replay")
    session = await engine.run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "provider-bound",
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert isinstance(engine.session_provider, ReplayProvider)
    assert len(engine.session_provider.calls) == 36
    assert tuple(call.call_key for call in engine.session_provider.calls) == (
        session.completed_call_keys
    )
    assert _deterministic_record(session.record) == _deterministic_record(
        baseline.record
    )
    assert session.protocol_trace == baseline.protocol_trace
    assert session.lifecycle_history == baseline.lifecycle_history
    assert session.completed_call_keys == baseline.completed_call_keys
    assert session.evidence_history == baseline.evidence_history
    assert session.lineage == baseline.lineage
    assert session.turns == baseline.turns


@pytest.mark.asyncio
async def test_one_injected_provider_handles_all_turns_without_output_drift(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    provider = RecordingProvider(
        ReplayProvider(build_replay_records(scenario, model="gate2-simulated"))
    )
    engine = ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-simulated",
    )

    session = await engine.run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "injected",
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert engine.session_provider is provider
    assert len(provider.calls) == 36
    assert tuple(call.call_key for call in provider.calls) == session.completed_call_keys
    assert {call.provider for call in session.record.model_calls} == {
        "gate2-injected-replay"
    }
    assert session.record.plan == scenario.plan
    assert session.record.adjudication == scenario.adjudication


@pytest.mark.asyncio
async def test_context_ceiling_fails_before_provider_invocation(tmp_path: Path) -> None:
    provider = FailingIfCalledProvider()
    engine = ProviderBoundDeliberationEngine(
        provider=provider,
        max_context_bytes=1,
    )

    with pytest.raises(ProviderError, match="context for .* limit is 1 bytes"):
        await engine.run(
            build_challenged_scenario(),
            project_root=ROOT,
            output_dir=tmp_path / "bounded",
        )

    assert provider.calls == 0
