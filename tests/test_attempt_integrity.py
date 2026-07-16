"""Adversarial Gate 2E tests for conservative budgets and checkpoint integrity."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel, ValidationError

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import Interpretation
from imperium.offline.attempts import (
    AttemptStatus,
    RetryAuthorizationRequired,
    UsageBudget,
    UsageBudgetExceeded,
)
from imperium.offline.engine import OfflineInterrupted, _call_key
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.persistence import load_session
from imperium.offline.provider_engine import ProviderBoundDeliberationEngine
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import CallMetadata, ModelResult, ProviderError
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


class ZeroUsageReplayProvider:
    """Replay valid outputs while intentionally omitting all usage metadata."""

    def __init__(self, scenario) -> None:
        self.replay = ReplayProvider(build_replay_records(scenario, model="gate2e-zero-usage"))
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
        replayed = await self.replay.generate(
            model=model,
            instructions=instructions,
            input_text=input_text,
            output_type=output_type,
            metadata=metadata,
        )
        return ModelResult[OutputT](
            output=replayed.output,
            provider="gate2e-zero-usage",
            model=model,
            input_tokens=0,
            cached_input_tokens=0,
            output_tokens=0,
            latency_ms=1,
            retries=0,
        )


class SimulatedProviderCrash(BaseException):
    """Represent process loss after the pending checkpoint but before a result."""


class CrashingReplayProvider(ZeroUsageReplayProvider):
    """Terminate outside normal provider error handling after launch."""

    async def generate(self, **kwargs):
        self.calls.append(kwargs["metadata"])
        raise SimulatedProviderCrash


class TighteningReplayProvider(ZeroUsageReplayProvider):
    """Make the next context exceed the ceiling after one accepted call."""

    engine: ProviderBoundDeliberationEngine | None = None

    async def generate(self, **kwargs):
        result = await super().generate(**kwargs)
        if len(self.calls) == 1:
            assert self.engine is not None
            self.engine.max_context_bytes = 1
        return result


@pytest.mark.asyncio
async def test_resume_preserves_pending_attempt_when_retry_authorization_is_required(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    provider = CrashingReplayProvider(scenario)

    with pytest.raises(SimulatedProviderCrash):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-crash",
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    checkpoint = tmp_path / "session.json"
    crashed = load_session(checkpoint)
    assert crashed.pending_call_key == _first_call_key()
    assert crashed.attempts[0].status is AttemptStatus.PENDING

    with pytest.raises(RetryAuthorizationRequired):
        await ProviderBoundDeliberationEngine(model="gate2e-replay").resume(checkpoint)

    failed = load_session(checkpoint)
    assert failed.pending_call_key == _first_call_key()
    assert failed.attempts[0].status is AttemptStatus.PENDING
    assert failed.failure_reason is not None
    assert failed.failure_reason.startswith("RetryAuthorizationRequired:")


@pytest.mark.asyncio
async def test_missing_input_usage_is_charged_from_persisted_estimate(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    probe_provider = ZeroUsageReplayProvider(scenario)
    probe_dir = tmp_path / "probe"
    with pytest.raises(OfflineInterrupted):
        await ProviderBoundDeliberationEngine(
            provider=probe_provider,
            model="gate2e-zero-usage",
        ).run(
            scenario,
            project_root=ROOT,
            output_dir=probe_dir,
            interrupt_after=_first_call_key(),
        )
    first_estimate = load_session(probe_dir / "session.json").attempts[0].estimated_input_tokens

    provider = ZeroUsageReplayProvider(scenario)
    output = tmp_path / "bounded"
    with pytest.raises(UsageBudgetExceeded, match="input token budget"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-zero-usage",
            usage_budget=UsageBudget(max_input_tokens=first_estimate + 1),
        ).run(scenario, project_root=ROOT, output_dir=output)

    failed = load_session(output / "session.json")
    assert len(provider.calls) == 1
    assert len(failed.attempts) == 1
    assert failed.attempts[0].input_tokens == 0
    assert failed.attempts[0].estimated_input_tokens == first_estimate


@pytest.mark.asyncio
async def test_missing_output_usage_consumes_reserved_budget(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = ZeroUsageReplayProvider(scenario)
    reserve = 4_096
    output = tmp_path / "output-reserve"

    with pytest.raises(UsageBudgetExceeded, match="output token budget"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-zero-usage",
            usage_budget=UsageBudget(
                max_output_tokens=reserve,
                output_token_reserve_per_attempt=reserve,
            ),
        ).run(scenario, project_root=ROOT, output_dir=output)

    failed = load_session(output / "session.json")
    assert len(provider.calls) == 1
    assert len(failed.attempts) == 1
    assert failed.attempts[0].output_tokens == 0


@pytest.mark.asyncio
async def test_later_preflight_failure_preserves_prior_accepted_attempts(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = TighteningReplayProvider(scenario)
    engine = ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2e-zero-usage",
    )
    provider.engine = engine

    with pytest.raises(ProviderError, match="limit is 1 bytes"):
        await engine.run(scenario, project_root=ROOT, output_dir=tmp_path)

    failed = load_session(tmp_path / "session.json")
    assert len(provider.calls) == 1
    assert len(failed.attempts) == 1
    assert failed.attempts[0].call_key == _first_call_key()
    assert failed.completed_call_keys == (_first_call_key(),)


@pytest.mark.asyncio
async def test_checkpoint_rejects_second_attempt_without_retry_lineage(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    with pytest.raises(OfflineInterrupted):
        await ProviderBoundDeliberationEngine(model="gate2e-replay").run(
            scenario,
            project_root=ROOT,
            output_dir=tmp_path,
            interrupt_after=_first_call_key(),
        )

    checkpoint = tmp_path / "session.json"
    payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    forged = dict(payload["attempts"][0])
    forged.update(
        {
            "attempt_id": f"{forged['call_key']}:attempt-2",
            "attempt_number": 2,
            "status": "failed",
            "error_type": "ForgedFailure",
            "error_message": "Injected without an authorized retry lineage.",
            "retry_of_attempt_id": None,
        }
    )
    payload["attempts"].append(forged)
    checkpoint.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError, match="attempts after the first require retry lineage"):
        load_session(checkpoint)


@pytest.mark.asyncio
async def test_checkpoint_binds_attempt_input_digest_to_turn_trace(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    with pytest.raises(OfflineInterrupted):
        await ProviderBoundDeliberationEngine(model="gate2e-replay").run(
            scenario,
            project_root=ROOT,
            output_dir=tmp_path,
            interrupt_after=_first_call_key(),
        )

    checkpoint = tmp_path / "session.json"
    payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    payload["attempts"][0]["input_sha256"] = "0" * 64
    checkpoint.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValidationError, match="attempt input and prompt digests"):
        load_session(checkpoint)
