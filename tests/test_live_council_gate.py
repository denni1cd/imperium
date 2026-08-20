"""Gate 2F tests use replay only and never launch Codex."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from imperium.domain.enums import DeliberationStage
from imperium.live.capture import (
    capture_completed_session,
    load_capture,
    verify_replay_equivalence,
    write_capture,
)
from imperium.live.gate import (
    LIVE_AUTHORIZATION,
    assess_council_session,
    estimate_council_gate,
    replay_council_capture,
    run_live_council_gate,
)
from imperium.live.gate_case import (
    LIVE_COUNCIL_SCENARIO_ID,
    build_live_council_scenario,
)
from imperium.offline.attempts import UsageBudget
from imperium.offline.fixtures import build_no_challenge_scenario
from imperium.offline.provider_engine import ProviderBoundDeliberationEngine
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import ProviderError
from imperium.providers.codex_cli import DEFAULT_CODEX_MODEL
from imperium.providers.replay import ReplayProvider

ROOT = Path(__file__).resolve().parents[1]


class FailsFirstProvider:
    def __init__(self) -> None:
        self.called = False

    async def generate(self, **kwargs):
        del kwargs
        if not self.called:
            self.called = True
            raise ProviderError("simulated first-attempt failure")
        raise AssertionError("initial provider must not receive an automatic retry")


def _usage_records(scenario) -> dict[str, list[dict[str, object]]]:
    records = build_replay_records(scenario, model=DEFAULT_CODEX_MODEL)
    for index, entries in enumerate(records.values(), start=1):
        entries[0].update(
            {
                "provider": "captured-live-simulation",
                "response_id": f"response-{index}",
                "input_tokens": 100 + index,
                "cached_input_tokens": 10,
                "output_tokens": 20 + index,
                "latency_ms": 1_000 + index,
            }
        )
    return records


def test_gate_case_is_frozen_full_council_condition() -> None:
    scenario = build_live_council_scenario()

    assert scenario.scenario_id == LIVE_COUNCIL_SCENARIO_ID
    assert scenario.request.context["experiment_condition"].startswith("C")
    assert "20-person data engineering group" in scenario.request.original_text
    assert len(scenario.interpretations) == 4
    assert scenario.request.hard_constraints[-1].endswith("implement software.")


@pytest.mark.asyncio
async def test_complete_session_capture_replays_without_codex(tmp_path: Path) -> None:
    scenario = build_live_council_scenario()
    live_provider = ReplayProvider(_usage_records(scenario))
    budget = UsageBudget(max_attempts_per_call=4)
    live = await ProviderBoundDeliberationEngine(
        provider=live_provider,
        model=DEFAULT_CODEX_MODEL,
        usage_budget=budget,
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "simulated-live",
    )
    capture_path = write_capture(
        capture_completed_session(live),
        tmp_path / "accepted-replay.json",
    )

    replay = await replay_council_capture(
        project_root=ROOT,
        capture_path=capture_path,
        output_dir=tmp_path / "replay",
    )

    verify_replay_equivalence(live, replay)
    assert replay.record.stage is DeliberationStage.PLAN_COMPLETE
    assert all(item.cached_input_tokens == 10 for item in replay.attempts)
    assert load_capture(capture_path).calls[0].response_id == "response-1"


@pytest.mark.asyncio
async def test_accepted_replay_equivalence_excludes_retry_audit_history(
    tmp_path: Path,
) -> None:
    scenario = build_live_council_scenario()
    live_dir = tmp_path / "live-with-retry"
    budget = UsageBudget(max_attempts_per_call=3)
    with pytest.raises(ProviderError, match="simulated first-attempt failure"):
        await ProviderBoundDeliberationEngine(
            provider=FailsFirstProvider(),
            model=DEFAULT_CODEX_MODEL,
            usage_budget=budget,
        ).run(
            scenario,
            project_root=ROOT,
            output_dir=live_dir,
        )

    live = await ProviderBoundDeliberationEngine(
        provider=ReplayProvider(build_replay_records(scenario, model=DEFAULT_CODEX_MODEL)),
        model=DEFAULT_CODEX_MODEL,
    ).retry_attempt(
        live_dir / "session.json",
        reason="Retry the simulated transient failure for the capture test.",
        output_dir=live_dir,
    )
    capture_path = write_capture(
        capture_completed_session(live),
        tmp_path / "retry-accepted-replay.json",
    )
    replay = await replay_council_capture(
        project_root=ROOT,
        capture_path=capture_path,
        output_dir=tmp_path / "retry-replay",
    )

    verify_replay_equivalence(live, replay)
    assert len(live.attempts) == len(replay.attempts) + 1


@pytest.mark.asyncio
async def test_gate_assessment_rejects_completion_without_debate(tmp_path: Path) -> None:
    scenario = build_no_challenge_scenario()
    session = await ProviderBoundDeliberationEngine().run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "no-debate",
    )

    assessment = assess_council_session(session)

    assert not assessment.structural_pass
    assert not next(
        check for check in assessment.checks if check.name == "member-authored debate exchange"
    ).passed
    assert assessment.human_review_required


def test_capture_tampering_fails_validation(tmp_path: Path) -> None:
    scenario = build_live_council_scenario()
    capture = {
        "schema_version": "1.0",
        "session_id": "tampered-session",
        "scenario_sha256": "scenario-digest",
        "usage_budget": UsageBudget().model_dump(mode="json"),
        "calls": [
            {
                "call_key": "call",
                "output_artifact_id": "artifact",
                "output_sha256": "typed-digest",
                "payload_sha256": "wrong-payload-digest",
                "provider": "provider",
                "model": "model",
                "input_tokens": 0,
                "cached_input_tokens": 0,
                "output_tokens": 0,
                "latency_ms": 0,
                "output": scenario.interpretations[0].model_dump(mode="json"),
            }
        ],
    }
    path = tmp_path / "tampered.json"
    path.write_text(json.dumps(capture), encoding="utf-8")

    with pytest.raises(ValidationError, match="payload does not match"):
        load_capture(path)


@pytest.mark.asyncio
async def test_estimate_uses_replay_and_respects_configured_attempts(tmp_path: Path) -> None:
    budget = UsageBudget(max_attempts_per_call=5)

    estimate = await estimate_council_gate(
        project_root=ROOT,
        output_dir=tmp_path / "estimate",
        usage_budget=budget,
    )

    assert estimate.expected_path_calls == 36
    assert estimate.protocol_call_ceiling == 59
    assert estimate.estimated_input_tokens > 0
    assert estimate.reserved_output_tokens == 36 * budget.output_token_reserve_per_attempt


@pytest.mark.asyncio
async def test_live_gate_requires_exact_explicit_authorization(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=LIVE_AUTHORIZATION):
        await run_live_council_gate(
            project_root=ROOT,
            output_dir=tmp_path / "must-not-run",
            authorization="yes",
            usage_budget=UsageBudget(),
            executable="definitely-not-a-real-codex-executable",
        )
