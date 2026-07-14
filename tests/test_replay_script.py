"""Gate 2 regression tests for extracting replay control from orchestration."""

from __future__ import annotations

from pathlib import Path

import pytest

from imperium.offline.engine import OfflineDeliberationEngine
from imperium.offline.fixtures import build_challenged_scenario, build_no_challenge_scenario
from imperium.offline.replay_script import build_replay_records
from imperium.providers.replay import ReplayProvider

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scenario_factory",
    (build_challenged_scenario, build_no_challenge_scenario),
)
async def test_extracted_replay_script_matches_completed_engine_calls(
    tmp_path: Path,
    scenario_factory,
) -> None:
    scenario = scenario_factory()
    records = build_replay_records(scenario)
    session = await OfflineDeliberationEngine().run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / scenario.scenario_id,
    )

    assert tuple(records) == session.completed_call_keys
    assert len(records) == len(set(records))


def test_challenged_replay_script_contains_all_36_provider_turns() -> None:
    records = build_replay_records(build_challenged_scenario(), model="fixture-model")

    assert len(records) == 36
    assert (
        "interpretations_complete:advocate:steward:Interpretation" in records
    )
    assert (
        "proposal_challenges_complete:challenger:steward:proposal:r1:"
        "proposal-scope-r1:ChallengeArtifact"
    ) in records
    assert "plan_complete:seneschal:ActionablePlan" in records
    assert all(entry[0]["provider"] == "stage4-replay" for entry in records.values())
    assert all(entry[0]["model"] == "fixture-model" for entry in records.values())


def test_extracted_records_are_consumable_by_replay_provider() -> None:
    records = build_replay_records(build_no_challenge_scenario())
    provider = ReplayProvider(records)

    assert provider.calls == []
    assert len(records) > 0
