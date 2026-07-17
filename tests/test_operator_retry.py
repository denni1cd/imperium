"""Gate 2E.2 operator disposition and configured-attempt authorization tests."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from imperium.domain.enums import DeliberationStage, SessionStatus
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


class FailingProvider:
    def __init__(self) -> None:
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
        del model, instructions, input_text, output_type
        self.calls.append(metadata)
        raise ProviderError("simulated provider failure")


class SimulatedCrash(BaseException):
    pass


class CrashingProvider(FailingProvider):
    async def generate(self, **kwargs):
        self.calls.append(kwargs["metadata"])
        raise SimulatedCrash


async def _failed_checkpoint(
    tmp_path: Path,
    *,
    budget: UsageBudget | None = None,
) -> Path:
    provider = FailingProvider()
    with pytest.raises(ProviderError, match="simulated provider failure"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-replay",
            usage_budget=budget,
        ).run(
            build_challenged_scenario(),
            project_root=ROOT,
            output_dir=tmp_path,
        )
    assert len(provider.calls) == 1
    return tmp_path / "session.json"


@pytest.mark.asyncio
async def test_operator_can_abandon_without_launching_replacement(tmp_path: Path) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)
    engine = ProviderBoundDeliberationEngine(model="gate2e-replay")

    abandoned = engine.abandon_attempt(
        checkpoint,
        reason="The operator accepts the missing interpretation.",
    )

    assert len(abandoned.attempts) == 1
    assert abandoned.attempts[0].status is AttemptStatus.ABANDONED
    assert (
        abandoned.attempts[0].disposition_reason
        == "The operator accepts the missing interpretation."
    )
    assert abandoned.pending_call_key is None

    with pytest.raises(ValueError, match="exactly one unresolved"):
        await engine.retry_attempt(
            checkpoint,
            reason="An abandoned attempt cannot be revived.",
        )


@pytest.mark.asyncio
async def test_abandoning_crash_pending_attempt_makes_session_terminal(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    with pytest.raises(SimulatedCrash):
        await ProviderBoundDeliberationEngine(
            provider=CrashingProvider(),
            model="gate2e-replay",
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    abandoned = ProviderBoundDeliberationEngine(
        model="gate2e-replay"
    ).abandon_attempt(
        tmp_path / "session.json",
        reason="The operator will proceed without replacing the uncertain call.",
    )

    assert abandoned.status is SessionStatus.FAILED
    assert abandoned.attempts[0].status is AttemptStatus.ABANDONED
    assert abandoned.pending_call_key is None
    assert abandoned.failure_reason is not None
    assert abandoned.failure_reason.startswith("AttemptAbandoned:")


@pytest.mark.asyncio
async def test_operator_authorizes_exactly_one_replacement_with_lineage(
    tmp_path: Path,
) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)
    engine = ProviderBoundDeliberationEngine(model="gate2e-replay")

    with pytest.raises(OfflineInterrupted):
        await engine.retry_attempt(
            checkpoint,
            reason="The transient provider failure is understood and one replacement is approved.",
            interrupt_after=_first_call_key(),
        )

    resumed = load_session(checkpoint)
    assert len(resumed.attempts) == 2
    original, replacement = resumed.attempts
    assert original.status is AttemptStatus.RETRIED
    assert replacement.status is AttemptStatus.ACCEPTED
    assert original.superseded_by_attempt_id == replacement.attempt_id
    assert replacement.retry_of_attempt_id == original.attempt_id
    assert original.disposition_reason is not None
    assert replacement.attempt_number == 2
    assert resumed.completed_call_keys == (_first_call_key(),)


@pytest.mark.asyncio
async def test_plain_resume_cannot_replace_failed_attempt(tmp_path: Path) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)
    provider = FailingProvider()

    returned = await ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2e-replay",
    ).resume(checkpoint)

    assert provider.calls == []
    assert len(returned.attempts) == 1
    assert returned.attempts[0].status is AttemptStatus.FAILED
    failed = load_session(checkpoint)
    assert failed == returned


@pytest.mark.asyncio
async def test_default_per_call_limit_rejects_third_attempt(tmp_path: Path) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)
    replacement_provider = FailingProvider()

    with pytest.raises(ProviderError, match="simulated provider failure"):
        await ProviderBoundDeliberationEngine(
            provider=replacement_provider,
            model="gate2e-replay",
        ).retry_attempt(
            checkpoint,
            reason="Approve the sole replacement after a diagnosed transient failure.",
        )

    failed = load_session(checkpoint)
    assert [attempt.status for attempt in failed.attempts] == [
        AttemptStatus.RETRIED,
        AttemptStatus.FAILED,
    ]
    assert len(replacement_provider.calls) == 1

    with pytest.raises(
        RetryAuthorizationRequired,
        match="configured per-call attempt limit is exhausted",
    ):
        await ProviderBoundDeliberationEngine(model="gate2e-replay").retry_attempt(
            checkpoint,
            reason="The default configuration permits only two attempts.",
        )


@pytest.mark.asyncio
async def test_failed_replacement_can_be_abandoned_without_another_call(
    tmp_path: Path,
) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)
    provider = FailingProvider()
    with pytest.raises(ProviderError, match="simulated provider failure"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-replay",
        ).retry_attempt(
            checkpoint,
            reason="Authorize one replacement after the diagnosed failure.",
        )

    abandoned = ProviderBoundDeliberationEngine(
        model="gate2e-replay"
    ).abandon_attempt(
        checkpoint,
        reason="The replacement also failed; stop this call without another launch.",
    )

    assert len(provider.calls) == 1
    assert [attempt.status for attempt in abandoned.attempts] == [
        AttemptStatus.RETRIED,
        AttemptStatus.ABANDONED,
    ]
    assert abandoned.attempts[-1].attempt_number == 2


@pytest.mark.asyncio
async def test_configured_per_call_limit_allows_three_attempts(
    tmp_path: Path,
) -> None:
    budget = UsageBudget(max_attempts_per_call=3)
    checkpoint = await _failed_checkpoint(tmp_path, budget=budget)

    for replacement_number in (2, 3):
        provider = FailingProvider()
        with pytest.raises(ProviderError, match="simulated provider failure"):
            await ProviderBoundDeliberationEngine(
                provider=provider,
                model="gate2e-replay",
                usage_budget=budget,
            ).retry_attempt(
                checkpoint,
                reason=f"Authorize configured attempt {replacement_number}.",
            )
        assert len(provider.calls) == 1

    failed = load_session(checkpoint)
    assert [attempt.status for attempt in failed.attempts] == [
        AttemptStatus.RETRIED,
        AttemptStatus.RETRIED,
        AttemptStatus.FAILED,
    ]
    assert failed.usage_budget.max_attempts_per_call == 3

    blocked = FailingProvider()
    with pytest.raises(
        RetryAuthorizationRequired,
        match="configured per-call attempt limit is exhausted",
    ):
        await ProviderBoundDeliberationEngine(
            provider=blocked,
            model="gate2e-replay",
            usage_budget=budget,
        ).retry_attempt(
            checkpoint,
            reason="Attempt four exceeds the persisted per-call limit.",
        )
    assert blocked.calls == []


@pytest.mark.asyncio
async def test_replacement_cannot_change_model_identity(tmp_path: Path) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)
    provider = FailingProvider()

    with pytest.raises(ValueError, match="preserve the original model identity"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="different-model",
        ).retry_attempt(
            checkpoint,
            reason="Model substitution is not part of retry authorization.",
        )

    assert provider.calls == []
    unchanged = load_session(checkpoint)
    assert len(unchanged.attempts) == 1
    assert unchanged.attempts[0].status is AttemptStatus.FAILED


@pytest.mark.asyncio
async def test_retry_requires_non_empty_reason(tmp_path: Path) -> None:
    checkpoint = await _failed_checkpoint(tmp_path)

    with pytest.raises(ValueError, match="non-empty reason"):
        await ProviderBoundDeliberationEngine(model="gate2e-replay").retry_attempt(
            checkpoint,
            reason="   ",
        )


@pytest.mark.asyncio
async def test_pending_crash_consumes_output_reserve_before_replacement(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    provider = CrashingProvider()
    reserve = 4_096
    budget = UsageBudget(
        max_output_tokens=reserve,
        output_token_reserve_per_attempt=reserve,
    )

    with pytest.raises(SimulatedCrash):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-replay",
            usage_budget=budget,
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    checkpoint = tmp_path / "session.json"
    replacement = FailingProvider()
    with pytest.raises(UsageBudgetExceeded, match="output token budget"):
        await ProviderBoundDeliberationEngine(
            provider=replacement,
            model="gate2e-replay",
            usage_budget=budget,
        ).retry_attempt(
            checkpoint,
            reason="The crashed call is uncertain, so its reserve must remain charged.",
        )

    assert replacement.calls == []
    preserved = load_session(checkpoint)
    assert len(preserved.attempts) == 1
    assert preserved.attempts[0].status is AttemptStatus.PENDING


@pytest.mark.asyncio
async def test_pending_retry_post_return_charges_original_output_reserve(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    reserve = 4_096
    budget = UsageBudget(
        max_output_tokens=9_000,
        output_token_reserve_per_attempt=reserve,
    )
    with pytest.raises(SimulatedCrash):
        await ProviderBoundDeliberationEngine(
            provider=CrashingProvider(),
            model="gate2e-replay",
            usage_budget=budget,
        ).run(scenario, project_root=ROOT, output_dir=tmp_path)

    records = build_replay_records(scenario, model="gate2e-replay")
    records[_first_call_key()][0]["output_tokens"] = 6_000
    provider = ReplayProvider(records)

    with pytest.raises(UsageBudgetExceeded, match="reported output token budget"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2e-replay",
            usage_budget=budget,
        ).retry_attempt(
            tmp_path / "session.json",
            reason="Retry the uncertain call while retaining its conservative reserve.",
        )

    assert len(provider.calls) == 1
    failed = load_session(tmp_path / "session.json")
    assert [attempt.status for attempt in failed.attempts] == [
        AttemptStatus.RETRIED,
        AttemptStatus.FAILED,
    ]
    assert failed.attempts[-1].output_tokens == 6_000

