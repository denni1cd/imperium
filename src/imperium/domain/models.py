"""Pydantic contracts for inspectable Imperium deliberations."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated, Any, Self
from uuid import uuid4

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SerializeAsAny,
    field_validator,
    model_validator,
)

from imperium.domain.enums import (
    ChallengeDisposition,
    DeliberationStage,
    EvidenceOutcome,
    SessionStatus,
)

NonEmptyStr = Annotated[str, Field(min_length=1)]
Confidence = Annotated[Decimal, Field(ge=Decimal("0"), le=Decimal("1"))]
_VECTOR_EPSILON = Decimal("0.000001")


def _new_id() -> str:
    return str(uuid4())


class StrictModel(BaseModel):
    """Base contract that rejects undeclared data instead of silently discarding it."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, str_strip_whitespace=True)


class ValueVector(StrictModel):
    """Persistent strategic priorities whose finite weights sum to one."""

    weights: dict[NonEmptyStr, Decimal]

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, weights: dict[str, Decimal]) -> dict[str, Decimal]:
        if not weights:
            raise ValueError("a value vector must contain at least one strategic value")
        invalid = {name: weight for name, weight in weights.items() if weight < 0 or weight > 1}
        if invalid:
            raise ValueError(f"value weights must be between 0 and 1: {invalid}")
        return weights

    @model_validator(mode="after")
    def validate_total(self) -> Self:
        total = sum(self.weights.values(), start=Decimal("0"))
        if abs(total - Decimal("1")) > _VECTOR_EPSILON:
            raise ValueError(f"value weights must sum to 1.0; received {total}")
        return self

    @property
    def total(self) -> Decimal:
        return sum(self.weights.values(), start=Decimal("0"))


class MemberProfile(StrictModel):
    """Persistent strategic identity for one council member."""

    member_id: NonEmptyStr
    title: NonEmptyStr
    purpose: NonEmptyStr
    values: ValueVector
    doctrine: tuple[NonEmptyStr, ...]
    jurisdiction: tuple[NonEmptyStr, ...] = ()
    vigilance: tuple[NonEmptyStr, ...] = ()
    accepted_sacrifices: tuple[NonEmptyStr, ...] = ()
    evidence_requirements: tuple[NonEmptyStr, ...] = ()
    revision_triggers: tuple[NonEmptyStr, ...] = ()
    presentation: dict[str, NonEmptyStr] = Field(default_factory=dict)

    @field_validator("doctrine")
    @classmethod
    def doctrine_is_required(cls, doctrine: tuple[str, ...]) -> tuple[str, ...]:
        if not doctrine:
            raise ValueError("a member profile requires at least one doctrine statement")
        return doctrine


class SovereignRequest(StrictModel):
    """The preserved user request and authoritative constraints."""

    request_id: str = Field(default_factory=_new_id)
    original_text: NonEmptyStr
    goals: tuple[NonEmptyStr, ...] = ()
    hard_constraints: tuple[NonEmptyStr, ...] = ()
    prohibitions: tuple[NonEmptyStr, ...] = ()
    supplied_facts: tuple[NonEmptyStr, ...] = ()
    context: dict[str, Any] = Field(default_factory=dict)


class Interpretation(StrictModel):
    """One member's blind interpretation of the original request."""

    interpretation_id: str = Field(default_factory=_new_id)
    member_id: NonEmptyStr
    core_decision: NonEmptyStr
    desired_outcome: NonEmptyStr
    opportunities: tuple[NonEmptyStr, ...] = ()
    risks: tuple[NonEmptyStr, ...] = ()
    assumptions: tuple[NonEmptyStr, ...] = ()
    missing_information: tuple[NonEmptyStr, ...] = ()
    initial_inclination: NonEmptyStr
    value_influence: dict[NonEmptyStr, NonEmptyStr]
    confidence: Confidence


class Frame(StrictModel):
    """A distinct interpretation through which the decision can be evaluated."""

    frame_id: str = Field(default_factory=_new_id)
    label: NonEmptyStr
    description: NonEmptyStr
    advocate_member_ids: tuple[NonEmptyStr, ...]
    decision_impact: NonEmptyStr


class FrameRegister(StrictModel):
    """Visible comparison of shared, contested, and unique problem frames."""

    shared_frames: tuple[Frame, ...] = ()
    contested_frames: tuple[Frame, ...] = ()
    unique_frames: tuple[Frame, ...] = ()
    factual_disagreements: tuple[NonEmptyStr, ...] = ()
    interpretive_disagreements: tuple[NonEmptyStr, ...] = ()
    value_disagreements: tuple[NonEmptyStr, ...] = ()


class EvidenceRequest(StrictModel):
    """A decision-critical request that must be resolved by the protocol."""

    evidence_request_id: str = Field(default_factory=_new_id)
    requester_member_id: NonEmptyStr
    disputed_claim: NonEmptyStr
    decision_impact: NonEmptyStr
    requested_information: NonEmptyStr
    preferred_source: NonEmptyStr


