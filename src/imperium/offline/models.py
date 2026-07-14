"""Validated contracts for the Stage 4 offline deliberation engine."""

from __future__ import annotations

from typing import Self

from pydantic import Field, field_validator, model_validator

from imperium.domain.council import CouncilConfiguration
from imperium.domain.enums import (
    ChallengePhase,
    DeliberationStage,
    EvidenceOutcome,
    SessionStatus,
)
from imperium.domain.models import (
    ActionablePlan,
    Adjudication,
    ChallengeResponse,
    DeliberationRecord,
    EvidenceResolution,
    FrameRegister,
    Interpretation,
    NonEmptyStr,
    Revision,
    SovereignRequest,
    StrategyProposal,
    StrictModel,
)
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    ProtocolConfiguration,
)
from imperium.domain.protocol_trace import ProtocolTrace
from imperium.domain.vocabulary import ValueVocabulary
from imperium.engine.lifecycle import LifecycleState


class FrozenTextArtifact(StrictModel):
    """Exact UTF-8 configuration or prompt content frozen for deterministic resume."""

    path: NonEmptyStr
    sha256: NonEmptyStr
    content: str


class FrozenRuntime(StrictModel):
    """Complete immutable design inputs used by one offline session."""

    package_version: NonEmptyStr
    vocabulary: ValueVocabulary
    council: CouncilConfiguration
    protocol: ProtocolConfiguration
    sources: tuple[FrozenTextArtifact, ...]

    @model_validator(mode="after")
    def validate_versions(self) -> Self:
        if self.council.vocabulary_version != self.vocabulary.version:
            raise ValueError("frozen council and vocabulary versions must match")
        if self.protocol.vocabulary_version != self.vocabulary.version:
            raise ValueError("frozen protocol and vocabulary versions must match")
        if self.protocol.council_version != self.council.version:
            raise ValueError("frozen protocol and council versions must match")
        paths = [source.path for source in self.sources]
        if len(paths) != len(set(paths)):
            raise ValueError("frozen source paths must be unique")
        return self

    def source(self, path: str) -> FrozenTextArtifact:
        """Return one exact frozen source by repository-relative path."""

        try:
            return next(source for source in self.sources if source.path == path)
        except StopIteration as exc:
            raise KeyError(f"frozen runtime does not contain {path!r}") from exc


class DebateRoundFixture(StrictModel):
    """Scripted artifacts for one bounded frame or proposal debate round."""

    phase: ChallengePhase
    round_number: int = Field(ge=1)
    claim_register: ClaimRegister
    claim_snapshot_round: int = Field(ge=0)
    supersedes_register_id: str | None = None
    claims_with_new_input: tuple[NonEmptyStr, ...] = ()
    plan: ChallengePlan
    challenges: tuple[ChallengeArtifact, ...] = ()
    responses: tuple[ChallengeResponse, ...] = ()
    continuation: ContinuationDecision

    @model_validator(mode="after")
    def validate_round(self) -> Self:
        if self.claim_register.phase is not self.phase:
            raise ValueError("round claim register must match its challenge phase")
        if self.plan.phase is not self.phase or self.plan.round_number != self.round_number:
            raise ValueError("round challenge plan must match phase and round number")
        if (
            self.continuation.phase is not self.phase
            or self.continuation.completed_round != self.round_number
        ):
            raise ValueError("round continuation decision must match phase and round number")
        if self.claim_snapshot_round == 0 and self.supersedes_register_id is not None:
            raise ValueError("initial claim snapshots cannot supersede another register")
        if self.claim_snapshot_round > 0 and not self.supersedes_register_id:
            raise ValueError("later claim snapshots must identify the superseded register")
        if len(self.challenges) != len(self.plan.assignments):
            raise ValueError("fixture requires one authored challenge per assignment")
        if len(self.responses) != len(self.plan.assignments):
            raise ValueError("fixture requires one response per assignment")
        return self


