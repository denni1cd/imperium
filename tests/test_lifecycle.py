"""Tests for deterministic deliberation stage ordering."""

import pytest

from imperium.domain.enums import DeliberationStage
from imperium.engine.lifecycle import InvalidTransition, LifecycleState


def test_lifecycle_advances_in_defined_order() -> None:
    state = LifecycleState()
    expected = (
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

    for stage in expected:
        state = state.advance(stage)

    assert state.is_complete
    assert state.history == (DeliberationStage.CREATED, *expected)


def test_lifecycle_rejects_skipped_stage() -> None:
    state = LifecycleState()
    with pytest.raises(InvalidTransition, match="expected request_preserved"):
        state.advance(DeliberationStage.COUNCIL_SELECTED)


def test_completed_lifecycle_cannot_advance() -> None:
    state = LifecycleState(
        stage=DeliberationStage.PLAN_COMPLETE,
        history=(DeliberationStage.CREATED, DeliberationStage.PLAN_COMPLETE),
    )
    with pytest.raises(InvalidTransition, match="already complete"):
        state.advance(DeliberationStage.PLAN_COMPLETE)
