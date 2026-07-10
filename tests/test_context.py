"""Tests ensuring council context is deliberately disclosed by stage."""

import pytest

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import ArtifactReference
from imperium.engine.context import ContextBuilder


def test_independent_interpretation_receives_no_council_artifacts(request, member) -> None:
    context = ContextBuilder.independent_interpretation(request, member)

    assert context.request.original_text == request.original_text
    assert context.member == member
    assert context.shared_facts == request.supplied_facts
    assert context.visible_artifacts == ()


def test_interpretation_boundary_rejects_visible_artifacts(request, member) -> None:
    artifact = ArtifactReference(
        artifact_id="other-interpretation",
        artifact_type="interpretation",
        owner_member_id="gazgul",
        payload={"core_decision": "Act before the opportunity closes."},
    )

    with pytest.raises(ValueError, match="cannot see council artifacts"):
        ContextBuilder.member_stage(
            stage=DeliberationStage.COUNCIL_SELECTED,
            request=request,
            member=member,
            visible_artifacts=(artifact,),
        )


def test_seneschal_cannot_synthesize_before_interpretation(request) -> None:
    with pytest.raises(ValueError, match="cannot receive council synthesis"):
        ContextBuilder.seneschal_stage(
            stage=DeliberationStage.COUNCIL_SELECTED,
            request=request,
            visible_artifacts=(),
        )


def test_later_member_stage_receives_only_explicit_artifacts(request, member) -> None:
    artifact = ArtifactReference(
        artifact_id="frame-register",
        artifact_type="frame_register",
        payload={"contested_frames": []},
    )
    context = ContextBuilder.member_stage(
        stage=DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        request=request,
        member=member,
        visible_artifacts=(artifact,),
    )

    assert context.visible_artifacts == (artifact,)
