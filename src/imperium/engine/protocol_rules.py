"""Deterministic enforcement for approved Stage 3 debate rules."""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Iterable

from imperium.domain.council import CouncilConfiguration
from imperium.domain.enums import (
    ArtifactKind,
    EvidenceOutcome,
    Materiality,
    SessionStatus,
    StopReason,
)
from imperium.domain.models import ChallengeResponse, EvidenceRequest, EvidenceResolution
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengeAssignment,
    ChallengePlan,
    ChallengePolicy,
    ClaimRegister,
    ContinuationDecision,
    StageContract,
)


class InvalidProtocolArtifact(ValueError):
    """Raised when an artifact violates the approved protocol configuration."""


_MATERIALITY_RANK = {
    Materiality.LOW: 0,
    Materiality.MEDIUM: 1,
    Materiality.HIGH: 2,
    Materiality.CRITICAL: 3,
}


def _at_least(actual: Materiality, threshold: Materiality) -> bool:
    return _MATERIALITY_RANK[actual] >= _MATERIALITY_RANK[threshold]


def _duplicates(values: Iterable[str]) -> set[str]:
    counts = Counter(values)
    return {value for value, count in counts.items() if count > 1}


def validate_stage_inputs(
    contract: StageContract,
    supplied_artifacts: Iterable[ArtifactKind],
) -> None:
    """Reject any artifact disclosed outside the stage's explicit information boundary."""

    supplied = tuple(supplied_artifacts)
    unexpected = set(supplied) - set(contract.allowed_input_artifacts)
    if unexpected:
        raise InvalidProtocolArtifact(
            f"stage {contract.stage_id!r} received forbidden artifacts: "
            f"{sorted(item.value for item in unexpected)}"
        )


def validate_stage_outputs(
    contract: StageContract,
    produced_artifacts: Iterable[ArtifactKind],
    *,
    supplied_input_artifacts: Iterable[ArtifactKind] = (),
) -> None:
    """Validate unconditional, subturn, and input-counted stage outputs."""

    produced = tuple(produced_artifacts)
    produced_counts = Counter(produced)
    input_counts = Counter(supplied_input_artifacts)

    required = set(contract.required_output_artifacts)
    conditional = {rule.output_artifact for rule in contract.output_cardinality}
    subturn_outputs = {
        turn.required_output_artifact for turn in contract.challenge_turns
    }
    allowed = required | conditional | subturn_outputs
    actual = set(produced)

    missing = {artifact for artifact in required if produced_counts[artifact] == 0}
    unexpected = actual - allowed
    cardinality_errors: list[str] = []
    for rule in contract.output_cardinality:
        expected_count = input_counts[rule.count_from_input_artifact]
        actual_count = produced_counts[rule.output_artifact]
        if actual_count != expected_count:
            cardinality_errors.append(
                f"{rule.output_artifact.value}={actual_count}; "
                f"expected {expected_count} from {rule.count_from_input_artifact.value}"
            )

    if missing or unexpected or cardinality_errors:
        details: list[str] = []
        if missing:
            details.append(f"missing={sorted(item.value for item in missing)}")
        if unexpected:
            details.append(f"unexpected={sorted(item.value for item in unexpected)}")
        if cardinality_errors:
            details.append("cardinality=" + ", ".join(cardinality_errors))
        raise InvalidProtocolArtifact(
            f"stage {contract.stage_id!r} output contract failed: " + "; ".join(details)
        )


