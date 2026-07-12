"""Tests for cross-artifact consistency in authoritative session records."""

from decimal import Decimal

import pytest

from imperium.domain.enums import DeliberationStage, SessionStatus
from imperium.domain.models import (
    ActionStep,
    ActionablePlan,
    Challenge,
    DeliberationRecord,
    Interpretation,
)
from imperium.engine.record_validation import (
    InvalidDeliberationRecord,
    validate_deliberation_record,
)


def _interpretation(member_id: str) -> Interpretation:
    return Interpretation(
        member_id=member_id,
        core_decision="Whether to proceed with the project.",
        desired_outcome="A justified, actionable decision.",
        initial_inclination="Run a constrained pilot.",
        value_influence={"economy": "Prefer evidence before major commitment."},
        confidence=Decimal("0.6"),
    )


def _plan() -> ActionablePlan:
    return ActionablePlan(
        decision="Run a constrained pilot.",
        objective="Test strategic value before full commitment.",
        immediate_next_action="Define the pilot success threshold.",
        steps=(
            ActionStep(
                order=1,
                action="Define and run the pilot.",
                completion_signal="Pilot results are recorded.",
            ),
        ),
        stop_or_reconsideration_conditions=("Stop if the success threshold is missed.",),
    )


def test_record_rejects_duplicate_member_snapshots(sovereign_request, member) -> None:
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member, member),
        selected_member_ids=(member.member_id,),
    )

    with pytest.raises(InvalidDeliberationRecord, match="profile snapshots must have unique"):
        validate_deliberation_record(record)


def test_record_rejects_duplicate_selected_members(sovereign_request, member) -> None:
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id, member.member_id),
    )

    with pytest.raises(InvalidDeliberationRecord, match="selected council member ids"):
        validate_deliberation_record(record)


def test_record_rejects_unselected_interpretation(sovereign_request, member) -> None:
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id,),
        interpretations=(_interpretation("guilliman"),),
    )

    with pytest.raises(InvalidDeliberationRecord, match="selected council members"):
        validate_deliberation_record(record)


def test_record_rejects_duplicate_member_interpretations(sovereign_request, member) -> None:
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id,),
        interpretations=(
            _interpretation(member.member_id),
            _interpretation(member.member_id),
        ),
    )

    with pytest.raises(InvalidDeliberationRecord, match="only one blind interpretation"):
        validate_deliberation_record(record)


def test_record_rejects_legacy_challenge_storage(sovereign_request, member) -> None:
    legacy = Challenge(
        challenger_member_id="vanguard",
        target_member_id="steward",
        target_artifact_id="proposal-steward",
        disputed_claim="Expected demand justifies the commitment.",
        materiality="The preferred strategy changes if demand is lower.",
        failure_consequence="Resources could be committed without adoption.",
    )
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id,),
        challenges=(legacy,),
    )

    with pytest.raises(InvalidDeliberationRecord, match="canonical authored challenges"):
        validate_deliberation_record(record)


def test_plan_complete_record_requires_complete_status(sovereign_request, member) -> None:
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id,),
        plan=_plan(),
        stage=DeliberationStage.PLAN_COMPLETE,
        status=SessionStatus.ACTIVE,
    )

    with pytest.raises(InvalidDeliberationRecord, match="complete session status"):
        validate_deliberation_record(record)


def test_complete_status_requires_plan_complete_record(sovereign_request, member) -> None:
    record = DeliberationRecord(
        request=sovereign_request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id,),
        status=SessionStatus.COMPLETE,
    )

    with pytest.raises(InvalidDeliberationRecord, match="must be at plan_complete"):
        validate_deliberation_record(record)
