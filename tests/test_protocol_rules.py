"""Tests for deterministic challenge, visibility, and stopping rules."""

from pathlib import Path

import pytest

from imperium.configuration import (
    load_council_configuration,
    load_protocol_configuration,
    load_value_vocabulary,
)
from imperium.domain.enums import (
    ArtifactKind,
    ChallengeDisposition,
    ChallengePhase,
    ClaimKind,
    ContinuationReason,
    DeliberationStage,
    Materiality,
    StopReason,
)
from imperium.domain.models import ChallengeResponse
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengeAssignment,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    NormalizedClaim,
)
from imperium.engine.protocol_rules import (
    InvalidProtocolArtifact,
    validate_challenge_artifact,
    validate_challenge_plan,
    validate_challenge_response,
    validate_continuation_decision,
    validate_stage_inputs,
    validate_stage_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_configuration():
    vocabulary = load_value_vocabulary(ROOT / "config" / "values.yaml")
    council = load_council_configuration(
        ROOT / "config" / "council.yaml",
        vocabulary=vocabulary,
    )
    protocol = load_protocol_configuration(
        ROOT / "config" / "protocol.yaml",
        vocabulary=vocabulary,
        council=council,
    )
    return council, protocol


def _claim(*, materiality: Materiality = Materiality.HIGH) -> NormalizedClaim:
    return NormalizedClaim(
        claim_id="claim-demand",
        source_artifact_id="proposal-steward",
        source_member_id="steward",
        kind=ClaimKind.ASSUMPTION,
        statement="Expected demand is sufficient to justify the commitment.",
        materiality=materiality,
        decision_impact="The strategy's expected value depends on sufficient demand.",
    )


def _register(*, materiality: Materiality = Materiality.HIGH) -> ClaimRegister:
    return ClaimRegister(
        phase=ChallengePhase.PROPOSAL,
        claims=(_claim(materiality=materiality),),
    )


def _assignment(*, challenger: str = "vanguard") -> ChallengeAssignment:
    return ChallengeAssignment(
        challenge_id="challenge-demand",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        challenger_member_id=challenger,
        target_member_id="steward",
        target_artifact_id="proposal-steward",
        target_claim_id="claim-demand",
        materiality=Materiality.HIGH,
        reason="The recommendation changes if demand is materially lower.",
        expected_consequence="Defend the forecast, narrow the commitment, or request evidence.",
    )


def _authored_challenge() -> ChallengeArtifact:
    return ChallengeArtifact(
        challenge_id="challenge-demand",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        challenger_member_id="vanguard",
        target_member_id="steward",
        target_artifact_id="proposal-steward",
        target_claim_id="claim-demand",
        statement="What committed demand supports this level of investment?",
        failure_consequence="The proposed commitment could consume resources without adoption.",
    )


def test_stage_visibility_rejects_forbidden_artifacts() -> None:
    _, protocol = _load_configuration()
    interpretation = protocol.contract_for(DeliberationStage.INTERPRETATIONS_COMPLETE)

    with pytest.raises(InvalidProtocolArtifact, match="forbidden artifacts"):
        validate_stage_inputs(
            interpretation,
            (
                ArtifactKind.SOVEREIGN_REQUEST,
                ArtifactKind.COUNCIL_SNAPSHOT,
                ArtifactKind.INTERPRETATION,
            ),
        )


def test_stage_output_contract_requires_all_and_only_declared_artifacts() -> None:
    _, protocol = _load_configuration()
    compare_frames = protocol.contract_for(DeliberationStage.FRAMES_COMPARED)

    with pytest.raises(InvalidProtocolArtifact, match="missing=.*frame_register"):
        validate_stage_outputs(compare_frames, (ArtifactKind.CLAIM_REGISTER,))

    validate_stage_outputs(
        compare_frames,
        (ArtifactKind.CLAIM_REGISTER, ArtifactKind.FRAME_REGISTER),
    )


def test_valid_counterweighted_challenge_plan_passes() -> None:
    council, protocol = _load_configuration()
    plan = ChallengePlan(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=(_assignment(),),
    )

    validate_challenge_plan(
        plan,
        claims=_register(),
        council=council,
        policy=protocol.challenge_policy,
    )


def test_authored_challenge_must_match_assignment() -> None:
    assignment = _assignment()
    validate_challenge_artifact(_authored_challenge(), assignment=assignment)

    wrong_author = _authored_challenge().model_copy(
        update={"challenger_member_id": "castellan"}
    )
    with pytest.raises(InvalidProtocolArtifact, match="does not match its assignment"):
        validate_challenge_artifact(wrong_author, assignment=assignment)


def test_challenge_response_must_come_from_assigned_target() -> None:
    assignment = _assignment()
    valid = ChallengeResponse(
        challenge_id=assignment.challenge_id,
        member_id=assignment.target_member_id,
        disposition=ChallengeDisposition.DEFEND,
        response="The staged commitment is supported by the supplied demand evidence.",
    )
    validate_challenge_response(valid, assignment=assignment)

    wrong_target = valid.model_copy(update={"member_id": "architect"})
    with pytest.raises(InvalidProtocolArtifact, match="assigned target"):
        validate_challenge_response(wrong_target, assignment=assignment)


def test_non_counterweight_requires_explicit_override() -> None:
    council, protocol = _load_configuration()
    plan = ChallengePlan(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=(_assignment(challenger="castellan"),),
    )

    with pytest.raises(InvalidProtocolArtifact, match="counterweight or explain"):
        validate_challenge_plan(
            plan,
            claims=_register(),
            council=council,
            policy=protocol.challenge_policy,
        )


def test_low_materiality_claim_cannot_be_challenged() -> None:
    council, protocol = _load_configuration()
    low_claim = _register(materiality=Materiality.LOW)
    assignment = _assignment().model_copy(update={"materiality": Materiality.LOW})
    plan = ChallengePlan(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=(assignment,),
    )

    with pytest.raises(InvalidProtocolArtifact, match="below the configured challenge threshold"):
        validate_challenge_plan(
            plan,
            claims=low_claim,
            council=council,
            policy=protocol.challenge_policy,
        )


def test_repeated_challenge_requires_new_input() -> None:
    council, protocol = _load_configuration()
    prior = ChallengePlan(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=(_assignment(),),
    )
    repeated_assignment = _assignment().model_copy(
        update={"challenge_id": "challenge-demand-round-2", "round_number": 2}
    )
    repeated = ChallengePlan(
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        assignments=(repeated_assignment,),
    )

    with pytest.raises(InvalidProtocolArtifact, match="requires new evidence"):
        validate_challenge_plan(
            repeated,
            claims=_register(),
            council=council,
            policy=protocol.challenge_policy,
            prior_plans=(prior,),
        )

    validate_challenge_plan(
        repeated,
        claims=_register(),
        council=council,
        policy=protocol.challenge_policy,
        prior_plans=(prior,),
        claims_with_new_input={"claim-demand"},
    )


def test_continuation_requires_high_materiality_and_specific_action() -> None:
    _, protocol = _load_configuration()
    decision = ContinuationDecision(
        phase=ChallengePhase.PROPOSAL,
        completed_round=1,
        continue_debate=True,
        reasons=(ContinuationReason.UNRESOLVED_MATERIAL_CLAIM,),
        unresolved_claim_ids=("claim-demand",),
        next_action="Ask the Architect to challenge the revised demand model.",
        justification="The claim could reverse the preferred investment strategy.",
    )

    validate_continuation_decision(
        decision,
        claims=_register(),
        policy=protocol.challenge_policy,
    )

    with pytest.raises(InvalidProtocolArtifact, match="high or critical"):
        validate_continuation_decision(
            decision,
            claims=_register(materiality=Materiality.MEDIUM),
            policy=protocol.challenge_policy,
        )


def test_round_limit_requires_explicit_safety_stop() -> None:
    _, protocol = _load_configuration()
    invalid = ContinuationDecision(
        phase=ChallengePhase.PROPOSAL,
        completed_round=2,
        continue_debate=False,
        unresolved_claim_ids=("claim-demand",),
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="The configured debate rounds are exhausted.",
    )

    with pytest.raises(InvalidProtocolArtifact, match="round_safety_limit"):
        validate_continuation_decision(
            invalid,
            claims=_register(),
            policy=protocol.challenge_policy,
        )

    valid = invalid.model_copy(update={"stop_reason": StopReason.ROUND_SAFETY_LIMIT})
    validate_continuation_decision(
        valid,
        claims=_register(),
        policy=protocol.challenge_policy,
    )
