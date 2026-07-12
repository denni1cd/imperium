"""Deterministic enforcement for approved Stage 3 debate rules."""

from __future__ import annotations

from collections import Counter
from collections.abc import Collection, Iterable

from imperium.domain.council import CouncilConfiguration
from imperium.domain.enums import ArtifactKind, Materiality, StopReason
from imperium.domain.protocol import (
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
) -> None:
    """Require every output promised by the stage contract and reject undeclared output."""

    produced = tuple(produced_artifacts)
    required = set(contract.required_output_artifacts)
    actual = set(produced)
    missing = required - actual
    unexpected = actual - required
    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing={sorted(item.value for item in missing)}")
        if unexpected:
            details.append(f"unexpected={sorted(item.value for item in unexpected)}")
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
