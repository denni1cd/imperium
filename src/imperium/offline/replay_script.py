"""Build one complete replay-provider script from a Stage 4 scenario.

Gate 2 requires provider outputs to become the sole downstream authority.  The
first safe step is to move scripted artifacts out of per-turn orchestration and
into one explicit ReplayProvider input.  This module preserves the existing
call-key contract without changing the Stage 4 engine yet.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from imperium.domain.enums import ChallengePhase, DeliberationStage
from imperium.offline.engine import _call_key
from imperium.offline.models import DebateRoundFixture, OfflineScenario

ReplayRecords = dict[str, list[dict[str, Any]]]


def _stage_for_phase(phase: ChallengePhase) -> DeliberationStage:
    return (
        DeliberationStage.FRAME_CHALLENGES_COMPLETE
        if phase is ChallengePhase.FRAME
        else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
    )


def _record(artifact: BaseModel, *, model: str) -> dict[str, Any]:
    return {
        "output": artifact.model_dump(mode="json"),
        "provider": "stage4-replay",
        "model": model,
    }


def build_replay_records(
    scenario: OfflineScenario,
    *,
    model: str = "offline-replay",
) -> ReplayRecords:
    """Return the complete stable call-key mapping for ``scenario``.

    Duplicate keys fail closed because a replay fixture must identify every
    model turn unambiguously.  Evidence resolutions are not provider turns and
    therefore are intentionally absent.
    """

    records: ReplayRecords = {}

    def add(
        artifact: BaseModel,
        *,
        stage: DeliberationStage,
        role: str,
        member_id: str | None = None,
        phase: ChallengePhase | None = None,
        round_number: int | None = None,
        subject: str | None = None,
    ) -> None:
        key = _call_key(
            resulting_stage=stage,
            role=role,
            output_type=type(artifact),
            member_id=member_id,
            phase=phase,
            round_number=round_number,
            subject=subject,
        )
        if key in records:
            raise ValueError(f"duplicate replay call key: {key}")
        records[key] = [_record(artifact, model=model)]

    for interpretation in scenario.interpretations:
        add(
            interpretation,
            stage=DeliberationStage.INTERPRETATIONS_COMPLETE,
            role="advocate",
            member_id=interpretation.member_id,
        )

    if not scenario.frame_rounds:
        raise ValueError("a replay scenario requires at least one frame debate round")
    add(
        scenario.frame_rounds[0].claim_register,
        stage=DeliberationStage.FRAMES_COMPARED,
        role="seneschal",
        subject="claims",
    )
    add(
        scenario.frame_register,
        stage=DeliberationStage.FRAMES_COMPARED,
        role="seneschal",
        subject="frames",
    )

    def add_round(fixture: DebateRoundFixture) -> None:
        stage = _stage_for_phase(fixture.phase)
        if fixture.phase is ChallengePhase.PROPOSAL or fixture.claim_snapshot_round > 0:
            add(
                fixture.claim_register,
                stage=stage,
                role="seneschal",
                phase=fixture.phase,
                round_number=fixture.round_number,
                subject="claims",
            )
        add(
            fixture.plan,
            stage=stage,
            role="seneschal",
            phase=fixture.phase,
            round_number=fixture.round_number,
            subject="plan",
        )

        challenges = {item.challenge_id: item for item in fixture.challenges}
        responses = {item.challenge_id: item for item in fixture.responses}
        for assignment in fixture.plan.assignments:
            try:
                challenge = challenges[assignment.challenge_id]
                response = responses[assignment.challenge_id]
            except KeyError as exc:
                raise ValueError(
                    f"replay round is missing exchange {assignment.challenge_id!r}"
                ) from exc
            add(
                challenge,
                stage=stage,
                role="challenger",
                member_id=assignment.challenger_member_id,
                phase=fixture.phase,
                round_number=fixture.round_number,
                subject=assignment.challenge_id,
            )
            add(
                response,
                stage=stage,
                role="target",
                member_id=assignment.target_member_id,
                phase=fixture.phase,
                round_number=fixture.round_number,
                subject=assignment.challenge_id,
            )

        add(
            fixture.continuation,
            stage=stage,
            role="seneschal",
            phase=fixture.phase,
            round_number=fixture.round_number,
            subject="continuation",
        )

    for fixture in scenario.frame_rounds:
        add_round(fixture)

    for proposal in scenario.proposals:
        add(
            proposal,
            stage=DeliberationStage.STRATEGIES_COMPLETE,
            role="advocate",
            member_id=proposal.member_id,
        )

    for fixture in scenario.proposal_rounds:
        add_round(fixture)

    for revision in scenario.revisions:
        add(
            revision,
            stage=DeliberationStage.REVISIONS_COMPLETE,
            role="advocate",
            member_id=revision.member_id,
        )

    add(
        scenario.adjudication,
        stage=DeliberationStage.ADJUDICATED,
        role="seneschal",
    )
    add(
        scenario.plan,
        stage=DeliberationStage.PLAN_COMPLETE,
        role="seneschal",
    )
    return records
