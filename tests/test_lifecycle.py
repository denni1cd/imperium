"""Tests for deterministic deliberation stage ordering."""

import pytest

from imperium.domain.enums import DeliberationStage
from imperium.engine.lifecycle import InvalidTransition, LifecycleState


EXPECTED_STAGES = (
    DeliberationStage.REQUEST_PRESERVED,
    DeliberationStage.COUNCIL_SELECTED,
    DeliberationStage.INTERPRETATIONS_COMPLETE,
    DeliberationStage.FRAMES_COMPARED,
    DeliberationStage.FRAME_CHALLENGES_COMPLETE,
    DeliberationStage.EVIDENCE_RESOLVED,
    DeliberationStage.STRATEGIES_COMPLETE,
    DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
    DeliberationStage.REVISIONS_COMPLETE,
    DeliberationStage.ADJUDICATED,
    DeliberationStage.PLAN_COMPLETE,
)


def complete_lifecycle() -> LifecycleState:
    state = LifecycleState()
    for stage in EXPECTED_STAGES:
        state = state.advance(stage)
    return state


def test_lifecycle_advances_in_defined_order() -> None:
    state = complete_lifecycle()

    assert state.is_complete
    assert state.history == (DeliberationStage.CREATED, *EXPECTED_STAGES)


def test_lifecycle_rejects_skipped_stage() -> None:
    state = LifecycleState()
    with pytest.raises(InvalidTransition, match="expected request_preserved"):
        state.advance(DeliberationStage.COUNCIL_SELECTED)


def test_lifecycle_rejects_fabricated_history() -> None:
    with pytest.raises(InvalidTransition, match="invalid lifecycle history transition"):
        LifecycleState(
            stage=DeliberationStage.COUNCIL_SELECTED,
            history=(DeliberationStage.CREATED, DeliberationStage.COUNCIL_SELECTED),
        )


def test_lifecycle_rejects_history_that_disagrees_with_stage() -> None:
    with pytest.raises(InvalidTransition, match="end at the current stage"):
        LifecycleState(
            stage=DeliberationStage.REQUEST_PRESERVED,
            history=(DeliberationStage.CREATED,),
        )


def test_completed_lifecycle_cannot_advance() -> None:
    state = complete_lifecycle()
    with pytest.raises(InvalidTransition, match="already complete"):
        state.advance(DeliberationStage.PLAN_COMPLETE)