def validate_challenge_plan(
    plan: ChallengePlan,
    *,
    claims: ClaimRegister,
    council: CouncilConfiguration,
    policy: ChallengePolicy,
    prior_plans: Iterable[ChallengePlan] = (),
    claims_with_new_input: Collection[str] = (),
) -> None:
    """Enforce material, bounded, counterweighted challenge assignment."""

    if plan.phase is not claims.phase:
        raise InvalidProtocolArtifact("challenge plan and claim register phases must match")
    if len(plan.assignments) > policy.maximum_assignments_per_round:
        raise InvalidProtocolArtifact(
            "challenge plan exceeds maximum assignments per round: "
            f"{len(plan.assignments)} > {policy.maximum_assignments_per_round}"
        )

    claim_by_id = {claim.claim_id: claim for claim in claims.claims}
    advocate_ids = set(council.advocate_member_ids)
    differentiation = {entry.member_id: entry for entry in council.differentiation}
    target_counts = Counter(assignment.target_member_id for assignment in plan.assignments)
    overloaded = {
        member_id: count
        for member_id, count in target_counts.items()
        if count > policy.maximum_targets_per_advocate_per_round
    }
    if overloaded:
        raise InvalidProtocolArtifact(
            f"challenge plan overloads target advocates: {dict(sorted(overloaded.items()))}"
        )

    previous_identities = {
        (
            assignment.challenger_member_id,
            assignment.target_member_id,
            assignment.target_claim_id,
        )
        for previous in prior_plans
        for assignment in previous.assignments
    }
    new_input = set(claims_with_new_input)

    for assignment in plan.assignments:
        if assignment.challenger_member_id not in advocate_ids:
            raise InvalidProtocolArtifact(
                f"challenge challenger is not an advocate: {assignment.challenger_member_id!r}"
            )
        if assignment.target_member_id not in advocate_ids:
            raise InvalidProtocolArtifact(
                f"challenge target is not an advocate: {assignment.target_member_id!r}"
            )

        claim = claim_by_id.get(assignment.target_claim_id)
        if claim is None:
            raise InvalidProtocolArtifact(
                f"challenge targets unknown claim: {assignment.target_claim_id!r}"
            )
        if claim.source_artifact_id != assignment.target_artifact_id:
            raise InvalidProtocolArtifact(
                f"challenge target artifact does not match claim {claim.claim_id!r}"
            )
        if claim.source_member_id != assignment.target_member_id:
            raise InvalidProtocolArtifact(
                f"challenge target member does not own claim {claim.claim_id!r}"
            )
        if assignment.materiality is not claim.materiality:
            raise InvalidProtocolArtifact(
                f"challenge materiality must match normalized claim {claim.claim_id!r}"
            )
        if not _at_least(claim.materiality, policy.challenge_materiality_threshold):
            raise InvalidProtocolArtifact(
                f"claim {claim.claim_id!r} is below the configured challenge threshold"
            )

        expected_counterweights = set(
            differentiation[assignment.target_member_id].counterweight_member_ids
        )
        if (
            policy.require_counterweight_when_available
            and expected_counterweights
            and assignment.challenger_member_id not in expected_counterweights
            and not assignment.counterweight_override_reason
        ):
            raise InvalidProtocolArtifact(
                f"challenge to {assignment.target_member_id!r} must use an identified "
                "counterweight or explain the override"
            )

        identity = (
            assignment.challenger_member_id,
            assignment.target_member_id,
            assignment.target_claim_id,
        )
        if (
            policy.require_new_evidence_or_revision_for_repeat
            and identity in previous_identities
            and assignment.target_claim_id not in new_input
        ):
            raise InvalidProtocolArtifact(
                "a repeated challenge requires new evidence or a revised claim: "
                f"{identity!r}"
            )


def validate_challenge_artifact(
    challenge: ChallengeArtifact,
    *,
    assignment: ChallengeAssignment,
) -> None:
    """Require the assigned challenger to author exactly the routed challenge."""

    expected = {
        "challenge_id": assignment.challenge_id,
        "phase": assignment.phase,
        "round_number": assignment.round_number,
        "challenger_member_id": assignment.challenger_member_id,
        "target_member_id": assignment.target_member_id,
        "target_artifact_id": assignment.target_artifact_id,
        "target_claim_id": assignment.target_claim_id,
    }
    actual = {
        "challenge_id": challenge.challenge_id,
        "phase": challenge.phase,
        "round_number": challenge.round_number,
        "challenger_member_id": challenge.challenger_member_id,
        "target_member_id": challenge.target_member_id,
        "target_artifact_id": challenge.target_artifact_id,
        "target_claim_id": challenge.target_claim_id,
    }
    mismatched = {
        key: {"expected": expected[key], "actual": actual[key]}
        for key in expected
        if actual[key] != expected[key]
    }
    if mismatched:
        raise InvalidProtocolArtifact(
            f"authored challenge does not match its assignment: {mismatched}"
        )


def validate_challenge_response(
    response: ChallengeResponse,
    *,
    assignment: ChallengeAssignment,
) -> None:
    """Require the assigned target to answer the routed challenge."""

    if response.challenge_id != assignment.challenge_id:
        raise InvalidProtocolArtifact("challenge response references the wrong challenge")
    if response.member_id != assignment.target_member_id:
        raise InvalidProtocolArtifact("challenge response was not produced by the assigned target")


