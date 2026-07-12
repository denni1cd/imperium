"""Exact Stage 3 contracts for the minimum deliberation protocol."""

from __future__ import annotations

from typing import Literal, Self
from uuid import uuid4

from pydantic import Field, field_validator, model_validator

from imperium.domain.enums import (
    ArtifactKind,
    ChallengePhase,
    ClaimKind,
    ContinuationReason,
    DeliberationStage,
    Materiality,
    ProtocolActor,
    StopReason,
)
from imperium.domain.models import NonEmptyStr, StrictModel


def _new_id() -> str:
    return str(uuid4())


class NormalizedClaim(StrictModel):
    """One decision-relevant proposition preserved in a comparable form."""

    claim_id: str = Field(default_factory=_new_id)
    source_artifact_id: NonEmptyStr
    source_member_id: str | None = None
    kind: ClaimKind
    statement: NonEmptyStr
    materiality: Materiality
    decision_impact: NonEmptyStr
    supporting_evidence: tuple[NonEmptyStr, ...] = ()
    depends_on_claim_ids: tuple[NonEmptyStr, ...] = ()
    contested_by_member_ids: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def reject_self_dependency(self) -> Self:
        if self.claim_id in self.depends_on_claim_ids:
            raise ValueError("a normalized claim cannot depend on itself")
        if len(set(self.depends_on_claim_ids)) != len(self.depends_on_claim_ids):
            raise ValueError("claim dependencies must be unique")
        if len(set(self.contested_by_member_ids)) != len(self.contested_by_member_ids):
            raise ValueError("contesting member identifiers must be unique")
        return self


class ClaimRegister(StrictModel):
    """Inspectable canonical claims for one debate phase."""

    register_id: str = Field(default_factory=_new_id)
    phase: ChallengePhase
    claims: tuple[NormalizedClaim, ...]

    @model_validator(mode="after")
    def validate_claim_graph(self) -> Self:
        if not self.claims:
            raise ValueError("a claim register must contain at least one material claim")
        claim_ids = [claim.claim_id for claim in self.claims]
        if len(set(claim_ids)) != len(claim_ids):
            raise ValueError("normalized claim identifiers must be unique")
        available = set(claim_ids)
        for claim in self.claims:
            unknown = set(claim.depends_on_claim_ids) - available
            if unknown:
                raise ValueError(
                    f"claim {claim.claim_id!r} depends on unknown claims: {sorted(unknown)}"
                )
        return self


class ChallengeAssignment(StrictModel):
    """A targeted challenge selected for a particular debate round."""

    challenge_id: str = Field(default_factory=_new_id)
    phase: ChallengePhase
    round_number: int = Field(ge=1)
    challenger_member_id: NonEmptyStr
    target_member_id: NonEmptyStr
    target_artifact_id: NonEmptyStr
    target_claim_id: NonEmptyStr
    materiality: Materiality
    reason: NonEmptyStr
    expected_consequence: NonEmptyStr
    counterweight_override_reason: str | None = None

    @model_validator(mode="after")
    def prevent_self_challenge(self) -> Self:
        if self.challenger_member_id == self.target_member_id:
            raise ValueError("a challenge assignment must target another advocate")
        return self


class ChallengePlan(StrictModel):
    """The complete, bounded challenge selection for one debate round."""

    plan_id: str = Field(default_factory=_new_id)
    phase: ChallengePhase
    round_number: int = Field(ge=1)
    assignments: tuple[ChallengeAssignment, ...] = ()
    no_challenge_reason: str | None = None

    @model_validator(mode="after")
    def validate_plan(self) -> Self:
        if not self.assignments and not self.no_challenge_reason:
            raise ValueError("an empty challenge plan must explain why no challenge is material")
        if self.assignments and self.no_challenge_reason:
            raise ValueError("a challenge plan cannot contain assignments and a no-challenge reason")

        challenge_ids = [assignment.challenge_id for assignment in self.assignments]
        if len(set(challenge_ids)) != len(challenge_ids):
            raise ValueError("challenge assignment identifiers must be unique")

        identities = [
            (
                assignment.challenger_member_id,
                assignment.target_member_id,
                assignment.target_claim_id,
            )
            for assignment in self.assignments
        ]
        if len(set(identities)) != len(identities):
            raise ValueError("a debate round cannot duplicate the same targeted challenge")

        for assignment in self.assignments:
            if assignment.phase is not self.phase:
                raise ValueError("all challenge assignments must match the plan phase")
            if assignment.round_number != self.round_number:
                raise ValueError("all challenge assignments must match the plan round")
        return self


