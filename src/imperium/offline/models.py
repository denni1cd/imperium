"""Validated contracts for the Stage 4 offline deliberation engine."""

from __future__ import annotations

from hashlib import sha256
from typing import Self

from pydantic import ConfigDict, Field, field_validator, model_validator

from imperium.domain.council import CouncilConfiguration
from imperium.domain.enums import (
    ArtifactKind,
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


def _text_digest(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


class FrozenTextArtifact(StrictModel):
    """Exact UTF-8 configuration or prompt content frozen for deterministic resume."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=False,
    )

    path: NonEmptyStr
    sha256: NonEmptyStr
    content: str

    @model_validator(mode="after")
    def validate_digest(self) -> Self:
        if self.sha256 != _text_digest(self.content):
            raise ValueError(f"frozen source digest does not match content for {self.path!r}")
        return self


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


def _scenario_digest(scenario: OfflineScenario) -> str:
    """Freeze scenario structure while permitting explicit evidence replacement on resume."""

    structural = scenario.model_copy(
        update={
            "frame_evidence_resolutions": (),
            "proposal_evidence_resolutions": (),
        }
    )
    return _text_digest(structural.model_dump_json())


class TurnTrace(StrictModel):
    """Inspectable record of one explicit provider invocation."""

    call_key: NonEmptyStr
    stage: DeliberationStage
    procedural_role: NonEmptyStr
    member_id: str | None = None
    prompt_path: NonEmptyStr
    prompt_sha256: NonEmptyStr
    visible_artifact_ids: tuple[NonEmptyStr, ...] = ()
    visible_artifact_kinds: tuple[NonEmptyStr, ...] = ()
    profile_member_id: str | None = None
    profile_sha256: str | None = None
    input_sha256: NonEmptyStr
    output_artifact_id: NonEmptyStr
    output_type: NonEmptyStr
    provider: NonEmptyStr
    model: NonEmptyStr

    @model_validator(mode="after")
    def validate_visible_artifact_metadata(self) -> Self:
        if self.visible_artifact_kinds and (
            len(self.visible_artifact_kinds) != len(self.visible_artifact_ids)
        ):
            raise ValueError("visible artifact IDs and kinds must have equal cardinality")
        return self


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
    scenario_sha256: str | None = None
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
        expected_scenario_digest = _scenario_digest(self.scenario)
        if self.scenario_sha256 is None:
            object.__setattr__(self, "scenario_sha256", expected_scenario_digest)
        elif self.scenario_sha256 != expected_scenario_digest:
            raise ValueError("frozen scenario digest does not match scenario content")
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
        call_ids = [call.call_id for call in self.record.model_calls]
        if len(set(call_ids)) != len(call_ids):
            raise ValueError("model call records must have unique call identifiers")
        if set(call_ids) != set(self.completed_call_keys):
            raise ValueError("model call records and completed call keys must match")
        if self.pending_call_key in set(self.completed_call_keys):
            raise ValueError("a completed call cannot remain pending")
        if self.record.status is SessionStatus.COMPLETE:
            if self.record.stage is not DeliberationStage.PLAN_COMPLETE:
                raise ValueError("complete sessions must be at plan_complete")

        self._validate_frozen_replay_artifacts()
        artifact_kinds = self._artifact_kind_index()
        profiles = {member.member_id: member for member in self.runtime.council.members}
        enriched: list[TurnTrace] = []
        for turn in self.turns:
            kinds = turn.visible_artifact_kinds or tuple(
                artifact_kinds.get(artifact_id, "unknown")
                for artifact_id in turn.visible_artifact_ids
            )
            profile_digest = turn.profile_sha256
            if profile_digest is None and turn.profile_member_id is not None:
                profile = profiles[turn.profile_member_id]
                profile_digest = _text_digest(profile.model_dump_json())
            enriched.append(
                turn.model_copy(
                    update={
                        "visible_artifact_kinds": kinds,
                        "profile_sha256": profile_digest,
                    }
                )
            )
        object.__setattr__(self, "turns", tuple(enriched))
        return self

    def _validate_frozen_replay_artifacts(self) -> None:
        """Reject checkpoints whose accepted replay outputs diverge from the frozen case."""

        if self.record.member_snapshots and (
            self.record.member_snapshots != self.runtime.council.members
        ):
            raise ValueError("member snapshots do not match the frozen council")
        if self.record.selected_member_ids and (
            self.record.selected_member_ids != self.runtime.council.advocate_member_ids
        ):
            raise ValueError("selected members do not match the frozen council")

        def require_expected(actual_items, expected_items, key, label: str) -> None:
            expected = {key(item): item for item in expected_items}
            for item in actual_items:
                identity = key(item)
                if identity not in expected or item != expected[identity]:
                    raise ValueError(
                        f"persisted {label} {identity!r} does not match the frozen scenario"
                    )

        require_expected(
            self.record.interpretations,
            self.scenario.interpretations,
            lambda item: item.member_id,
            "interpretation",
        )
        if self.record.frame_register is not None and (
            self.record.frame_register != self.scenario.frame_register
        ):
            raise ValueError("persisted frame register does not match the frozen scenario")
        require_expected(
            self.record.proposals,
            self.scenario.proposals,
            lambda item: item.member_id,
            "proposal",
        )
        require_expected(
            self.record.revisions,
            self.scenario.revisions,
            lambda item: item.member_id,
            "revision",
        )

        rounds = (*self.scenario.frame_rounds, *self.scenario.proposal_rounds)
        expected_snapshots = {
            (round_fixture.phase, round_fixture.claim_snapshot_round): round_fixture
            for round_fixture in rounds
        }
        for snapshot in self.protocol_trace.claim_register_snapshots:
            key = (snapshot.phase, snapshot.round_number)
            expected = expected_snapshots.get(key)
            if (
                expected is None
                or snapshot.claim_register != expected.claim_register
                or snapshot.supersedes_register_id != expected.supersedes_register_id
            ):
                raise ValueError(
                    f"persisted claim snapshot {key!r} does not match the frozen scenario"
                )
        require_expected(
            self.protocol_trace.challenge_plans,
            tuple(round_fixture.plan for round_fixture in rounds),
            lambda item: (item.phase, item.round_number),
            "challenge plan",
        )
        require_expected(
            self.protocol_trace.challenges,
            tuple(
                challenge
                for round_fixture in rounds
                for challenge in round_fixture.challenges
            ),
            lambda item: item.challenge_id,
            "challenge",
        )
        require_expected(
            self.record.challenge_responses,
            tuple(
                response
                for round_fixture in rounds
                for response in round_fixture.responses
            ),
            lambda item: item.challenge_id,
            "challenge response",
        )
        require_expected(
            self.protocol_trace.continuation_decisions,
            tuple(round_fixture.continuation for round_fixture in rounds),
            lambda item: (item.phase, item.completed_round),
            "continuation decision",
        )

        expected_requests = tuple(
            response.evidence_request
            for round_fixture in rounds
            for response in round_fixture.responses
            if response.evidence_request is not None
        )
        require_expected(
            self.record.evidence_requests,
            expected_requests,
            lambda item: item.evidence_request_id,
            "evidence request",
        )
        expected_resolutions = (
            *self.scenario.frame_evidence_resolutions,
            *self.scenario.proposal_evidence_resolutions,
        )
        require_expected(
            self.record.evidence_resolutions,
            expected_resolutions,
            lambda item: item.evidence_request_id,
            "evidence resolution",
        )

        if self.record.adjudication is not None and (
            self.record.adjudication != self.scenario.adjudication
        ):
            raise ValueError("persisted adjudication does not match the frozen scenario")
        if self.record.minority_objections and self.record.adjudication is not None and (
            self.record.minority_objections
            != self.record.adjudication.minority_objections
        ):
            raise ValueError("record minority objections must match adjudication")
        if self.record.plan is not None and self.record.plan != self.scenario.plan:
            raise ValueError("persisted actionable plan does not match the frozen scenario")

    def _artifact_kind_index(self) -> dict[str, str]:
        index: dict[str, str] = {"frame-register": ArtifactKind.FRAME_REGISTER.value}
        index.update(
            {
                item.interpretation_id: ArtifactKind.INTERPRETATION.value
                for item in self.record.interpretations
            }
        )
        index.update(
            {
                item.proposal_id: ArtifactKind.STRATEGY_PROPOSAL.value
                for item in self.record.proposals
            }
        )
        index.update(
            {
                item.revision_id: ArtifactKind.REVISION.value
                for item in self.record.revisions
            }
        )
        index.update(
            {
                item.challenge_id: ArtifactKind.CHALLENGE.value
                for item in self.protocol_trace.challenges
            }
        )
        index.update(
            {
                f"{item.challenge_id}:response": ArtifactKind.CHALLENGE_RESPONSE.value
                for item in self.record.challenge_responses
            }
        )
        index.update(
            {
                item.claim_register.register_id: ArtifactKind.CLAIM_REGISTER.value
                for item in self.protocol_trace.claim_register_snapshots
            }
        )
        index.update(
            {
                item.plan_id: ArtifactKind.CHALLENGE_PLAN.value
                for item in self.protocol_trace.challenge_plans
            }
        )
        index.update(
            {
                item.decision_id: ArtifactKind.CONTINUATION_DECISION.value
                for item in self.protocol_trace.continuation_decisions
            }
        )
        index.update(
            {
                f"{item.evidence_request_id}:resolution": ArtifactKind.EVIDENCE_RESOLUTION.value
                for item in self.record.evidence_resolutions
            }
        )
        if self.record.adjudication is not None:
            index[self.record.adjudication.adjudication_id] = ArtifactKind.ADJUDICATION.value
        if self.record.plan is not None:
            index["actionable-plan"] = ArtifactKind.ACTIONABLE_PLAN.value
        return index

    @property
    def status(self) -> SessionStatus:
        return self.record.status
