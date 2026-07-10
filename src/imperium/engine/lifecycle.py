"""Deterministic state transitions for the minimum deliberation protocol."""

from __future__ import annotations

from dataclasses import dataclass

from imperium.domain.enums import DeliberationStage


class InvalidTransition(ValueError):
    """Raised when code attempts to skip or reverse a required stage."""


_NEXT_STAGE: dict[DeliberationStage, DeliberationStage] = {
    DeliberationStage.CREATED: DeliberationStage.REQUEST_PRESERVED,
    DeliberationStage.REQUEST_PRESERVED: DeliberationStage.COUNCIL_SELECTED,
    DeliberationStage.COUNCIL_SELECTED: DeliberationStage.INTERPRETATIONS_COMPLETE,
    DeliberationStage.INTERPRETATIONS_COMPLETE: DeliberationStage.FRAMES_COMPARED,
    DeliberationStage.FRAMES_COMPARED: DeliberationStage.FRAME_CHALLENGES_COMPLETE,
    DeliberationStage.FRAME_CHALLENGES_COMPLETE: DeliberationStage.EVIDENCE_RESOLVED,
    DeliberationStage.EVIDENCE_RESOLVED: DeliberationStage.STRATEGIES_COMPLETE,
    DeliberationStage.STRATEGIES_COMPLETE: DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
    DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE: DeliberationStage.REVISIONS_COMPLETE,
    DeliberationStage.REVISIONS_COMPLETE: DeliberationStage.ADJUDICATED,
    DeliberationStage.ADJUDICATED: DeliberationStage.PLAN_COMPLETE,
}


@dataclass(frozen=True, slots=True)
class LifecycleState:
    """Immutable current stage plus an audit trail of completed transitions."""

    stage: DeliberationStage = DeliberationStage.CREATED
    history: tuple[DeliberationStage, ...] = (DeliberationStage.CREATED,)

    @property
    def is_complete(self) -> bool:
        return self.stage is DeliberationStage.PLAN_COMPLETE

    @property
    def expected_next_stage(self) -> DeliberationStage | None:
        return _NEXT_STAGE.get(self.stage)

    def advance(self, next_stage: DeliberationStage) -> LifecycleState:
        expected = self.expected_next_stage
        if expected is None:
            raise InvalidTransition("the deliberation lifecycle is already complete")
        if next_stage is not expected:
            raise InvalidTransition(
                f"cannot transition from {self.stage.value} to {next_stage.value}; "
                f"expected {expected.value}"
            )
        return LifecycleState(stage=next_stage, history=(*self.history, next_stage))