class ChallengeArtifact(StrictModel):
    """The assigned advocate's own authored challenge to a normalized claim."""

    challenge_id: NonEmptyStr
    phase: ChallengePhase
    round_number: int = Field(ge=1)
    challenger_member_id: NonEmptyStr
    target_member_id: NonEmptyStr
    target_artifact_id: NonEmptyStr
    target_claim_id: NonEmptyStr
    statement: NonEmptyStr
    failure_consequence: NonEmptyStr
    evidence_needed: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def prevent_self_challenge(self) -> Self:
        if self.challenger_member_id == self.target_member_id:
            raise ValueError("an authored challenge must target another advocate")
        return self


class ContinuationDecision(StrictModel):
    """Inspectable decision to continue or stop one debate phase."""

    decision_id: str = Field(default_factory=_new_id)
    phase: ChallengePhase
    completed_round: int = Field(ge=1)
    continue_debate: bool
    reasons: tuple[ContinuationReason, ...] = ()
    unresolved_claim_ids: tuple[NonEmptyStr, ...] = ()
    next_action: str | None = None
    stop_reason: StopReason | None = None
    justification: NonEmptyStr

    @model_validator(mode="after")
    def validate_decision(self) -> Self:
        if self.continue_debate:
            if not self.reasons:
                raise ValueError("continuing debate requires at least one permitted reason")
            if not self.unresolved_claim_ids:
                raise ValueError("continuing debate requires identified unresolved claims")
            if not self.next_action:
                raise ValueError("continuing debate requires a specific next action")
            if self.stop_reason is not None:
                raise ValueError("a continuation decision cannot also contain a stop reason")
        else:
            if self.stop_reason is None:
                raise ValueError("stopping debate requires an explicit stop reason")
            if self.next_action is not None:
                raise ValueError("a stopped debate phase cannot schedule another debate action")
        return self


class ChallengeTurnContract(StrictModel):
    """One advocate-owned subturn within a Seneschal-coordinated challenge stage."""

    turn_id: NonEmptyStr
    speaker_from_assignment: Literal["challenger", "target"]
    allowed_input_artifacts: tuple[ArtifactKind, ...]
    required_output_artifact: ArtifactKind
    prompt_template: NonEmptyStr

    @field_validator("allowed_input_artifacts")
    @classmethod
    def reject_duplicate_inputs(
        cls,
        artifacts: tuple[ArtifactKind, ...],
    ) -> tuple[ArtifactKind, ...]:
        if len(set(artifacts)) != len(artifacts):
            raise ValueError("challenge-turn input artifact lists must not contain duplicates")
        return artifacts

    @model_validator(mode="after")
    def validate_turn_shape(self) -> Self:
        if self.speaker_from_assignment == "challenger":
            if self.required_output_artifact is not ArtifactKind.CHALLENGE:
                raise ValueError("the challenger subturn must produce a challenge artifact")
            required_inputs = {ArtifactKind.CLAIM_REGISTER, ArtifactKind.CHALLENGE_PLAN}
        else:
            if self.required_output_artifact is not ArtifactKind.CHALLENGE_RESPONSE:
                raise ValueError("the target subturn must produce a challenge response")
            required_inputs = {ArtifactKind.CHALLENGE, ArtifactKind.CHALLENGE_PLAN}

        missing = required_inputs - set(self.allowed_input_artifacts)
        if missing:
            raise ValueError(
                "challenge subturn is missing required inputs: "
                f"{sorted(item.value for item in missing)}"
            )
        return self


