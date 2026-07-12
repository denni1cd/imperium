"""Shared enumerations for the controlled deliberation lifecycle."""

from enum import StrEnum


class DeliberationStage(StrEnum):
    """Ordered stages controlled by the Imperium engine."""

    CREATED = "created"
    REQUEST_PRESERVED = "request_preserved"
    COUNCIL_SELECTED = "council_selected"
    INTERPRETATIONS_COMPLETE = "interpretations_complete"
    FRAMES_COMPARED = "frames_compared"
    FRAME_CHALLENGES_COMPLETE = "frame_challenges_complete"
    EVIDENCE_RESOLVED = "evidence_resolved"
    STRATEGIES_COMPLETE = "strategies_complete"
    PROPOSAL_CHALLENGES_COMPLETE = "proposal_challenges_complete"
    PROPOSAL_EVIDENCE_RESOLVED = "proposal_evidence_resolved"
    REVISIONS_COMPLETE = "revisions_complete"
    ADJUDICATED = "adjudicated"
    PLAN_COMPLETE = "plan_complete"


class ChallengeDisposition(StrEnum):
    """Required consequence of a targeted challenge."""

    DEFEND = "defend"
    REFINE = "refine"
    CONCEDE = "concede"
    WITHDRAW = "withdraw"
    REQUEST_EVIDENCE = "request_evidence"


class ChallengePhase(StrEnum):
    """The two places where the minimum protocol permits targeted debate."""

    FRAME = "frame"
    PROPOSAL = "proposal"


class ClaimKind(StrEnum):
    """Normalized categories used to compare material strategic claims."""

    FACT = "fact"
    ASSUMPTION = "assumption"
    INTERPRETATION = "interpretation"
    VALUE_JUDGMENT = "value_judgment"
    FORECAST = "forecast"
    PROPOSED_ACTION = "proposed_action"
    TRADEOFF = "tradeoff"
    RISK = "risk"


class Materiality(StrEnum):
    """Expected effect of a claim or issue on the final strategic judgment."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProtocolActor(StrEnum):
    """Actor responsible for one protocol stage."""

    ENGINE = "engine"
    ADVOCATE = "advocate"
    SENESCHAL = "seneschal"


class ArtifactKind(StrEnum):
    """Typed artifacts that may cross an explicit stage boundary."""

    SOVEREIGN_REQUEST = "sovereign_request"
    COUNCIL_SNAPSHOT = "council_snapshot"
    INTERPRETATION = "interpretation"
    CLAIM_REGISTER = "claim_register"
    FRAME_REGISTER = "frame_register"
    CHALLENGE_PLAN = "challenge_plan"
    CHALLENGE = "challenge"
    CHALLENGE_RESPONSE = "challenge_response"
    EVIDENCE_REQUEST = "evidence_request"
    EVIDENCE_RESOLUTION = "evidence_resolution"
    STRATEGY_PROPOSAL = "strategy_proposal"
    REVISION = "revision"
    CONTINUATION_DECISION = "continuation_decision"
    ADJUDICATION = "adjudication"
    ACTIONABLE_PLAN = "actionable_plan"


class ContinuationReason(StrEnum):
    """Allowed reason for another debate round."""

    NEW_MATERIAL_FRAME = "new_material_frame"
    UNRESOLVED_MATERIAL_CLAIM = "unresolved_material_claim"
    DECISION_CRITICAL_EVIDENCE = "decision_critical_evidence"
    ADJUDICATION_MAY_CHANGE = "adjudication_may_change"


class StopReason(StrEnum):
    """Inspectable reason a debate phase ended or paused."""

    NO_MATERIAL_OPEN_ISSUES = "no_material_open_issues"
    REPEATED_WITHOUT_NEW_INPUT = "repeated_without_new_input"
    USER_CLARIFICATION_REQUIRED = "user_clarification_required"
    DELIBERATION_PAUSED = "deliberation_paused"
    ROUND_SAFETY_LIMIT = "round_safety_limit"
    PHASE_COMPLETE = "phase_complete"


class EvidenceOutcome(StrEnum):
    """Permitted resolution paths for a decision-critical evidence request."""

    GATHERED = "gathered"
    USER_CLARIFICATION_REQUIRED = "user_clarification_required"
    PROCEED_CONDITIONALLY = "proceed_conditionally"
    DELIBERATION_PAUSED = "deliberation_paused"


class SessionStatus(StrEnum):
    """High-level status of a deliberation session."""

    ACTIVE = "active"
    WAITING_FOR_USER = "waiting_for_user"
    PAUSED = "paused"
    COMPLETE = "complete"
    FAILED = "failed"


class AuthorityLevel(StrEnum):
    """Authority hierarchy defined by the accepted project decisions."""

    USER_HARD_CONSTRAINT = "user_hard_constraint"
    USER_OBJECTIVE = "user_objective"
    VERIFIED_FACT = "verified_fact"
    EXPLICIT_ASSUMPTION = "explicit_assumption"
    MEMBER_VALUE = "member_value"


class CouncilRole(StrEnum):
    """Procedural role of a configured council profile."""

    ADVOCATE = "advocate"
    SENESCHAL = "seneschal"
