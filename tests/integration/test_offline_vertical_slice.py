"""End-to-end acceptance tests for the Stage 4 offline deliberation engine."""

from __future__ import annotations

from pathlib import Path

import pytest

from imperium.domain.enums import DeliberationStage, EvidenceOutcome, SessionStatus
from imperium.domain.models import DeliberationRecord, EvidenceResolution
from imperium.offline.engine import OfflineDeliberationEngine, OfflineInterrupted
from imperium.offline.fixtures import (
    build_challenged_scenario,
    build_no_challenge_scenario,
)
from imperium.offline.persistence import load_session


ROOT = Path(__file__).resolve().parents[2]


def _deterministic_record(record: DeliberationRecord) -> dict[str, object]:
    """Remove honest wall-clock metadata while preserving stable call identities and outputs."""

    payload = record.model_dump(mode="json")
    for call in payload["model_calls"]:
        call.pop("created_at", None)
    return payload


@pytest.mark.asyncio
async def test_challenged_session_reaches_actionable_plan(tmp_path: Path) -> None:
    output = tmp_path / "challenged"
    session = await OfflineDeliberationEngine().run(
        build_challenged_scenario(),
        project_root=ROOT,
        output_dir=output,
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert session.record.status is SessionStatus.COMPLETE
    assert len(session.record.interpretations) == 4
    assert len(session.record.proposals) == 4
    assert len(session.record.revisions) == 4
    assert len(session.protocol_trace.challenge_plans) == 3
    assert len(session.protocol_trace.challenges) == 6
    assert len(session.record.challenge_responses) == 6
    assert len(session.protocol_trace.claim_register_snapshots) == 3
    assert session.record.plan is not None
    assert session.record.adjudication is not None
    assert session.record.adjudication.minority_objections
    assert "live-provider interruption safety" in (
        session.record.adjudication.minority_objections[0].objection
    )
    assert any(
        "live providers" in condition
        for condition in session.record.plan.stop_or_reconsideration_conditions
    )

    advocate_turns = [turn for turn in session.turns if turn.member_id is not None]
    assert advocate_turns
    assert all(turn.profile_member_id == turn.member_id for turn in advocate_turns)
    assert {turn.member_id for turn in advocate_turns} == {
        "steward",
        "vanguard",
        "architect",
        "castellan",
    }

    expected_files = {
        "session.json",
        "record.json",
        "protocol_trace.json",
        "manifest.json",
        "lineage.json",
        "transcript.md",
        "plan.json",
    }
    assert expected_files <= {path.name for path in output.iterdir()}
    assert "## Debate" in (output / "transcript.md").read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_empty_challenge_plans_create_no_synthetic_exchanges(tmp_path: Path) -> None:
    session = await OfflineDeliberationEngine().run(
        build_no_challenge_scenario(),
        project_root=ROOT,
        output_dir=tmp_path / "empty",
    )

    assert session.record.status is SessionStatus.COMPLETE
    assert len(session.protocol_trace.challenge_plans) == 2
    assert all(not plan.assignments for plan in session.protocol_trace.challenge_plans)
    assert session.protocol_trace.challenges == ()
    assert session.record.challenge_responses == ()
    assert session.record.evidence_requests == ()
    assert session.record.evidence_resolutions == ()


@pytest.mark.asyncio
async def test_conditional_evidence_path_completes_with_bounds(tmp_path: Path) -> None:
    session = await OfflineDeliberationEngine().run(
        build_challenged_scenario(
            evidence_outcome=EvidenceOutcome.PROCEED_CONDITIONALLY
        ),
        project_root=ROOT,
        output_dir=tmp_path / "conditional",
    )

    assert session.record.status is SessionStatus.COMPLETE
    resolution = session.record.evidence_resolutions[-1]
    assert resolution.outcome is EvidenceOutcome.PROCEED_CONDITIONALLY
    assert resolution.planning_conditions
    assert resolution.remaining_uncertainty


@pytest.mark.asyncio
async def test_waiting_session_resumes_after_explicit_evidence_replacement(
    tmp_path: Path,
) -> None:
    output = tmp_path / "waiting"
    engine = OfflineDeliberationEngine()
    waiting = await engine.run(
        build_challenged_scenario(
            evidence_outcome=EvidenceOutcome.USER_CLARIFICATION_REQUIRED
        ),
        project_root=ROOT,
        output_dir=output,
    )

    assert waiting.record.status is SessionStatus.WAITING_FOR_USER
    assert waiting.record.stage is DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
    assert waiting.record.plan is None

    replacement = EvidenceResolution(
        evidence_request_id="evidence-fixture-coverage",
        outcome=EvidenceOutcome.GATHERED,
        evidence=("The user confirmed every distinct Stage 4 acceptance fixture is required.",),
        source_references=("synthetic:user-confirmation",),
    )
    resumed = await engine.resume(
        output / "session.json",
        evidence_replacements=(replacement,),
    )

    assert resumed.record.status is SessionStatus.COMPLETE
    assert resumed.record.stage is DeliberationStage.PLAN_COMPLETE
    assert resumed.record.evidence_resolutions[-1] == replacement
    events = [
        event
        for event in resumed.evidence_history
        if event.evidence_request_id == replacement.evidence_request_id
    ]
    assert events[-1].replaced_outcome is EvidenceOutcome.USER_CLARIFICATION_REQUIRED


@pytest.mark.asyncio
async def test_paused_session_does_not_advance(tmp_path: Path) -> None:
    session = await OfflineDeliberationEngine().run(
        build_challenged_scenario(
            evidence_outcome=EvidenceOutcome.DELIBERATION_PAUSED
        ),
        project_root=ROOT,
        output_dir=tmp_path / "paused",
    )

    assert session.record.status is SessionStatus.PAUSED
    assert session.record.stage is DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
    assert session.record.revisions == ()
    assert session.record.adjudication is None
    assert session.record.plan is None


@pytest.mark.asyncio
async def test_interrupted_session_resumes_to_same_structured_result(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    engine = OfflineDeliberationEngine()
    uninterrupted = await engine.run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "uninterrupted",
    )
    interrupted_output = tmp_path / "interrupted"
    call_key = (
        "proposal_challenges_complete:challenger:steward:proposal:r1:"
        "proposal-scope-r1:ChallengeArtifact"
    )

    with pytest.raises(OfflineInterrupted) as raised:
        await engine.run(
            scenario,
            project_root=ROOT,
            output_dir=interrupted_output,
            interrupt_after=call_key,
        )

    checkpoint = raised.value.checkpoint
    saved = load_session(checkpoint)
    assert call_key in saved.completed_call_keys
    assert saved.record.stage is DeliberationStage.STRATEGIES_COMPLETE

    resumed = await engine.resume(checkpoint)
    assert _deterministic_record(resumed.record) == _deterministic_record(
        uninterrupted.record
    )
    assert resumed.protocol_trace == uninterrupted.protocol_trace
    assert resumed.lifecycle_history == uninterrupted.lifecycle_history
    assert resumed.completed_call_keys == uninterrupted.completed_call_keys