class OutputCardinalityRule(StrictModel):
    """Require one output artifact for each matching input artifact, including zero."""

    output_artifact: ArtifactKind
    count_from_input_artifact: ArtifactKind

    @model_validator(mode="after")
    def reject_identity_mapping(self) -> Self:
        if self.output_artifact is self.count_from_input_artifact:
            raise ValueError("output cardinality must map between different artifact kinds")
        return self


class StageContract(StrictModel):
    """Exact information and artifact contract for one lifecycle transition."""

    stage_id: NonEmptyStr
    prerequisite_stage: DeliberationStage
    resulting_stage: DeliberationStage
    actor: ProtocolActor
    allowed_input_artifacts: tuple[ArtifactKind, ...]
    required_output_artifacts: tuple[ArtifactKind, ...]
    prompt_template: str | None = None
    per_advocate: bool = False
    blind: bool = False
    permits_evidence_requests: bool = False
    challenge_turns: tuple[ChallengeTurnContract, ...] = ()
    output_cardinality: tuple[OutputCardinalityRule, ...] = ()

    @field_validator("allowed_input_artifacts", "required_output_artifacts")
    @classmethod
    def reject_duplicate_artifacts(
        cls,
        artifacts: tuple[ArtifactKind, ...],
    ) -> tuple[ArtifactKind, ...]:
        if len(set(artifacts)) != len(artifacts):
            raise ValueError("stage artifact lists must not contain duplicates")
        return artifacts

    @model_validator(mode="after")
    def validate_actor_contract(self) -> Self:
        if self.prerequisite_stage is self.resulting_stage:
            raise ValueError("a stage contract must advance the lifecycle")
        if self.actor is ProtocolActor.ENGINE and self.prompt_template is not None:
            raise ValueError("engine-owned stages do not use model prompt templates")
        if self.actor is not ProtocolActor.ENGINE and not self.prompt_template:
            raise ValueError("model-owned stages require a prompt template")
        if self.per_advocate and self.actor is not ProtocolActor.ADVOCATE:
            raise ValueError("only advocate-owned stages can produce one output per advocate")
        if self.blind and not self.per_advocate:
            raise ValueError("blind execution is only valid for per-advocate stages")

        cardinality_outputs = [rule.output_artifact for rule in self.output_cardinality]
        if len(set(cardinality_outputs)) != len(cardinality_outputs):
            raise ValueError("stage output-cardinality targets must be unique")
        overlap = set(cardinality_outputs) & set(self.required_output_artifacts)
        if overlap:
            raise ValueError(
                "conditionally counted outputs cannot also be unconditional outputs: "
                f"{sorted(item.value for item in overlap)}"
            )
        missing_cardinality_inputs = {
            rule.count_from_input_artifact
            for rule in self.output_cardinality
            if rule.count_from_input_artifact not in self.allowed_input_artifacts
        }
        if missing_cardinality_inputs:
            raise ValueError(
                "output cardinality references forbidden input artifacts: "
                f"{sorted(item.value for item in missing_cardinality_inputs)}"
            )

        if self.challenge_turns:
            if self.actor is not ProtocolActor.SENESCHAL:
                raise ValueError("challenge subturns require a Seneschal-coordinated stage")
            speakers = tuple(turn.speaker_from_assignment for turn in self.challenge_turns)
            if speakers != ("challenger", "target"):
                raise ValueError(
                    "challenge stages must execute challenger then target subturns"
                )
            required_stage_outputs = {
                ArtifactKind.CHALLENGE_PLAN,
                ArtifactKind.CONTINUATION_DECISION,
            }
            missing = required_stage_outputs - set(self.required_output_artifacts)
            if missing:
                raise ValueError(
                    "challenge stages are missing unconditional outputs: "
                    f"{sorted(item.value for item in missing)}"
                )
            conditional_turn_outputs = {
                turn.required_output_artifact for turn in self.challenge_turns
            }
            illegal_unconditional = conditional_turn_outputs & set(
                self.required_output_artifacts
            )
            if illegal_unconditional:
                raise ValueError(
                    "challenge subturn outputs must remain conditional on assignments: "
                    f"{sorted(item.value for item in illegal_unconditional)}"
                )
        elif ArtifactKind.CHALLENGE in self.required_output_artifacts:
            raise ValueError("a stage requiring challenge artifacts must define challenge subturns")
        return self


