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
