"""Stage 4 contracts for resumable offline deliberation and direct debate."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Self

from pydantic import Field, field_validator, model_validator

from imperium.domain.enums import ChallengeDisposition, ChallengePhase, DeliberationStage
from imperium.domain.models import (
    Challenge,
    ChallengeResponse,
    DeliberationRecord,
    FrameRegister,
    NonEmptyStr,
    Revision,
    StrategyProposal,
    StrictModel,
)
from imperium.domain.protocol import ChallengeAssignment, ClaimRegister
from imperium.domain.protocol_trace import ProtocolTrace


class FrameComparisonOutput(StrictModel):
    """Seneschal output that compares blind frames without deciding strategy."""

    claim_register: ClaimRegister
    frame_register: FrameRegister

    @model_validator(mode="after")
    def require_frame_phase(self) -> Self:
        if self.claim_register.phase is not ChallengePhase.FRAME:
            raise ValueError("frame comparison must produce a frame-phase claim register")
        return self


class DebateExchange(StrictModel):
    """One direct challenger-to-target confrontation and the target's response."""

    phase: ChallengePhase
    round_number: int = Field(ge=1)
    assignment: ChallengeAssignment
    challenge: Challenge
    response: ChallengeResponse

    @model_validator(mode="after")
    def validate_direct_exchange(self) -> Self:
        if self.assignment.phase is not self.phase:
            raise ValueError("debate exchange phase must match its challenge assignment")
        if self.assignment.round_number != self.round_number:
            raise ValueError("debate exchange round must match its challenge assignment")
        if self.challenge.challenge_id != self.assignment.challenge_id:
            raise ValueError("the articulated challenge must use the assigned challenge identifier")
        if self.challenge.challenger_member_id != self.assignment.challenger_member_id:
            raise ValueError("the assigned challenger must articulate the challenge directly")
        if self.challenge.target_member_id != self.assignment.target_member_id:
            raise ValueError("the articulated challenge must address the assigned target")
        if self.challenge.target_artifact_id != self.assignment.target_artifact_id:
            raise ValueError("the articulated challenge must address the assigned artifact")
        if self.response.challenge_id != self.challenge.challenge_id:
            raise ValueError("the target response must answer the direct challenge identifier")
        if self.response.member_id != self.assignment.target_member_id:
            raise ValueError("the challenged member must answer its own direct challenge")
        return self

    @property
    def exchange_id(self) -> str:
        """Use the assigned challenge identifier as the durable exchange identity."""

        return self.assignment.challenge_id


class DebateImpact(StrictModel):
    """Traceable effect of a direct exchange on a later strategic artifact."""

    exchange_id: NonEmptyStr
    member_id: NonEmptyStr
    resulting_artifact_id: NonEmptyStr
    disposition: ChallengeDisposition
    explanation: NonEmptyStr
    position_changed: bool = False
    reasoning_strengthened: bool = False
    uncertainty_clarified: bool = False

    @model_validator(mode="after")
    def require_consequence(self) -> Self:
        if not (
            self.position_changed
            or self.reasoning_strengthened
            or self.uncertainty_clarified
        ):
            raise ValueError(
                "a debate impact must change the position, strengthen its reasoning, "
                "or clarify material uncertainty"
            )
        if self.disposition in {
            ChallengeDisposition.REFINE,
            ChallengeDisposition.CONCEDE,
            ChallengeDisposition.WITHDRAW,
        } and not self.position_changed:
            raise ValueError("refinement, concession, and withdrawal must record position change")
        if self.disposition is ChallengeDisposition.REQUEST_EVIDENCE and not self.uncertainty_clarified:
            raise ValueError("an evidence request must record clarification of uncertainty")
        return self


class StrategyDevelopmentOutput(StrictModel):
    """An advocate proposal plus explicit effects from frame confrontation."""

    proposal: StrategyProposal
    debate_impacts: tuple[DebateImpact, ...] = ()

    @model_validator(mode="after")
    def impacts_belong_to_proposal(self) -> Self:
        for impact in self.debate_impacts:
            if impact.member_id != self.proposal.member_id:
                raise ValueError("strategy debate impacts must belong to the proposing advocate")
            if impact.resulting_artifact_id != self.proposal.proposal_id:
                raise ValueError("strategy debate impacts must identify the resulting proposal")
        return self


class RevisionOutput(StrictModel):
    """An advocate revision plus explicit effects from proposal confrontation."""

    revision: Revision
    debate_impacts: tuple[DebateImpact, ...] = ()

    @model_validator(mode="after")
    def impacts_belong_to_revision(self) -> Self:
        for impact in self.debate_impacts:
            if impact.member_id != self.revision.member_id:
                raise ValueError("revision debate impacts must belong to the revising advocate")
            if impact.resulting_artifact_id != self.revision.revision_id:
                raise ValueError("revision debate impacts must identify the resulting revision")
        return self


class StageCheckpoint(StrictModel):
    """Atomic stage completion record used for inspection and resume."""

    stage_id: NonEmptyStr
    resulting_stage: DeliberationStage
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provider_call_keys: tuple[NonEmptyStr, ...] = ()


class OfflineDeliberationSession(StrictModel):
    """Authoritative Stage 4 envelope for a complete or resumable offline run."""

    record: DeliberationRecord
    protocol_trace: ProtocolTrace = Field(default_factory=ProtocolTrace)
    lifecycle_history: tuple[DeliberationStage, ...] = (DeliberationStage.CREATED,)
    debate_exchanges: tuple[DebateExchange, ...] = ()
    debate_impacts: tuple[DebateImpact, ...] = ()
    checkpoints: tuple[StageCheckpoint, ...] = ()

    @field_validator("lifecycle_history")
    @classmethod
    def require_lifecycle_history(
        cls, history: tuple[DeliberationStage, ...]
    ) -> tuple[DeliberationStage, ...]:
        if not history or history[0] is not DeliberationStage.CREATED:
            raise ValueError("offline lifecycle history must begin at created")
        return history

    @model_validator(mode="after")
    def validate_session_links(self) -> Self:
        if self.lifecycle_history[-1] is not self.record.stage:
            raise ValueError("offline lifecycle history must end at the record's current stage")

        exchange_ids = [exchange.exchange_id for exchange in self.debate_exchanges]
        if len(set(exchange_ids)) != len(exchange_ids):
            raise ValueError("direct debate exchange identifiers must be unique")
        exchange_by_id = {exchange.exchange_id: exchange for exchange in self.debate_exchanges}

        impact_keys: list[tuple[str, str, str]] = []
        for impact in self.debate_impacts:
            exchange = exchange_by_id.get(impact.exchange_id)
            if exchange is None:
                raise ValueError(
                    f"debate impact references unknown exchange: {impact.exchange_id!r}"
                )
            if impact.member_id != exchange.assignment.target_member_id:
                raise ValueError("only the directly challenged member may claim an exchange impact")
            if impact.disposition is not exchange.response.disposition:
                raise ValueError("debate impact disposition must match the target response")
            impact_keys.append(
                (impact.exchange_id, impact.member_id, impact.resulting_artifact_id)
            )
        if len(set(impact_keys)) != len(impact_keys):
            raise ValueError("debate impact links must be unique")

        checkpoint_stages = [checkpoint.resulting_stage for checkpoint in self.checkpoints]
        if len(set(checkpoint_stages)) != len(checkpoint_stages):
            raise ValueError("each lifecycle stage may have only one completed checkpoint")
        return self
