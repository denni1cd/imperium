"""Tests proving that a panel or Seneschal proxy cannot masquerade as debate."""

import pytest
from pydantic import ValidationError

from imperium.domain.enums import (
    ChallengeDisposition,
    ChallengePhase,
    DeliberationStage,
    Materiality,
)
from imperium.domain.models import Challenge, ChallengeResponse, DeliberationRecord, SovereignRequest
from imperium.domain.offline import DebateExchange, DebateImpact, OfflineDeliberationSession
from imperium.domain.protocol import ChallengeAssignment, ChallengePlan
from imperium.domain.protocol_trace import ProtocolTrace
from imperium.engine.debate_verification import require_actual_debate, verify_actual_debate


def _assignment(phase: ChallengePhase, challenge_id: str) -> ChallengeAssignment:
    return ChallengeAssignment(
        challenge_id=challenge_id,
        phase=phase,
        round_number=1,
        challenger_member_id="castellan",
        target_member_id="vanguard",
        target_artifact_id="artifact-vanguard",
        target_claim_id="claim-vanguard",
        materiality=Materiality.HIGH,
        reason="The urgency claim may understate downside.",
        expected_consequence="Vanguard must refine or defend the timing claim.",
    )


def _exchange(phase: ChallengePhase, challenge_id: str) -> DebateExchange:
    assignment = _assignment(phase, challenge_id)
    return DebateExchange(
        phase=phase,
        round_number=1,
        assignment=assignment,
        challenge=Challenge(
            challenge_id=challenge_id,
            challenger_member_id="castellan",
            target_member_id="vanguard",
            target_artifact_id="artifact-vanguard",
            disputed_claim="Delay destroys the opportunity.",
            materiality="high",
            failure_consequence="The council may rush into avoidable commitment.",
        ),
        response=ChallengeResponse(
            challenge_id=challenge_id,
            member_id="vanguard",
            disposition=ChallengeDisposition.REFINE,
            response="Act immediately, but limit the first commitment to a reversible pilot.",
            revised_claim="Immediate action should be a reversible pilot rather than a full build.",
        ),
    )


def _session(*, exchanges=(), impacts=(), plans=()) -> OfflineDeliberationSession:
    request = SovereignRequest(original_text="Choose a strategy.")
    return OfflineDeliberationSession(
        record=DeliberationRecord(request=request),
        protocol_trace=ProtocolTrace(challenge_plans=tuple(plans)),
        lifecycle_history=(DeliberationStage.CREATED,),
        debate_exchanges=tuple(exchanges),
        debate_impacts=tuple(impacts),
    )


def test_direct_exchange_rejects_seneschal_proxy() -> None:
    assignment = _assignment(ChallengePhase.FRAME, "challenge-1")
    with pytest.raises(ValidationError, match="assigned challenger must articulate"):
        DebateExchange(
            phase=ChallengePhase.FRAME,
            round_number=1,
            assignment=assignment,
            challenge=Challenge(
                challenge_id="challenge-1",
                challenger_member_id="seneschal",
                target_member_id="vanguard",
                target_artifact_id="artifact-vanguard",
                disputed_claim="Delay destroys the opportunity.",
                materiality="high",
                failure_consequence="The council may rush.",
            ),
            response=ChallengeResponse(
                challenge_id="challenge-1",
                member_id="vanguard",
                disposition=ChallengeDisposition.DEFEND,
                response="The opportunity is genuinely time-sensitive.",
            ),
        )


def test_panel_only_session_fails_actual_debate_verification() -> None:
    report = verify_actual_debate(_session())
    assert report.passed is False
    assert any("no direct cross-member" in failure for failure in report.failures)


def test_planned_challenge_without_exchange_fails() -> None:
    assignment = _assignment(ChallengePhase.FRAME, "challenge-1")
    plan = ChallengePlan(
        phase=ChallengePhase.FRAME,
        round_number=1,
        assignments=(assignment,),
    )
    report = verify_actual_debate(_session(plans=(plan,)), require_both_phases=False)
    assert report.passed is False
    assert any("without direct challenger/target exchange" in item for item in report.failures)


def test_exchange_without_later_consequence_fails() -> None:
    exchange = _exchange(ChallengePhase.FRAME, "challenge-1")
    plan = ChallengePlan(
        phase=ChallengePhase.FRAME,
        round_number=1,
        assignments=(exchange.assignment,),
    )
    report = verify_actual_debate(
        _session(exchanges=(exchange,), plans=(plan,)),
        require_both_phases=False,
    )
    assert report.passed is False
    assert any("no later strategic consequence" in item for item in report.failures)


def test_direct_exchange_with_traceable_impact_passes_single_phase() -> None:
    exchange = _exchange(ChallengePhase.FRAME, "challenge-1")
    plan = ChallengePlan(
        phase=ChallengePhase.FRAME,
        round_number=1,
        assignments=(exchange.assignment,),
    )
    impact = DebateImpact(
        exchange_id="challenge-1",
        member_id="vanguard",
        resulting_artifact_id="proposal-vanguard",
        disposition=ChallengeDisposition.REFINE,
        explanation="Vanguard narrowed immediate action to a reversible pilot.",
        position_changed=True,
    )
    report = require_actual_debate(
        _session(exchanges=(exchange,), impacts=(impact,), plans=(plan,)),
        require_both_phases=False,
        minimum_targeted_members=1,
    )
    assert report.passed is True
    assert report.direct_exchange_count == 1
