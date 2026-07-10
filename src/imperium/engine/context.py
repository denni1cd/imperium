"""Construct the exact information visible to each deliberation call."""

from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import (
    ArtifactReference,
    MemberProfile,
    SovereignRequest,
    StageContext,
)


class ContextBuilder:
    """Creates explicit contexts instead of passing an accumulated chat transcript."""

    @staticmethod
    def independent_interpretation(
        request: SovereignRequest,
        member: MemberProfile,
    ) -> StageContext:
        """Give a member only the preserved request, supplied facts, and its own profile."""
        return StageContext(
            stage=DeliberationStage.COUNCIL_SELECTED,
            request=request,
            member=member,
            shared_facts=request.supplied_facts,
            visible_artifacts=(),
        )

    @staticmethod
    def member_stage(
        *,
        stage: DeliberationStage,
        request: SovereignRequest,
        member: MemberProfile,
        visible_artifacts: Iterable[ArtifactReference] = (),
        shared_facts: Iterable[str] | None = None,
    ) -> StageContext:
        artifacts = tuple(visible_artifacts)
        if stage is DeliberationStage.COUNCIL_SELECTED and artifacts:
            raise ValueError("independent interpretation cannot see council artifacts")
        return StageContext(
            stage=stage,
            request=request,
            member=member,
            shared_facts=tuple(shared_facts if shared_facts is not None else request.supplied_facts),
            visible_artifacts=artifacts,
        )

    @staticmethod
    def seneschal_stage(
        *,
        stage: DeliberationStage,
        request: SovereignRequest,
        visible_artifacts: Iterable[ArtifactReference],
        shared_facts: Iterable[str] | None = None,
    ) -> StageContext:
        if stage in {
            DeliberationStage.CREATED,
            DeliberationStage.REQUEST_PRESERVED,
            DeliberationStage.COUNCIL_SELECTED,
        }:
            raise ValueError("the Seneschal cannot receive council synthesis before interpretation")
        return StageContext(
            stage=stage,
            request=request,
            member=None,
            shared_facts=tuple(shared_facts if shared_facts is not None else request.supplied_facts),
            visible_artifacts=tuple(visible_artifacts),
        )


def artifact_reference(
    artifact: BaseModel,
    *,
    artifact_id: str,
    artifact_type: str,
    owner_member_id: str | None = None,
) -> ArtifactReference:
    """Convert a validated domain artifact into an explicitly disclosed reference."""
    return ArtifactReference(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        owner_member_id=owner_member_id,
        payload=artifact.model_dump(mode="json"),
    )
