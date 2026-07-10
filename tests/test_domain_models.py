"""Tests for constitutional domain invariants."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from imperium.domain.enums import ChallengeDisposition, EvidenceOutcome
from imperium.domain.models import (
    ActionStep,
    ActionablePlan,
    Challenge,
    ChallengeResponse,
    DeliberationRecord,
    EvidenceRequest,
    EvidenceResolution,
    ValueVector,
)


def test_value_vector_requires_total_of_one() -> None:
    with pytest.raises(ValidationError, match="sum to 1.0"):
        ValueVector(weights={"economy": Decimal("0.6"), "reliability": Decimal("0.3")})


def test_value_vector_rejects_out_of_range_weight() -> None:
    with pytest.raises(ValidationError, match="between 0 and 1"):
        ValueVector(weights={"economy": Decimal("1.1"), "reliability": Decimal("-0.1")})


def test_challenge_cannot_target_same_member() -> None:
    with pytest.raises(ValidationError, match="different council member"):
        Challenge(
            challenger_member_id="accountant",
            target_member_id="accountant",
            target_artifact_id="frame-1",
            disputed_claim="The project is time-sensitive.",
            materiality="Timing determines whether immediate commitment is justified.",
            failure_consequence="The council could recommend wasteful urgency.",
        )


def test_evidence_disposition_requires_evidence_request() -> None:
    with pytest.raises(ValidationError, match="must include an evidence request"):
        ChallengeResponse(
            challenge_id="challenge-1",
            member_id="gazgul",
            disposition=ChallengeDisposition.REQUEST_EVIDENCE,
            response="The timing claim requires external validation.",
        )


def test_gathered_evidence_requires_payload() -> None:
    with pytest.raises(ValidationError, match="must include evidence"):
        EvidenceResolution(
            evidence_request_id="evidence-1",
            outcome=EvidenceOutcome.GATHERED,
        )


def test_conditional_evidence_requires_conditions() -> None:
    with pytest.raises(ValidationError, match="must include planning conditions"):
        EvidenceResolution(
            evidence_request_id="evidence-1",
            outcome=EvidenceOutcome.PROCEED_CONDITIONALLY,
        )


def test_actionable_plan_requires_ordered_unique_steps() -> None:
    with pytest.raises(ValidationError, match="execution order"):
        ActionablePlan(
            decision="Run a constrained pilot.",
            objective="Validate strategic value before full commitment.",
            immediate_next_action="Define the pilot threshold.",
            steps=(
                ActionStep(
                    order=2,
                    action="Evaluate results.",
                    completion_signal="Results are scored.",
                ),
                ActionStep(
                    order=1,
                    action="Run the pilot.",
                    completion_signal="The pilot is complete.",
                ),
            ),
            stop_or_reconsideration_conditions=("Stop if the threshold is missed.",),
        )


def test_selected_member_requires_profile_snapshot(sovereign_request, member) -> None:
    with pytest.raises(ValidationError, match="missing profile snapshots"):
        DeliberationRecord(
            request=sovereign_request,
            member_snapshots=(member,),
            selected_member_ids=("accountant", "gazgul"),
        )


def test_evidence_request_is_valid_when_complete() -> None:
    evidence_request = EvidenceRequest(
        requester_member_id="accountant",
        disputed_claim="Demand will justify the investment.",
        decision_impact="The launch case depends on expected demand.",
        requested_information="Evidence of committed users.",
        preferred_source="user or market research",
    )
    assert evidence_request.requested_information == "Evidence of committed users."
