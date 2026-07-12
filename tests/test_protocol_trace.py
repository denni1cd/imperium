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
    ChallengeArtifact,
    ChallengeAssignment,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    NormalizedClaim,
)
from imperium.domain.protocol_trace import ClaimRegisterSnapshot, ProtocolTrace


def _register(phase: ChallengePhase, *, register_id: str) -> ClaimRegister:
    return ClaimRegister(
        register_id=register_id,
        phase=phase,
        claims=(
            NormalizedClaim(
                claim_id=f"claim-{phase.value}-{register_id}",
                source_artifact_id=f"artifact-{phase.value}",
                source_member_id="steward",
                kind=ClaimKind.ASSUMPTION,
                statement="A material premise controls the recommendation.",
                materiality=Materiality.HIGH,
                decision_impact="The preferred strategy changes if the premise fails.",
            ),
        ),
    )


def _initial_snapshot(phase: ChallengePhase) -> ClaimRegisterSnapshot:
    return ClaimRegisterSnapshot(
        phase=phase,
        round_number=0,
        claim_register=_register(phase, register_id=f"register-{phase.value}-0"),
    )


def _assigned_plan() -> ChallengePlan:
    assignment = ChallengeAssignment(
        challenge_id="challenge-proposal-1",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        challenger_member_id="vanguard",
        target_member_id="steward",
        target_artifact_id="proposal-steward",
        target_claim_id="claim-proposal-1",
        materiality=Materiality.HIGH,
        reason="Demand controls whether the investment is justified.",
        expected_consequence="Defend, refine, or condition the commitment.",
    )
    return ChallengePlan(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=(assignment,),
    )


def _authored_challenge() -> ChallengeArtifact:
    return ChallengeArtifact(
        challenge_id="challenge-proposal-1",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        challenger_member_id="vanguard",
        target_member_id="steward",
        target_artifact_id="proposal-steward",
        target_claim_id="claim-proposal-1",
        statement="What committed demand justifies the proposed investment?",
        failure_consequence="The resources could be committed without sufficient adoption.",
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
        claim_register_snapshots=(_initial_snapshot(ChallengePhase.FRAME),),
        challenge_plans=(plan,),
        continuation_decisions=(decision,),
    )

    assert trace.challenge_plans[0].round_number == 1


def test_protocol_trace_preserves_authored_challenge_assignment() -> None:
    trace = ProtocolTrace(
        challenge_plans=(_assigned_plan(),),
        challenges=(_authored_challenge(),),
    )
    assert trace.challenges[0].challenger_member_id == "vanguard"

    invalid = _authored_challenge().model_copy(update={"target_member_id": "architect"})
    with pytest.raises(ValidationError, match="does not match its assignment"):
        ProtocolTrace(challenge_plans=(_assigned_plan(),), challenges=(invalid,))


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
            claim_register_snapshots=(_initial_snapshot(ChallengePhase.PROPOSAL),),
            continuation_decisions=(decision,),
        )


def test_trace_rejects_duplicate_phase_and_round_snapshots() -> None:
    snapshot = _initial_snapshot(ChallengePhase.FRAME)

    with pytest.raises(ValidationError, match="phase and round combinations must be unique"):
        ProtocolTrace(claim_register_snapshots=(snapshot, snapshot.model_copy()))


def test_later_claim_register_must_supersede_prior_round() -> None:
    initial = _initial_snapshot(ChallengePhase.FRAME)
    incorrect = ClaimRegisterSnapshot(
        phase=ChallengePhase.FRAME,
        round_number=1,
        claim_register=_register(ChallengePhase.FRAME, register_id="register-frame-1"),
        supersedes_register_id="wrong-register",
    )

    with pytest.raises(ValidationError, match="must supersede the prior register"):
        ProtocolTrace(claim_register_snapshots=(initial, incorrect))

    correct = incorrect.model_copy(
        update={"supersedes_register_id": initial.claim_register.register_id}
    )
    trace = ProtocolTrace(claim_register_snapshots=(initial, correct))
    assert trace.claim_register_snapshots[-1].round_number == 1