class EvidenceResolution(StrictModel):
    """One of the constitutionally permitted outcomes for an evidence request."""

    evidence_request_id: NonEmptyStr
    outcome: EvidenceOutcome
    evidence: tuple[NonEmptyStr, ...] = ()
    source_references: tuple[NonEmptyStr, ...] = ()
    remaining_uncertainty: tuple[NonEmptyStr, ...] = ()
    planning_conditions: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def validate_outcome_details(self) -> Self:
        if self.outcome is EvidenceOutcome.GATHERED and not self.evidence:
            raise ValueError("gathered evidence outcomes must include evidence")
        if self.outcome is EvidenceOutcome.PROCEED_CONDITIONALLY and not self.planning_conditions:
            raise ValueError("conditional evidence outcomes must include planning conditions")
        return self


class Challenge(StrictModel):
    """A targeted challenge to a material interpretation, claim, or strategy."""

    challenge_id: str = Field(default_factory=_new_id)
    challenger_member_id: NonEmptyStr
    target_member_id: NonEmptyStr
    target_artifact_id: NonEmptyStr
    disputed_claim: NonEmptyStr
    materiality: NonEmptyStr
    failure_consequence: NonEmptyStr
    evidence_needed: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def prevent_self_challenge(self) -> Self:
        if self.challenger_member_id == self.target_member_id:
            raise ValueError("a targeted challenge must come from a different council member")
        return self


class ChallengeResponse(StrictModel):
    """Required consequential response to a challenge."""

    challenge_id: NonEmptyStr
    member_id: NonEmptyStr
    disposition: ChallengeDisposition
    response: NonEmptyStr
    revised_claim: str | None = None
    evidence_request: EvidenceRequest | None = None

    @model_validator(mode="after")
    def validate_disposition_payload(self) -> Self:
        if self.disposition is ChallengeDisposition.REFINE and not self.revised_claim:
            raise ValueError("a refined response must include the revised claim")
        if self.disposition is ChallengeDisposition.REQUEST_EVIDENCE and not self.evidence_request:
            raise ValueError("an evidence-request disposition must include an evidence request")
        return self


