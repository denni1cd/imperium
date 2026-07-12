"""Tests for the typed Stage 3 deliberation trace."""

import pytest
from pydantic import ValidationError

from imperium.domain.enums import (
    ChallengePhase,
    ClaimKind,
    Materiality,
    StopReason,
)
from imperium.domain.protocol import (
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    NormalizedClaim,
)
from imperium.domain.protocol_trace import ProtocolTrace


def _register(phase: ChallengePhase) -> ClaimRegister:
    return ClaimRegister(
        phase=phase,
        claims=(
            NormalizedClaim(
                claim_id=f"claim-{phase.value}",
                source_artifact_id=f"artifact-{phase.value}",
                source_member_id="steward",
                kind=ClaimKind.ASSUMPTION,
                statement="A material premise controls the recommendation.",
                materiality=Materiality.HIGH,
                decision_impact="The preferred strategy changes if the premise fails.",
            ),
        ),
    )


def test_protocol_trace_records_each_phase_and_round_once() -> None:
    plan = ChallengePlan(
        phase=ChallengePhase.FRAME,
        round_number=1,
        assignments=(),
        no_challenge_reason="No material frame challenge remains.",
    )
    decision = ContinuationDecision(
        phase=ChallengePhase.FRAME,
        completed_round=1,
        continue_debate=False,
        stop_reason=StopReason.NO_MATERIAL_OPEN_ISSUES,
        justification="All material frame disagreements are either resolved or preserved.",
    )

    trace = ProtocolTrace(
        claim_registers=(_register(ChallengePhase.FRAME),),
        challenge_plans=(plan,),
        continuation_decisions=(decision,),
    )

    assert trace.challenge_plans[0].round_number == 1


def test_continuation_decision_requires_matching_challenge_plan() -> None:
    decision = ContinuationDecision(
        phase=ChallengePhase.PROPOSAL,
        completed_round=1,
        continue_debate=False,
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="Proposal debate is complete.",
    )

    with pytest.raises(ValidationError, match="matching challenge plan"):
        ProtocolTrace(
            claim_registers=(_register(ChallengePhase.PROPOSAL),),
            continuation_decisions=(decision,),
        )


def test_trace_rejects_duplicate_phase_registers() -> None:
    register = _register(ChallengePhase.FRAME)

    with pytest.raises(ValidationError, match="one claim register per phase"):
        ProtocolTrace(claim_registers=(register, register.model_copy()))
