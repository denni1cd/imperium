"""Gate 2E tests for durable attempts, usage budgets, and output integrity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from imperium.domain.enums import DeliberationStage, SessionStatus
from imperium.domain.models import Interpretation
from imperium.offline.attempts import (
    AttemptStatus,
    UsageBudget,
    UsageBudgetExceeded,
    usage_totals,
)
from imperium.offline.engine import OfflineInterrupted, _call_key
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.persistence import load_session
from imperium.offline.provider_engine import ProviderBoundDeliberationEngine
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import (
    CallMetadata,
    ModelResult,
    ProviderAmbiguousError,
    ProviderError,
)
from imperium.providers.replay import ReplayProvider

ROOT = Path(__file__).resolve().parents[1]
OutputT = TypeVar("OutputT", bound=BaseModel)


def _first_call_key() -> str:
    return _call_key(
        resulting_stage=DeliberationStage.INTERPRETATIONS_COMPLETE,
        role="advocate",
        output_type=Interpretation,
        member_id="steward",
    )


class CountingReplayProvider:
    def __init__(self, scenario, *, input_tokens: int = 0, cached_input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.replay = ReplayProvider(build_replay_records(scenario, model="gate2e-simulated"))
        self.calls: list[CallMetadata] = []
        self.input_tokens = input_tokens
        self.cached_input_tokens = cached_input_tokens
        self.output_tokens = output_tokens

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
        replayed = await self.replay.generate(
            model=model,
            instructions=instructions,
            input_text=input_text,
            output_type=output_type,
            metadata=metadata,
        )
        return ModelResult[OutputT](
            output=replayed.output,
            provider="gate2e-simulated",
            model=model,
            response_id=f"response-{len(self.calls)}",
            input_tokens=self.input_tokens,
            cached_input_tokens=self.cached_input_tokens,
            output_tokens=self.output_tokens,
            latency_ms=7,
            retries=0,
        )


class PendingInspectingProvider(CountingReplayProvider):
    def __init__(self, scenario, output_dir: Path) -> None:
        super().__init__(scenario)
        self.output_dir = output_dir
        self.pending_seen = False

    async def generate(self, **kwargs):
        checkpoint = load_session(self.output_dir / "session.json")
        assert checkpoint.pending_call_key == kwargs["metadata"].call_key
        pending = checkpoint.attempts[-1]
        assert pending.status is AttemptStatus.PENDING
        assert pending.call_key == checkpoint.pending_call_key
        assert pending.input_sha256
        assert pending.prompt_sha256
        self.pending_seen = True
        return await super().generate(**kwargs)


class DeterministicFailureProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, **kwargs):
        del kwargs
        self.calls += 1
        raise ProviderError("deterministic provider failure")


class AmbiguousFailureProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, **kwargs):
        del kwargs
        self.calls += 1
        raise ProviderAmbiguousError("provider outcome is unknown")


@pytest.mark.asyncio
async def test_complete_replay_persists_one_accepted_attempt_per_turn(tmp_path: Path) -> None:
    session = await ProviderBoundDeliberationEngine(model="gate2e-replay").run(
        build_challenged_scenario(),
        project_root=ROOT,
        output_dir=tmp_path,
    )

    assert session.status is SessionStatus.COMPLETE
    assert len(session.attempts) == 36
    assert all(item.status is AttemptStatus.ACCEPTED for item in session.attempts)
    assert tuple(item.call_key for item in session.attempts) == session.completed_call_keys
    assert usage_totals(session.attempts).attempts_launched == 36
    assert load_session(tmp_path / "session.json").attempts == session.attempts


@pytest.mark.asyncio
async def test_pending_attempt_is_checkpointed_before_provider_invocation(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = PendingInspectingProvider(scenario, tmp_path)

    with pytest.raises(OfflineInterrupted):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-simulated",
        ).run(
            scenario,
            project_root=ROOT,
            output_dir=tmp_path,
            interrupt_after=_first_call_key(),
        )

    assert provider.pending_seen
    accepted = load_session(tmp_path / "session.json").attempts[-1]
    assert accepted.status is AttemptStatus.ACCEPTED
    assert accepted.call_key == _first_call_key()
    assert accepted.output_sha256


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("provider", "expected_status", "message"),
    (
        (DeterministicFailureProvider(), AttemptStatus.FAILED, "deterministic provider failure"),
        (AmbiguousFailureProvider(), AttemptStatus.AMBIGUOUS, "provider outcome is unknown"),
    ),
)
async def test_provider_failures_preserve_terminal_attempt_state(
    tmp_path: Path,
    provider,
    expected_status: AttemptStatus,
    message: str,
) -> None:
    with pytest.raises(ProviderError, match=message):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-simulated",
        ).run(
            build_challenged_scenario(),
            project_root=ROOT,
            output_dir=tmp_path,
        )

    failed = load_session(tmp_path / "session.json")
    assert failed.status is SessionStatus.FAILED
    assert failed.pending_call_key is None
    assert failed.completed_call_keys == ()
    assert len(failed.attempts) == 1
    assert failed.attempts[0].status is expected_status
    assert failed.attempts[0].error_message == message
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_call_budget_stops_before_launching_another_attempt(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = CountingReplayProvider(scenario)
    budget = UsageBudget(max_attempts=1)

    with pytest.raises(UsageBudgetExceeded, match="attempt budget"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-simulated",
            usage_budget=budget,
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    failed = load_session(tmp_path / "session.json")
    assert len(provider.calls) == 1
    assert len(failed.attempts) == 1
    assert failed.attempts[0].status is AttemptStatus.ACCEPTED


@pytest.mark.asyncio
async def test_input_budget_fails_before_provider_invocation(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = CountingReplayProvider(scenario)
    budget = UsageBudget(max_input_tokens=1)

    with pytest.raises(UsageBudgetExceeded, match="estimated input token budget"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-simulated",
            usage_budget=budget,
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    assert provider.calls == []
    assert load_session(tmp_path / "session.json").attempts == ()


@pytest.mark.asyncio
async def test_cached_tokens_are_recorded_on_an_accepted_attempt(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = CountingReplayProvider(
        scenario,
        input_tokens=10,
        cached_input_tokens=4,
        output_tokens=2,
    )

    with pytest.raises(OfflineInterrupted):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-simulated",
        ).run(
            scenario,
            project_root=ROOT,
            output_dir=tmp_path,
            interrupt_after=_first_call_key(),
        )

    attempt = load_session(tmp_path / "session.json").attempts[-1]
    assert attempt.status is AttemptStatus.ACCEPTED
    assert attempt.input_tokens == 10
    assert attempt.cached_input_tokens == 4
    assert attempt.output_tokens == 2


@pytest.mark.asyncio
async def test_reported_usage_breach_is_recorded_without_accepting_output(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = CountingReplayProvider(
        scenario,
        input_tokens=10,
        cached_input_tokens=4,
        output_tokens=2,
    )
    budget = UsageBudget(
        max_cached_input_tokens=3,
        max_output_tokens=100_000,
        output_token_reserve_per_attempt=1,
    )

    with pytest.raises(UsageBudgetExceeded, match="cached input token budget"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-simulated",
            usage_budget=budget,
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    failed = load_session(tmp_path / "session.json")
    attempt = failed.attempts[-1]
    assert attempt.status is AttemptStatus.FAILED
    assert attempt.cached_input_tokens == 4
    assert attempt.output_sha256
    assert failed.completed_call_keys == ()
    assert failed.record.interpretations == ()


@pytest.mark.asyncio
async def test_provider_checkpoint_rejects_tampered_accepted_artifact(tmp_path: Path) -> None:
    await ProviderBoundDeliberationEngine(model="gate2e-replay").run(
        build_challenged_scenario(),
        project_root=ROOT,
        output_dir=tmp_path,
    )
    checkpoint = tmp_path / "session.json"
    payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    payload["record"]["interpretations"][0]["core_decision"] = "Tampered after acceptance."
    checkpoint.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="accepted attempt output digest"):
        load_session(checkpoint)