class ChallengePolicy(StrictModel):
    """Bounded rules for selecting consequential rather than theatrical challenges."""

    challenge_materiality_threshold: Materiality
    continuation_materiality_threshold: Materiality
    maximum_assignments_per_round: int = Field(ge=1)
    maximum_targets_per_advocate_per_round: int = Field(ge=1)
    maximum_rounds_per_phase: int = Field(ge=1)
    require_counterweight_when_available: bool
    require_new_evidence_or_revision_for_repeat: bool
    ranking_order: tuple[NonEmptyStr, ...]

    @field_validator("ranking_order")
    @classmethod
    def require_ranking_rules(cls, entries: tuple[str, ...]) -> tuple[str, ...]:
        if not entries:
            raise ValueError("challenge policy requires a deterministic ranking order")
        return entries


class EvidencePolicy(StrictModel):
    """Exact routing rules for decision-critical missing information."""

    user_clarification_conditions: tuple[NonEmptyStr, ...]
    external_research_conditions: tuple[NonEmptyStr, ...]
    conditional_planning_conditions: tuple[NonEmptyStr, ...]
    pause_conditions: tuple[NonEmptyStr, ...]

    @field_validator(
        "user_clarification_conditions",
        "external_research_conditions",
        "conditional_planning_conditions",
        "pause_conditions",
    )
    @classmethod
    def require_evidence_route(cls, entries: tuple[str, ...]) -> tuple[str, ...]:
        if not entries:
            raise ValueError("every evidence route requires at least one explicit condition")
        return entries


class StoppingPolicy(StrictModel):
    """Objective rules for ending debate without premature consensus or repetition."""

    continuation_reasons: tuple[ContinuationReason, ...]
    stop_reasons: tuple[StopReason, ...]
    require_specific_next_action: Literal[True]
    preserve_unresolved_high_materiality_issues: Literal[True]
    safety_limit_behavior: Literal["pause_or_proceed_conditionally"]

    @model_validator(mode="after")
    def require_complete_reason_sets(self) -> Self:
        if set(self.continuation_reasons) != set(ContinuationReason):
            raise ValueError("stopping policy must enumerate every permitted continuation reason")
        if set(self.stop_reasons) != set(StopReason):
            raise ValueError("stopping policy must enumerate every permitted stop reason")
        return self


class AbbreviatedPathPolicy(StrictModel):
    """Rules for simple decisions, disabled during the first controlled experiments."""

    enabled_for_initial_experiments: Literal[False]
    required_criteria: tuple[NonEmptyStr, ...]
    permitted_skips: tuple[NonEmptyStr, ...]

    @field_validator("required_criteria", "permitted_skips")
    @classmethod
    def require_abbreviation_rules(cls, entries: tuple[str, ...]) -> tuple[str, ...]:
        if not entries:
            raise ValueError("abbreviated-path policy sections cannot be empty")
        return entries