class StrategyProposal(StrictModel):
    """A member's proposed course of action after frame challenge and evidence resolution."""

    proposal_id: str = Field(default_factory=_new_id)
    member_id: NonEmptyStr
    title: NonEmptyStr
    summary: NonEmptyStr
    proposed_actions: tuple[NonEmptyStr, ...]
    expected_benefits: tuple[NonEmptyStr, ...]
    assumptions: tuple[NonEmptyStr, ...] = ()
    tradeoffs: tuple[NonEmptyStr, ...] = ()
    risks: tuple[NonEmptyStr, ...] = ()
    sacrifices: tuple[NonEmptyStr, ...] = ()
    decision_triggers: tuple[NonEmptyStr, ...] = ()
    reconsideration_conditions: tuple[NonEmptyStr, ...]
    confidence: Confidence

    @field_validator("proposed_actions", "expected_benefits", "reconsideration_conditions")
    @classmethod
    def require_nonempty_strategy_sections(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if not value:
            raise ValueError("strategy actions, benefits, and reconsideration conditions are required")
        return value


class Revision(StrictModel):
    """A traceable post-debate revision or justified decision to retain a proposal."""

    revision_id: str = Field(default_factory=_new_id)
    member_id: NonEmptyStr
    original_proposal_id: NonEmptyStr
    revised_proposal: StrategyProposal
    changes: tuple[NonEmptyStr, ...] = ()
    reasons: tuple[NonEmptyStr, ...]
    supporting_evidence: tuple[NonEmptyStr, ...] = ()
    concessions: tuple[NonEmptyStr, ...] = ()
    unresolved_disagreements: tuple[NonEmptyStr, ...] = ()
    expected_effect: NonEmptyStr
    confidence: Confidence

    @field_validator("reasons")
    @classmethod
    def reasons_are_required(cls, reasons: tuple[str, ...]) -> tuple[str, ...]:
        if not reasons:
            raise ValueError("a revision record must explain why the position changed or remained")
        return reasons


class MinorityObjection(StrictModel):
    """A losing objection that remains material to the chosen strategy."""

    member_id: NonEmptyStr
    objection: NonEmptyStr
    decision_impact: NonEmptyStr
    reconsideration_trigger: NonEmptyStr


class Adjudication(StrictModel):
    """The Seneschal's strategic judgment before action authorization."""

    adjudication_id: str = Field(default_factory=_new_id)
    chosen_strategy: NonEmptyStr
    decisive_reasons: tuple[NonEmptyStr, ...]
    accepted_frames: tuple[NonEmptyStr, ...] = ()
    rejected_alternatives: dict[NonEmptyStr, NonEmptyStr] = Field(default_factory=dict)
    minority_objections: tuple[MinorityObjection, ...] = ()
    assumptions: tuple[NonEmptyStr, ...] = ()
    actions_requiring_authorization: tuple[NonEmptyStr, ...] = ()
    confidence: Confidence

    @field_validator("decisive_reasons")
    @classmethod
    def decisive_reasons_are_required(cls, reasons: tuple[str, ...]) -> tuple[str, ...]:
        if not reasons:
            raise ValueError("an adjudication requires decisive reasons")
        return reasons


class ActionStep(StrictModel):
    """One concrete step in the resulting actionable plan."""

    order: Annotated[int, Field(ge=1)]
    action: NonEmptyStr
    owner: str | None = None
    dependencies: tuple[NonEmptyStr, ...] = ()
    completion_signal: NonEmptyStr


class ActionablePlan(StrictModel):
    """The primary usable output of an Imperium deliberation."""

    decision: NonEmptyStr
    objective: NonEmptyStr
    immediate_next_action: NonEmptyStr
    steps: tuple[ActionStep, ...]
    checkpoints: tuple[NonEmptyStr, ...] = ()
    risks_and_mitigations: dict[NonEmptyStr, NonEmptyStr] = Field(default_factory=dict)
    assumptions: tuple[NonEmptyStr, ...] = ()
    decision_triggers: tuple[NonEmptyStr, ...] = ()
    stop_or_reconsideration_conditions: tuple[NonEmptyStr, ...]

    @field_validator("steps", "stop_or_reconsideration_conditions")
    @classmethod
    def require_plan_sections(cls, value: tuple[Any, ...]) -> tuple[Any, ...]:
        if not value:
            raise ValueError("an actionable plan requires steps and reconsideration conditions")
        return value

    @model_validator(mode="after")
    def validate_step_order(self) -> Self:
        orders = [step.order for step in self.steps]
        if len(orders) != len(set(orders)):
            raise ValueError("action step order values must be unique")
        if orders != sorted(orders):
            raise ValueError("action steps must be supplied in execution order")
        return self


class ArtifactReference(StrictModel):
    """A deliberately disclosed artifact in a stage-specific context."""

    artifact_id: NonEmptyStr
    artifact_type: NonEmptyStr
    owner_member_id: str | None = None
    payload: dict[str, Any]


class StageContext(StrictModel):
    """The complete and inspectable information boundary for one model call."""

    stage: DeliberationStage
    request: SovereignRequest
    member: SerializeAsAny[MemberProfile] | None = None
    shared_facts: tuple[NonEmptyStr, ...] = ()
    visible_artifacts: tuple[ArtifactReference, ...] = ()


class ModelCallRecord(StrictModel):
    """Provider-neutral usage and trace information for one model call."""

    call_id: str = Field(default_factory=_new_id)
    provider: NonEmptyStr
    model: NonEmptyStr
    stage: DeliberationStage
    member_id: str | None = None
    input_tokens: Annotated[int, Field(ge=0)] = 0
    output_tokens: Annotated[int, Field(ge=0)] = 0
    latency_ms: Annotated[int, Field(ge=0)] = 0
    retries: Annotated[int, Field(ge=0)] = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DeliberationRecord(StrictModel):
    """Authoritative, inspectable state for a complete or in-progress session."""

    session_id: str = Field(default_factory=_new_id)
    request: SovereignRequest
    member_snapshots: tuple[MemberProfile, ...] = ()
    selected_member_ids: tuple[NonEmptyStr, ...] = ()
    interpretations: tuple[Interpretation, ...] = ()
    frame_register: FrameRegister | None = None
    challenges: tuple[Challenge, ...] = ()
    challenge_responses: tuple[ChallengeResponse, ...] = ()
    evidence_requests: tuple[EvidenceRequest, ...] = ()
    evidence_resolutions: tuple[EvidenceResolution, ...] = ()
    proposals: tuple[StrategyProposal, ...] = ()
    revisions: tuple[Revision, ...] = ()
    minority_objections: tuple[MinorityObjection, ...] = ()
    adjudication: Adjudication | None = None
    plan: ActionablePlan | None = None
    model_calls: tuple[ModelCallRecord, ...] = ()
    stage: DeliberationStage = DeliberationStage.CREATED
    status: SessionStatus = SessionStatus.ACTIVE

    @model_validator(mode="after")
    def selected_members_must_have_snapshots(self) -> Self:
        available = {member.member_id for member in self.member_snapshots}
        missing = set(self.selected_member_ids) - available
        if missing:
            raise ValueError(f"selected members are missing profile snapshots: {sorted(missing)}")
        if self.stage is DeliberationStage.PLAN_COMPLETE and self.plan is None:
            raise ValueError("a completed plan stage requires an actionable plan")
        return self