def validate_challenge_round_outputs(
    plan: ChallengePlan,
    *,
    challenges: Iterable[ChallengeArtifact],
    responses: Iterable[ChallengeResponse],
) -> None:
    """Require one authored challenge and response per nonempty assignment, or none."""

    challenge_items = tuple(challenges)
    response_items = tuple(responses)
    assignment_by_id = {
        assignment.challenge_id: assignment for assignment in plan.assignments
    }
    expected_ids = set(assignment_by_id)

    challenge_ids = [item.challenge_id for item in challenge_items]
    response_ids = [item.challenge_id for item in response_items]
    duplicate_challenges = _duplicates(challenge_ids)
    duplicate_responses = _duplicates(response_ids)
    if duplicate_challenges:
        raise InvalidProtocolArtifact(
            f"challenge round contains duplicate authored challenges: {sorted(duplicate_challenges)}"
        )
    if duplicate_responses:
        raise InvalidProtocolArtifact(
            f"challenge round contains duplicate responses: {sorted(duplicate_responses)}"
        )

    if set(challenge_ids) != expected_ids:
        raise InvalidProtocolArtifact(
            "authored challenge identifiers must exactly match challenge assignments"
        )
    if set(response_ids) != expected_ids:
        raise InvalidProtocolArtifact(
            "challenge response identifiers must exactly match challenge assignments"
        )

    for challenge in challenge_items:
        validate_challenge_artifact(
            challenge,
            assignment=assignment_by_id[challenge.challenge_id],
        )
    for response in response_items:
        validate_challenge_response(
            response,
            assignment=assignment_by_id[response.challenge_id],
        )


def validate_evidence_resolutions(
    requests: Iterable[EvidenceRequest],
    resolutions: Iterable[EvidenceResolution],
) -> None:
    """Require exactly one resolution for every evidence request, including zero."""

    request_items = tuple(requests)
    resolution_items = tuple(resolutions)
    request_ids = [item.evidence_request_id for item in request_items]
    resolution_ids = [item.evidence_request_id for item in resolution_items]

    duplicate_requests = _duplicates(request_ids)
    duplicate_resolutions = _duplicates(resolution_ids)
    if duplicate_requests:
        raise InvalidProtocolArtifact(
            f"evidence request identifiers must be unique: {sorted(duplicate_requests)}"
        )
    if duplicate_resolutions:
        raise InvalidProtocolArtifact(
            f"evidence requests may be resolved only once: {sorted(duplicate_resolutions)}"
        )
    if set(request_ids) != set(resolution_ids):
        missing = set(request_ids) - set(resolution_ids)
        orphaned = set(resolution_ids) - set(request_ids)
        raise InvalidProtocolArtifact(
            "evidence resolution mapping is incomplete; "
            f"missing={sorted(missing)}, orphaned={sorted(orphaned)}"
        )


def evidence_session_status(
    resolutions: Iterable[EvidenceResolution],
) -> SessionStatus:
    """Return the required session status after a validated evidence stage."""

    outcomes = {item.outcome for item in resolutions}
    if EvidenceOutcome.DELIBERATION_PAUSED in outcomes:
        return SessionStatus.PAUSED
    if EvidenceOutcome.USER_CLARIFICATION_REQUIRED in outcomes:
        return SessionStatus.WAITING_FOR_USER
    return SessionStatus.ACTIVE


def validate_continuation_decision(
    decision: ContinuationDecision,
    *,
    claims: ClaimRegister,
    policy: ChallengePolicy,
) -> None:
    """Continue only for an adjudication-relevant unresolved issue and bounded next action."""

    if decision.phase is not claims.phase:
        raise InvalidProtocolArtifact("continuation decision and claim register phases must match")

    claim_by_id = {claim.claim_id: claim for claim in claims.claims}
    unknown = set(decision.unresolved_claim_ids) - set(claim_by_id)
    if unknown:
        raise InvalidProtocolArtifact(
            f"continuation decision references unknown claims: {sorted(unknown)}"
        )

    if decision.continue_debate:
        if decision.completed_round >= policy.maximum_rounds_per_phase:
            raise InvalidProtocolArtifact(
                "debate cannot continue past the configured round safety limit; "
                "pause or proceed conditionally while preserving unresolved issues"
            )
        insufficient = [
            claim_id
            for claim_id in decision.unresolved_claim_ids
            if not _at_least(
                claim_by_id[claim_id].materiality,
                policy.continuation_materiality_threshold,
            )
        ]
        if insufficient:
            raise InvalidProtocolArtifact(
                "continuation requires high or critical unresolved claims: "
                f"{sorted(insufficient)}"
            )
    elif (
        decision.completed_round >= policy.maximum_rounds_per_phase
        and decision.unresolved_claim_ids
        and decision.stop_reason is not StopReason.ROUND_SAFETY_LIMIT
    ):
        raise InvalidProtocolArtifact(
            "stopping at the round safety limit with unresolved claims must record "
            "round_safety_limit"
        )