class ProtocolConfiguration(StrictModel):
    """Approved versioned definition of the complete minimum protocol."""

    version: NonEmptyStr
    status: Literal["approved"]
    vocabulary_version: NonEmptyStr
    council_version: NonEmptyStr
    normalization_rules: tuple[NonEmptyStr, ...]
    stage_contracts: tuple[StageContract, ...]
    challenge_policy: ChallengePolicy
    evidence_policy: EvidencePolicy
    stopping_policy: StoppingPolicy
    abbreviated_path: AbbreviatedPathPolicy

    @field_validator("normalization_rules")
    @classmethod
    def require_normalization_rules(cls, entries: tuple[str, ...]) -> tuple[str, ...]:
        if not entries:
            raise ValueError("the protocol requires explicit claim normalization rules")
        return entries

    @model_validator(mode="after")
    def validate_stage_chain(self) -> Self:
        if not self.stage_contracts:
            raise ValueError("the protocol requires stage contracts")

        stage_ids = [contract.stage_id for contract in self.stage_contracts]
        if len(set(stage_ids)) != len(stage_ids):
            raise ValueError("protocol stage identifiers must be unique")

        expected_prerequisite = DeliberationStage.CREATED
        resulting_stages: list[DeliberationStage] = []
        for contract in self.stage_contracts:
            if contract.prerequisite_stage is not expected_prerequisite:
                raise ValueError(
                    f"stage {contract.stage_id!r} requires {contract.prerequisite_stage.value!r}; "
                    f"expected {expected_prerequisite.value!r}"
                )
            expected_prerequisite = contract.resulting_stage
            resulting_stages.append(contract.resulting_stage)

        required_stages = [stage for stage in DeliberationStage if stage is not DeliberationStage.CREATED]
        if resulting_stages != required_stages:
            raise ValueError("protocol stage contracts must cover the lifecycle exactly once and in order")

        interpretation = next(
            contract
            for contract in self.stage_contracts
            if contract.resulting_stage is DeliberationStage.INTERPRETATIONS_COMPLETE
        )
        if interpretation.actor is not ProtocolActor.ADVOCATE or not interpretation.blind:
            raise ValueError("independent interpretation must be blind and advocate-owned")
        forbidden_initial_inputs = set(interpretation.allowed_input_artifacts) - {
            ArtifactKind.SOVEREIGN_REQUEST,
            ArtifactKind.COUNCIL_SNAPSHOT,
        }
        if forbidden_initial_inputs:
            raise ValueError(
                "independent interpretation cannot receive council artifacts: "
                f"{sorted(item.value for item in forbidden_initial_inputs)}"
            )

        challenge_stages = {
            DeliberationStage.FRAME_CHALLENGES_COMPLETE,
            DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
        }
        evidence_stages = {
            DeliberationStage.EVIDENCE_RESOLVED,
            DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED,
        }
        for contract in self.stage_contracts:
            if contract.resulting_stage in challenge_stages and not contract.challenge_turns:
                raise ValueError(
                    f"challenge stage {contract.stage_id!r} must define advocate subturns"
                )
            if contract.resulting_stage not in challenge_stages and contract.challenge_turns:
                raise ValueError(
                    f"non-challenge stage {contract.stage_id!r} cannot define challenge subturns"
                )
            if contract.resulting_stage in evidence_stages:
                expected_rule = OutputCardinalityRule(
                    output_artifact=ArtifactKind.EVIDENCE_RESOLUTION,
                    count_from_input_artifact=ArtifactKind.EVIDENCE_REQUEST,
                )
                if contract.output_cardinality != (expected_rule,):
                    raise ValueError(
                        f"evidence stage {contract.stage_id!r} must resolve each evidence request exactly once"
                    )
            elif contract.output_cardinality:
                raise ValueError(
                    f"non-evidence stage {contract.stage_id!r} cannot define output cardinality"
                )

        final_contract = self.stage_contracts[-1]
        if final_contract.resulting_stage is not DeliberationStage.PLAN_COMPLETE:
            raise ValueError("the protocol must terminate with an actionable plan")
        if ArtifactKind.ACTIONABLE_PLAN not in final_contract.required_output_artifacts:
            raise ValueError("the final stage must require an actionable plan artifact")
        return self

    def contract_for(self, resulting_stage: DeliberationStage) -> StageContract:
        """Return the exact contract that produces one lifecycle stage."""

        return next(
            contract for contract in self.stage_contracts if contract.resulting_stage is resulting_stage
        )