class OfflineScenario(StrictModel):
    """All scripted reasoning artifacts for one deterministic offline session."""

    scenario_id: NonEmptyStr
    description: NonEmptyStr
    request: SovereignRequest
    interpretations: tuple[Interpretation, ...]
    frame_register: FrameRegister
    frame_rounds: tuple[DebateRoundFixture, ...]
    frame_evidence_resolutions: tuple[EvidenceResolution, ...] = ()
    proposals: tuple[StrategyProposal, ...]
    proposal_rounds: tuple[DebateRoundFixture, ...]
    proposal_evidence_resolutions: tuple[EvidenceResolution, ...] = ()
    revisions: tuple[Revision, ...]
    adjudication: Adjudication
    plan: ActionablePlan

    @field_validator("interpretations", "proposals", "revisions")
    @classmethod
    def require_advocate_outputs(cls, value: tuple[object, ...]) -> tuple[object, ...]:
        if not value:
            raise ValueError("offline scenarios require advocate outputs")
        return value

    @model_validator(mode="after")
    def validate_phases(self) -> Self:
        if not self.frame_rounds or any(
            round_fixture.phase is not ChallengePhase.FRAME
            for round_fixture in self.frame_rounds
        ):
            raise ValueError("offline scenarios require frame-phase round fixtures")
        if not self.proposal_rounds or any(
            round_fixture.phase is not ChallengePhase.PROPOSAL
            for round_fixture in self.proposal_rounds
        ):
            raise ValueError("offline scenarios require proposal-phase round fixtures")
        return self


class TurnTrace(StrictModel):
    """Inspectable record of one explicit provider invocation."""

    call_key: NonEmptyStr
    stage: DeliberationStage
    procedural_role: NonEmptyStr
    member_id: str | None = None
    prompt_path: NonEmptyStr
    prompt_sha256: NonEmptyStr
    visible_artifact_ids: tuple[NonEmptyStr, ...] = ()
    profile_member_id: str | None = None
    input_sha256: NonEmptyStr
    output_artifact_id: NonEmptyStr
    output_type: NonEmptyStr
    provider: NonEmptyStr
    model: NonEmptyStr


class EvidenceDispositionEvent(StrictModel):
    """Historical evidence outcome, including replacements during resume."""

    evidence_request_id: NonEmptyStr
    outcome: EvidenceOutcome
    replaced_outcome: EvidenceOutcome | None = None
    note: NonEmptyStr


class LineageLink(StrictModel):
    """One inspectable relationship between deliberation artifacts."""

    source_artifact_id: NonEmptyStr
    target_artifact_id: NonEmptyStr
    relationship: NonEmptyStr


class OfflineSession(StrictModel):
    """Authoritative resumable envelope for one Stage 4 run."""

    session_id: NonEmptyStr
    scenario: OfflineScenario
    runtime: FrozenRuntime
    record: DeliberationRecord
    protocol_trace: ProtocolTrace = Field(default_factory=ProtocolTrace)
    lifecycle_history: tuple[DeliberationStage, ...] = (DeliberationStage.CREATED,)
    turns: tuple[TurnTrace, ...] = ()
    completed_call_keys: tuple[NonEmptyStr, ...] = ()
    pending_call_key: str | None = None
    evidence_history: tuple[EvidenceDispositionEvent, ...] = ()
    lineage: tuple[LineageLink, ...] = ()
    checkpoint_sequence: int = Field(default=0, ge=0)
    failure_reason: str | None = None

    @model_validator(mode="after")
    def validate_session(self) -> Self:
        LifecycleState(stage=self.record.stage, history=self.lifecycle_history)
        if self.record.session_id != self.session_id:
            raise ValueError("offline session and deliberation record IDs must match")
        if self.record.request != self.scenario.request:
            raise ValueError("offline session record must preserve the scenario request")
        if len(set(self.completed_call_keys)) != len(self.completed_call_keys):
            raise ValueError("completed call keys must be unique")
        turn_keys = [turn.call_key for turn in self.turns]
        if len(set(turn_keys)) != len(turn_keys):
            raise ValueError("turn trace call keys must be unique")
        if set(turn_keys) != set(self.completed_call_keys):
            raise ValueError("turn trace and completed call keys must describe the same calls")
        if self.pending_call_key in set(self.completed_call_keys):
            raise ValueError("a completed call cannot remain pending")
        if self.record.status is SessionStatus.COMPLETE:
            if self.record.stage is not DeliberationStage.PLAN_COMPLETE:
                raise ValueError("complete sessions must be at plan_complete")
        return self

    @property
    def status(self) -> SessionStatus:
        return self.record.status
