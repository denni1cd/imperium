"""Complete provider-neutral Stage 4 orchestration using deterministic replay artifacts."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from hashlib import sha256
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from imperium.domain.enums import (
    ArtifactKind,
    ChallengePhase,
    DeliberationStage,
    SessionStatus,
)
from imperium.domain.models import (
    Adjudication,
    ArtifactReference,
    ChallengeResponse,
    DeliberationRecord,
    EvidenceRequest,
    EvidenceResolution,
    FrameRegister,
    Interpretation,
    ModelCallRecord,
    Revision,
    StageContext,
    StrategyProposal,
)
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
)
from imperium.domain.protocol_trace import ClaimRegisterSnapshot, ProtocolTrace
from imperium.engine.context import ContextBuilder, artifact_reference
from imperium.engine.lifecycle import LifecycleState
from imperium.engine.protocol_rules import (
    evidence_session_status,
    validate_challenge_plan,
    validate_challenge_round_outputs,
    validate_continuation_decision,
    validate_evidence_resolutions,
    validate_stage_inputs,
    validate_stage_outputs,
)
from imperium.offline.models import (
    DebateRoundFixture,
    EvidenceDispositionEvent,
    LineageLink,
    OfflineScenario,
    OfflineSession,
    TurnTrace,
)
from imperium.offline.persistence import load_session, session_path, write_checkpoint, write_review_artifacts
from imperium.offline.runtime import freeze_runtime, text_sha256
from imperium.providers.base import CallMetadata
from imperium.providers.replay import ReplayProvider

OutputT = TypeVar("OutputT", bound=BaseModel)
ApplyArtifact = Callable[[OfflineSession, OutputT], OfflineSession]


class OfflineInterrupted(RuntimeError):
    """Raised after a requested committed call to prove checkpoint resume behavior."""

    def __init__(self, call_key: str, checkpoint: Path) -> None:
        super().__init__(f"offline run interrupted after {call_key}; checkpoint={checkpoint}")
        self.call_key = call_key
        self.checkpoint = checkpoint


def _replace_model(model: OutputT, **updates: object) -> OutputT:
    candidate = model.model_copy(update=updates)
    return type(model).model_validate(candidate.model_dump(mode="python"))


def _replace_session(session: OfflineSession, **updates: object) -> OfflineSession:
    candidate = session.model_copy(update=updates)
    return OfflineSession.model_validate(candidate.model_dump(mode="python"))


def _append_unique(
    items: Sequence[OutputT],
    item: OutputT,
    *,
    identity: Callable[[OutputT], str],
) -> tuple[OutputT, ...]:
    existing = {identity(value) for value in items}
    if identity(item) in existing:
        return tuple(items)
    return (*items, item)


def _artifact_id(artifact: BaseModel) -> str:
    for field in (
        "interpretation_id",
        "register_id",
        "plan_id",
        "challenge_id",
        "evidence_request_id",
        "proposal_id",
        "revision_id",
        "decision_id",
        "adjudication_id",
        "request_id",
    ):
        value = getattr(artifact, field, None)
        if value:
            if isinstance(artifact, ChallengeResponse):
                return f"{value}:response"
            if isinstance(artifact, EvidenceResolution):
                return f"{value}:resolution"
            return str(value)
    if isinstance(artifact, FrameRegister):
        return "frame-register"
    return type(artifact).__name__.replace("_", "-").lower()


def _call_key(
    *,
    resulting_stage: DeliberationStage,
    role: str,
    output_type: type[BaseModel],
    member_id: str | None = None,
    phase: ChallengePhase | None = None,
    round_number: int | None = None,
    subject: str | None = None,
) -> str:
    parts = [resulting_stage.value, role]
    if member_id:
        parts.append(member_id)
    if phase:
        parts.append(phase.value)
    if round_number is not None:
        parts.append(f"r{round_number}")
    if subject:
        parts.append(subject)
    parts.append(output_type.__name__)
    return ":".join(parts)


def _profile(session: OfflineSession, member_id: str):
    return next(member for member in session.runtime.council.members if member.member_id == member_id)


def _reference(
    artifact: BaseModel,
    kind: ArtifactKind,
    *,
    owner_member_id: str | None = None,
) -> ArtifactReference:
    return artifact_reference(
        artifact,
        artifact_id=_artifact_id(artifact),
        artifact_type=kind.value,
        owner_member_id=owner_member_id,
    )


def _source_reference(session: OfflineSession, artifact_id: str) -> ArtifactReference:
    for interpretation in session.record.interpretations:
        if interpretation.interpretation_id == artifact_id:
            return _reference(
                interpretation,
                ArtifactKind.INTERPRETATION,
                owner_member_id=interpretation.member_id,
            )
    for proposal in session.record.proposals:
        if proposal.proposal_id == artifact_id:
            return _reference(
                proposal,
                ArtifactKind.STRATEGY_PROPOSAL,
                owner_member_id=proposal.member_id,
            )
    raise ValueError(f"target source artifact is not present in the session: {artifact_id!r}")


def _validate_visible(
    *,
    label: str,
    allowed: Iterable[ArtifactKind],
    supplied: Iterable[ArtifactKind],
) -> None:
    unexpected = set(supplied) - set(allowed)
    if unexpected:
        raise ValueError(
            f"{label} received forbidden artifacts: "
            f"{sorted(kind.value for kind in unexpected)}"
        )


def _context_hash(context: StageContext) -> str:
    return sha256(context.model_dump_json().encode("utf-8")).hexdigest()


def _update_record(record: DeliberationRecord, **updates: object) -> DeliberationRecord:
    return _replace_model(record, **updates)


def _update_trace(trace: ProtocolTrace, **updates: object) -> ProtocolTrace:
    return _replace_model(trace, **updates)


class OfflineDeliberationEngine:
    """Execute every protocol 1.3 stage using scripted replay artifacts."""

    def __init__(self, *, model: str = "offline-replay") -> None:
        self.model = model

    async def run(
        self,
        scenario: OfflineScenario,
        *,
        project_root: str | Path,
        output_dir: str | Path,
        interrupt_after: str | None = None,
    ) -> OfflineSession:
        """Create and execute one new deterministic offline session."""

        runtime = freeze_runtime(project_root)
        if runtime.protocol.version != "1.3":
            raise ValueError(
                f"Stage 4 requires protocol 1.3; loaded {runtime.protocol.version!r}"
            )
        session_id = f"offline-{scenario.scenario_id}"
        record = DeliberationRecord(
            session_id=session_id,
            request=scenario.request,
        )
        session = OfflineSession(
            session_id=session_id,
            scenario=scenario,
            runtime=runtime,
            record=record,
        )
        write_checkpoint(session, output_dir)
        return await self._execute(
            session,
            output_dir=output_dir,
            interrupt_after=interrupt_after,
        )

    async def resume(
        self,
        checkpoint: str | Path,
        *,
        output_dir: str | Path | None = None,
        evidence_replacements: Iterable[EvidenceResolution] = (),
        interrupt_after: str | None = None,
    ) -> OfflineSession:
        """Resume a saved session using only its frozen runtime and scenario content."""

        source = Path(checkpoint)
        session = load_session(source)
        destination = Path(output_dir) if output_dir is not None else source.parent
        replacements = tuple(evidence_replacements)
        if replacements:
            session = self._replace_scenario_resolutions(session, replacements)
            record = _update_record(session.record, status=SessionStatus.ACTIVE)
            session = _replace_session(
                session,
                record=record,
                failure_reason=None,
                pending_call_key=None,
                checkpoint_sequence=session.checkpoint_sequence + 1,
            )
            write_checkpoint(session, destination)
        elif session.status in {SessionStatus.WAITING_FOR_USER, SessionStatus.PAUSED}:
            raise ValueError("waiting or paused sessions require explicit evidence replacements")
        return await self._execute(
            session,
            output_dir=destination,
            interrupt_after=interrupt_after,
        )

    async def _execute(
        self,
        session: OfflineSession,
        *,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        try:
            while session.status is SessionStatus.ACTIVE:
                stage = session.record.stage
                if stage is DeliberationStage.CREATED:
                    session = self._advance(session, DeliberationStage.REQUEST_PRESERVED, output_dir)
                elif stage is DeliberationStage.REQUEST_PRESERVED:
                    session = self._select_council(session, output_dir)
                elif stage is DeliberationStage.COUNCIL_SELECTED:
                    session = await self._interpret(
                        session, output_dir, interrupt_after
                    )
                elif stage is DeliberationStage.INTERPRETATIONS_COMPLETE:
                    session = await self._compare_frames(
                        session, output_dir, interrupt_after
                    )
                elif stage is DeliberationStage.FRAMES_COMPARED:
                    session = await self._challenge_phase(
                        session,
                        rounds=session.scenario.frame_rounds,
                        output_dir=output_dir,
                        interrupt_after=interrupt_after,
                    )
                elif stage is DeliberationStage.FRAME_CHALLENGES_COMPLETE:
                    session = self._resolve_evidence(
                        session,
                        phase=ChallengePhase.FRAME,
                        resolutions=session.scenario.frame_evidence_resolutions,
                        output_dir=output_dir,
                    )
                elif stage is DeliberationStage.EVIDENCE_RESOLVED:
                    session = await self._propose(session, output_dir, interrupt_after)
                elif stage is DeliberationStage.STRATEGIES_COMPLETE:
                    session = await self._challenge_phase(
                        session,
                        rounds=session.scenario.proposal_rounds,
                        output_dir=output_dir,
                        interrupt_after=interrupt_after,
                    )
                elif stage is DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE:
                    session = self._resolve_evidence(
                        session,
                        phase=ChallengePhase.PROPOSAL,
                        resolutions=session.scenario.proposal_evidence_resolutions,
                        output_dir=output_dir,
                    )
                elif stage is DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED:
                    session = await self._revise(session, output_dir, interrupt_after)
                elif stage is DeliberationStage.REVISIONS_COMPLETE:
                    session = await self._adjudicate(session, output_dir, interrupt_after)
                elif stage is DeliberationStage.ADJUDICATED:
                    session = await self._plan(session, output_dir, interrupt_after)
                else:
                    break
        except OfflineInterrupted:
            raise
        except Exception as exc:
            record = _update_record(session.record, status=SessionStatus.FAILED)
            session = _replace_session(
                session,
                record=record,
                failure_reason=f"{type(exc).__name__}: {exc}",
                pending_call_key=None,
                checkpoint_sequence=session.checkpoint_sequence + 1,
            )
            write_review_artifacts(session, output_dir)
            raise

        write_review_artifacts(session, output_dir)
        return session

    def _advance(
        self,
        session: OfflineSession,
        next_stage: DeliberationStage,
        output_dir: str | Path,
    ) -> OfflineSession:
        lifecycle = LifecycleState(
            stage=session.record.stage,
            history=session.lifecycle_history,
        ).advance(next_stage)
        status = (
            SessionStatus.COMPLETE
            if next_stage is DeliberationStage.PLAN_COMPLETE
            else session.record.status
        )
        record = _update_record(session.record, stage=next_stage, status=status)
        session = _replace_session(
            session,
            record=record,
            lifecycle_history=lifecycle.history,
            checkpoint_sequence=session.checkpoint_sequence + 1,
        )
        write_checkpoint(session, output_dir)
        return session

    def _select_council(
        self,
        session: OfflineSession,
        output_dir: str | Path,
    ) -> OfflineSession:
        record = _update_record(
            session.record,
            member_snapshots=session.runtime.council.members,
            selected_member_ids=session.runtime.council.advocate_member_ids,
        )
        session = _replace_session(session, record=record)
        return self._advance(session, DeliberationStage.COUNCIL_SELECTED, output_dir)

    async def _call(
        self,
        session: OfflineSession,
        *,
        expected: OutputT,
        resulting_stage: DeliberationStage,
        procedural_role: str,
        prompt_path: str,
        context: StageContext,
        apply: ApplyArtifact[OutputT],
        output_dir: str | Path,
        member_id: str | None = None,
        phase: ChallengePhase | None = None,
        round_number: int | None = None,
        subject: str | None = None,
        interrupt_after: str | None = None,
    ) -> tuple[OfflineSession, OutputT]:
        key = _call_key(
            resulting_stage=resulting_stage,
            role=procedural_role,
            output_type=type(expected),
            member_id=member_id,
            phase=phase,
            round_number=round_number,
            subject=subject,
        )
        if key in set(session.completed_call_keys):
            return session, expected

        if context.member is not None:
            if context.member.member_id != member_id:
                raise ValueError("advocate context must contain only the active member profile")
            if any(
                reference.artifact_type == ArtifactKind.COUNCIL_SNAPSHOT.value
                for reference in context.visible_artifacts
            ):
                raise ValueError("advocate context cannot expose the complete council registry")

        prompt = session.runtime.source(prompt_path)
        pending = _replace_session(
            session,
            pending_call_key=key,
            checkpoint_sequence=session.checkpoint_sequence + 1,
        )
        write_checkpoint(pending, output_dir)

        provider = ReplayProvider(
            {
                key: [
                    {
                        "output": expected.model_dump(mode="json"),
                        "provider": "stage4-replay",
                        "model": self.model,
                    }
                ]
            }
        )
        result = await provider.generate(
            model=self.model,
            instructions=prompt.content,
            input_text=context.model_dump_json(),
            output_type=type(expected),
            metadata=CallMetadata(
                session_id=session.session_id,
                call_key=key,
                stage=session.record.stage,
                member_id=member_id,
            ),
        )

        committed = apply(pending, result.output)
        call_record = ModelCallRecord(
            call_id=key,
            provider=result.provider,
            model=result.model,
            stage=session.record.stage,
            member_id=member_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )
        record = _update_record(
            committed.record,
            model_calls=_append_unique(
                committed.record.model_calls,
                call_record,
                identity=lambda item: item.call_id,
            ),
        )
        trace = TurnTrace(
            call_key=key,
            stage=session.record.stage,
            procedural_role=procedural_role,
            member_id=member_id,
            prompt_path=prompt.path,
            prompt_sha256=prompt.sha256,
            visible_artifact_ids=tuple(
                reference.artifact_id for reference in context.visible_artifacts
            ),
            profile_member_id=context.member.member_id if context.member else None,
            input_sha256=_context_hash(context),
            output_artifact_id=_artifact_id(result.output),
            output_type=type(result.output).__name__,
            provider=result.provider,
            model=result.model,
        )
        committed = _replace_session(
            committed,
            record=record,
            turns=(*committed.turns, trace),
            completed_call_keys=(*committed.completed_call_keys, key),
            pending_call_key=None,
            checkpoint_sequence=committed.checkpoint_sequence + 1,
        )
        checkpoint = write_checkpoint(committed, output_dir)
        if interrupt_after == key:
            raise OfflineInterrupted(key, checkpoint)
        return committed, result.output

    async def _interpret(
        self,
        session: OfflineSession,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        contract = session.runtime.protocol.contract_for(
            DeliberationStage.INTERPRETATIONS_COMPLETE
        )
        expected_by_member = {
            item.member_id: item for item in session.scenario.interpretations
        }
        if set(expected_by_member) != set(session.runtime.council.advocate_member_ids):
            raise ValueError("scenario must contain exactly one interpretation per advocate")

        for member in session.runtime.council.advocates:
            context = ContextBuilder.independent_interpretation(session.record.request, member)

            def apply(current: OfflineSession, output: Interpretation) -> OfflineSession:
                record = _update_record(
                    current.record,
                    interpretations=_append_unique(
                        current.record.interpretations,
                        output,
                        identity=lambda item: item.member_id,
                    ),
                )
                return _replace_session(current, record=record)

            session, _ = await self._call(
                session,
                expected=expected_by_member[member.member_id],
                resulting_stage=DeliberationStage.INTERPRETATIONS_COMPLETE,
                procedural_role="advocate",
                prompt_path=contract.prompt_template or "",
                context=context,
                apply=apply,
                output_dir=output_dir,
                member_id=member.member_id,
                interrupt_after=interrupt_after,
            )

        validate_stage_outputs(
            contract,
            tuple(ArtifactKind.INTERPRETATION for _ in session.record.interpretations),
        )
        return self._advance(
            session, DeliberationStage.INTERPRETATIONS_COMPLETE, output_dir
        )

    async def _compare_frames(
        self,
        session: OfflineSession,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        contract = session.runtime.protocol.contract_for(DeliberationStage.FRAMES_COMPARED)
        refs = tuple(
            _reference(
                interpretation,
                ArtifactKind.INTERPRETATION,
                owner_member_id=interpretation.member_id,
            )
            for interpretation in session.record.interpretations
        )
        validate_stage_inputs(
            contract,
            tuple(ArtifactKind.INTERPRETATION for _ in refs),
        )
        context = ContextBuilder.seneschal_stage(
            stage=session.record.stage,
            request=session.record.request,
            visible_artifacts=refs,
        )
        register = session.scenario.frame_rounds[0].claim_register

        def apply_claims(current: OfflineSession, output: ClaimRegister) -> OfflineSession:
            snapshot = ClaimRegisterSnapshot(
                phase=ChallengePhase.FRAME,
                round_number=0,
                claim_register=output,
            )
            trace = _update_trace(
                current.protocol_trace,
                claim_register_snapshots=_append_unique(
                    current.protocol_trace.claim_register_snapshots,
                    snapshot,
                    identity=lambda item: f"{item.phase.value}:{item.round_number}",
                ),
            )
            return _replace_session(current, protocol_trace=trace)

        session, _ = await self._call(
            session,
            expected=register,
            resulting_stage=DeliberationStage.FRAMES_COMPARED,
            procedural_role="seneschal",
            prompt_path=contract.prompt_template or "",
            context=context,
            apply=apply_claims,
            output_dir=output_dir,
            subject="claims",
            interrupt_after=interrupt_after,
        )

        def apply_frames(current: OfflineSession, output: FrameRegister) -> OfflineSession:
            return _replace_session(
                current,
                record=_update_record(current.record, frame_register=output),
            )

        session, _ = await self._call(
            session,
            expected=session.scenario.frame_register,
            resulting_stage=DeliberationStage.FRAMES_COMPARED,
            procedural_role="seneschal",
            prompt_path=contract.prompt_template or "",
            context=context,
            apply=apply_frames,
            output_dir=output_dir,
            subject="frames",
            interrupt_after=interrupt_after,
        )
        validate_stage_outputs(
            contract,
            (ArtifactKind.CLAIM_REGISTER, ArtifactKind.FRAME_REGISTER),
        )
        return self._advance(session, DeliberationStage.FRAMES_COMPARED, output_dir)

    async def _challenge_phase(
        self,
        session: OfflineSession,
        *,
        rounds: tuple[DebateRoundFixture, ...],
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        phase = rounds[0].phase
        resulting_stage = (
            DeliberationStage.FRAME_CHALLENGES_COMPLETE
            if phase is ChallengePhase.FRAME
            else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
        )
        contract = session.runtime.protocol.contract_for(resulting_stage)
        prior_plans: list[ChallengePlan] = []

        for index, fixture in enumerate(rounds):
            if fixture.round_number != index + 1:
                raise ValueError("debate round fixtures must be contiguous and begin at one")

            if phase is ChallengePhase.PROPOSAL or fixture.claim_snapshot_round > 0:
                base_refs = self._seneschal_debate_refs(session, phase)
                context = ContextBuilder.seneschal_stage(
                    stage=session.record.stage,
                    request=session.record.request,
                    visible_artifacts=base_refs,
                )

                def apply_register(
                    current: OfflineSession,
                    output: ClaimRegister,
                    fixture: DebateRoundFixture = fixture,
                ) -> OfflineSession:
                    snapshot = ClaimRegisterSnapshot(
                        phase=fixture.phase,
                        round_number=fixture.claim_snapshot_round,
                        claim_register=output,
                        supersedes_register_id=fixture.supersedes_register_id,
                    )
                    trace = _update_trace(
                        current.protocol_trace,
                        claim_register_snapshots=_append_unique(
                            current.protocol_trace.claim_register_snapshots,
                            snapshot,
                            identity=lambda item: f"{item.phase.value}:{item.round_number}",
                        ),
                    )
                    return _replace_session(current, protocol_trace=trace)

                session, _ = await self._call(
                    session,
                    expected=fixture.claim_register,
                    resulting_stage=resulting_stage,
                    procedural_role="seneschal",
                    prompt_path=contract.prompt_template or "",
                    context=context,
                    apply=apply_register,
                    output_dir=output_dir,
                    phase=phase,
                    round_number=fixture.round_number,
                    subject="claims",
                    interrupt_after=interrupt_after,
                )

            validate_challenge_plan(
                fixture.plan,
                claims=fixture.claim_register,
                council=session.runtime.council,
                policy=session.runtime.protocol.challenge_policy,
                prior_plans=tuple(prior_plans),
                claims_with_new_input=fixture.claims_with_new_input,
            )
            plan_context = ContextBuilder.seneschal_stage(
                stage=session.record.stage,
                request=session.record.request,
                visible_artifacts=self._seneschal_debate_refs(session, phase),
            )

            def apply_plan(current: OfflineSession, output: ChallengePlan) -> OfflineSession:
                trace = _update_trace(
                    current.protocol_trace,
                    challenge_plans=_append_unique(
                        current.protocol_trace.challenge_plans,
                        output,
                        identity=lambda item: f"{item.phase.value}:{item.round_number}",
                    ),
                )
                return _replace_session(current, protocol_trace=trace)

            session, _ = await self._call(
                session,
                expected=fixture.plan,
                resulting_stage=resulting_stage,
                procedural_role="seneschal",
                prompt_path=contract.prompt_template or "",
                context=plan_context,
                apply=apply_plan,
                output_dir=output_dir,
                phase=phase,
                round_number=fixture.round_number,
                subject="plan",
                interrupt_after=interrupt_after,
            )

            challenge_by_id = {item.challenge_id: item for item in fixture.challenges}
            response_by_id = {item.challenge_id: item for item in fixture.responses}
            for assignment in fixture.plan.assignments:
                challenge = challenge_by_id[assignment.challenge_id]
                source = _source_reference(session, assignment.target_artifact_id)
                claim_ref = _reference(fixture.claim_register, ArtifactKind.CLAIM_REGISTER)
                plan_ref = _reference(fixture.plan, ArtifactKind.CHALLENGE_PLAN)
                turn = contract.challenge_turns[0]
                supplied = (
                    ArtifactKind.CLAIM_REGISTER,
                    ArtifactKind.CHALLENGE_PLAN,
                    ArtifactKind(source.artifact_type),
                )
                _validate_visible(
                    label=turn.turn_id,
                    allowed=turn.allowed_input_artifacts,
                    supplied=supplied,
                )
                challenge_context = ContextBuilder.member_stage(
                    stage=session.record.stage,
                    request=session.record.request,
                    member=_profile(session, assignment.challenger_member_id),
                    visible_artifacts=(claim_ref, plan_ref, source),
                )

                def apply_challenge(
                    current: OfflineSession,
                    output: ChallengeArtifact,
                ) -> OfflineSession:
                    trace = _update_trace(
                        current.protocol_trace,
                        challenges=_append_unique(
                            current.protocol_trace.challenges,
                            output,
                            identity=lambda item: item.challenge_id,
                        ),
                    )
                    link = LineageLink(
                        source_artifact_id=output.target_claim_id,
                        target_artifact_id=output.challenge_id,
                        relationship="challenged_by",
                    )
                    return _replace_session(
                        current,
                        protocol_trace=trace,
                        lineage=_append_unique(
                            current.lineage,
                            link,
                            identity=lambda item: (
                                f"{item.source_artifact_id}:{item.target_artifact_id}:"
                                f"{item.relationship}"
                            ),
                        ),
                    )

                session, _ = await self._call(
                    session,
                    expected=challenge,
                    resulting_stage=resulting_stage,
                    procedural_role="challenger",
                    prompt_path=turn.prompt_template,
                    context=challenge_context,
                    apply=apply_challenge,
                    output_dir=output_dir,
                    member_id=assignment.challenger_member_id,
                    phase=phase,
                    round_number=fixture.round_number,
                    subject=assignment.challenge_id,
                    interrupt_after=interrupt_after,
                )

                response = response_by_id[assignment.challenge_id]
                response_turn = contract.challenge_turns[1]
                challenge_ref = _reference(challenge, ArtifactKind.CHALLENGE)
                supplied_response = (
                    ArtifactKind.CHALLENGE_PLAN,
                    ArtifactKind.CHALLENGE,
                    ArtifactKind(source.artifact_type),
                )
                _validate_visible(
                    label=response_turn.turn_id,
                    allowed=response_turn.allowed_input_artifacts,
                    supplied=supplied_response,
                )
                response_context = ContextBuilder.member_stage(
                    stage=session.record.stage,
                    request=session.record.request,
                    member=_profile(session, assignment.target_member_id),
                    visible_artifacts=(plan_ref, challenge_ref, source),
                )

                def apply_response(
                    current: OfflineSession,
                    output: ChallengeResponse,
                ) -> OfflineSession:
                    responses = _append_unique(
                        current.record.challenge_responses,
                        output,
                        identity=lambda item: item.challenge_id,
                    )
                    requests = current.record.evidence_requests
                    if output.evidence_request is not None:
                        requests = _append_unique(
                            requests,
                            output.evidence_request,
                            identity=lambda item: item.evidence_request_id,
                        )
                    record = _update_record(
                        current.record,
                        challenge_responses=responses,
                        evidence_requests=requests,
                    )
                    links = list(current.lineage)
                    links.append(
                        LineageLink(
                            source_artifact_id=output.challenge_id,
                            target_artifact_id=f"{output.challenge_id}:response",
                            relationship="answered_by",
                        )
                    )
                    if output.evidence_request is not None:
                        links.append(
                            LineageLink(
                                source_artifact_id=f"{output.challenge_id}:response",
                                target_artifact_id=output.evidence_request.evidence_request_id,
                                relationship="requested_evidence",
                            )
                        )
                    unique_links: list[LineageLink] = []
                    seen: set[str] = set()
                    for link in links:
                        key = (
                            f"{link.source_artifact_id}:{link.target_artifact_id}:"
                            f"{link.relationship}"
                        )
                        if key not in seen:
                            seen.add(key)
                            unique_links.append(link)
                    return _replace_session(
                        current,
                        record=record,
                        lineage=tuple(unique_links),
                    )

                session, _ = await self._call(
                    session,
                    expected=response,
                    resulting_stage=resulting_stage,
                    procedural_role="target",
                    prompt_path=response_turn.prompt_template,
                    context=response_context,
                    apply=apply_response,
                    output_dir=output_dir,
                    member_id=assignment.target_member_id,
                    phase=phase,
                    round_number=fixture.round_number,
                    subject=assignment.challenge_id,
                    interrupt_after=interrupt_after,
                )

            validate_challenge_round_outputs(
                fixture.plan,
                challenges=fixture.challenges,
                responses=fixture.responses,
            )
            validate_continuation_decision(
                fixture.continuation,
                claims=fixture.claim_register,
                policy=session.runtime.protocol.challenge_policy,
            )
            continuation_context = ContextBuilder.seneschal_stage(
                stage=session.record.stage,
                request=session.record.request,
                visible_artifacts=self._seneschal_debate_refs(session, phase),
            )

            def apply_continuation(
                current: OfflineSession,
                output: ContinuationDecision,
            ) -> OfflineSession:
                trace = _update_trace(
                    current.protocol_trace,
                    continuation_decisions=_append_unique(
                        current.protocol_trace.continuation_decisions,
                        output,
                        identity=lambda item: f"{item.phase.value}:{item.completed_round}",
                    ),
                )
                return _replace_session(current, protocol_trace=trace)

            session, _ = await self._call(
                session,
                expected=fixture.continuation,
                resulting_stage=resulting_stage,
                procedural_role="seneschal",
                prompt_path=contract.prompt_template or "",
                context=continuation_context,
                apply=apply_continuation,
                output_dir=output_dir,
                phase=phase,
                round_number=fixture.round_number,
                subject="continuation",
                interrupt_after=interrupt_after,
            )

            produced = []
            if phase is ChallengePhase.PROPOSAL or fixture.claim_snapshot_round > 0:
                produced.append(ArtifactKind.CLAIM_REGISTER)
            produced.extend(
                [
                    ArtifactKind.CHALLENGE_PLAN,
                    *(ArtifactKind.CHALLENGE for _ in fixture.challenges),
                    *(ArtifactKind.CHALLENGE_RESPONSE for _ in fixture.responses),
                    ArtifactKind.CONTINUATION_DECISION,
                ]
            )
            validate_stage_outputs(contract, tuple(produced))
            prior_plans.append(fixture.plan)

            if not fixture.continuation.continue_debate:
                if index != len(rounds) - 1:
                    raise ValueError("scenario contains rounds after a stopping decision")
                break
            if index == len(rounds) - 1:
                raise ValueError("continuation decision requires another scripted round")

        return self._advance(session, resulting_stage, output_dir)

    def _seneschal_debate_refs(
        self,
        session: OfflineSession,
        phase: ChallengePhase,
    ) -> tuple[ArtifactReference, ...]:
        refs: list[ArtifactReference] = []
        if session.record.frame_register is not None:
            refs.append(_reference(session.record.frame_register, ArtifactKind.FRAME_REGISTER))
        if phase is ChallengePhase.FRAME:
            refs.extend(
                _reference(
                    item,
                    ArtifactKind.INTERPRETATION,
                    owner_member_id=item.member_id,
                )
                for item in session.record.interpretations
            )
        else:
            refs.extend(
                _reference(
                    item,
                    ArtifactKind.STRATEGY_PROPOSAL,
                    owner_member_id=item.member_id,
                )
                for item in session.record.proposals
            )
            refs.extend(
                _reference(item, ArtifactKind.EVIDENCE_RESOLUTION)
                for item in session.record.evidence_resolutions
            )
        refs.extend(
            _reference(snapshot.claim_register, ArtifactKind.CLAIM_REGISTER)
            for snapshot in session.protocol_trace.claim_register_snapshots
            if snapshot.phase is phase
        )
        refs.extend(
            _reference(plan, ArtifactKind.CHALLENGE_PLAN)
            for plan in session.protocol_trace.challenge_plans
            if plan.phase is phase
        )
        refs.extend(
            _reference(challenge, ArtifactKind.CHALLENGE)
            for challenge in session.protocol_trace.challenges
            if challenge.phase is phase
        )
        return tuple(refs)

    def _phase_request_ids(
        self,
        rounds: tuple[DebateRoundFixture, ...],
    ) -> tuple[str, ...]:
        return tuple(
            response.evidence_request.evidence_request_id
            for round_fixture in rounds
            for response in round_fixture.responses
            if response.evidence_request is not None
        )

    def _resolve_evidence(
        self,
        session: OfflineSession,
        *,
        phase: ChallengePhase,
        resolutions: tuple[EvidenceResolution, ...],
        output_dir: str | Path,
    ) -> OfflineSession:
        resulting_stage = (
            DeliberationStage.EVIDENCE_RESOLVED
            if phase is ChallengePhase.FRAME
            else DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED
        )
        contract = session.runtime.protocol.contract_for(resulting_stage)
        rounds = (
            session.scenario.frame_rounds
            if phase is ChallengePhase.FRAME
            else session.scenario.proposal_rounds
        )
        request_ids = self._phase_request_ids(rounds)
        requests_by_id = {
            request.evidence_request_id: request for request in session.record.evidence_requests
        }
        requests = tuple(requests_by_id[request_id] for request_id in request_ids)
        validate_evidence_resolutions(requests, resolutions)
        validate_stage_inputs(
            contract,
            tuple(ArtifactKind.EVIDENCE_REQUEST for _ in requests),
        )
        validate_stage_outputs(
            contract,
            tuple(ArtifactKind.EVIDENCE_RESOLUTION for _ in resolutions),
            supplied_input_artifacts=tuple(
                ArtifactKind.EVIDENCE_REQUEST for _ in requests
            ),
        )

        current = {
            resolution.evidence_request_id: resolution
            for resolution in session.record.evidence_resolutions
        }
        history = list(session.evidence_history)
        links = list(session.lineage)
        for resolution in resolutions:
            previous = current.get(resolution.evidence_request_id)
            current[resolution.evidence_request_id] = resolution
            history.append(
                EvidenceDispositionEvent(
                    evidence_request_id=resolution.evidence_request_id,
                    outcome=resolution.outcome,
                    replaced_outcome=previous.outcome if previous else None,
                    note=(
                        "Replaced prior evidence disposition during explicit resume."
                        if previous
                        else "Recorded evidence disposition for the current stage."
                    ),
                )
            )
            links.append(
                LineageLink(
                    source_artifact_id=resolution.evidence_request_id,
                    target_artifact_id=f"{resolution.evidence_request_id}:resolution",
                    relationship="resolved_as",
                )
            )

        ordered_resolutions = tuple(
            current[request.evidence_request_id]
            for request in session.record.evidence_requests
            if request.evidence_request_id in current
        )
        stage_status = evidence_session_status(resolutions)
        record = _update_record(
            session.record,
            evidence_resolutions=ordered_resolutions,
            status=stage_status,
        )
        session = _replace_session(
            session,
            record=record,
            evidence_history=tuple(history),
            lineage=tuple(links),
            checkpoint_sequence=session.checkpoint_sequence + 1,
        )
        write_checkpoint(session, output_dir)
        if stage_status is not SessionStatus.ACTIVE:
            write_review_artifacts(session, output_dir)
            return session
        return self._advance(session, resulting_stage, output_dir)

    async def _propose(
        self,
        session: OfflineSession,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        contract = session.runtime.protocol.contract_for(DeliberationStage.STRATEGIES_COMPLETE)
        expected_by_member = {item.member_id: item for item in session.scenario.proposals}
        if set(expected_by_member) != set(session.runtime.council.advocate_member_ids):
            raise ValueError("scenario must contain exactly one proposal per advocate")
        visible = self._strategy_refs(session)
        validate_stage_inputs(
            contract,
            tuple(ArtifactKind(reference.artifact_type) for reference in visible),
        )
        for member in session.runtime.council.advocates:
            context = ContextBuilder.member_stage(
                stage=session.record.stage,
                request=session.record.request,
                member=member,
                visible_artifacts=visible,
            )

            def apply(current: OfflineSession, output: StrategyProposal) -> OfflineSession:
                record = _update_record(
                    current.record,
                    proposals=_append_unique(
                        current.record.proposals,
                        output,
                        identity=lambda item: item.member_id,
                    ),
                )
                return _replace_session(current, record=record)

            session, _ = await self._call(
                session,
                expected=expected_by_member[member.member_id],
                resulting_stage=DeliberationStage.STRATEGIES_COMPLETE,
                procedural_role="advocate",
                prompt_path=contract.prompt_template or "",
                context=context,
                apply=apply,
                output_dir=output_dir,
                member_id=member.member_id,
                interrupt_after=interrupt_after,
            )
        validate_stage_outputs(
            contract,
            tuple(ArtifactKind.STRATEGY_PROPOSAL for _ in session.record.proposals),
        )
        return self._advance(session, DeliberationStage.STRATEGIES_COMPLETE, output_dir)

    def _strategy_refs(self, session: OfflineSession) -> tuple[ArtifactReference, ...]:
        refs: list[ArtifactReference] = []
        if session.record.frame_register is not None:
            refs.append(_reference(session.record.frame_register, ArtifactKind.FRAME_REGISTER))
        refs.extend(
            _reference(snapshot.claim_register, ArtifactKind.CLAIM_REGISTER)
            for snapshot in session.protocol_trace.claim_register_snapshots
            if snapshot.phase is ChallengePhase.FRAME
        )
        refs.extend(
            _reference(plan, ArtifactKind.CHALLENGE_PLAN)
            for plan in session.protocol_trace.challenge_plans
            if plan.phase is ChallengePhase.FRAME
        )
        refs.extend(
            _reference(challenge, ArtifactKind.CHALLENGE)
            for challenge in session.protocol_trace.challenges
            if challenge.phase is ChallengePhase.FRAME
        )
        refs.extend(
            _reference(response, ArtifactKind.CHALLENGE_RESPONSE)
            for response in session.record.challenge_responses
            if response.challenge_id.startswith("frame-")
        )
        refs.extend(
            _reference(resolution, ArtifactKind.EVIDENCE_RESOLUTION)
            for resolution in session.record.evidence_resolutions
        )
        return tuple(refs)

    async def _revise(
        self,
        session: OfflineSession,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        contract = session.runtime.protocol.contract_for(DeliberationStage.REVISIONS_COMPLETE)
        expected_by_member = {item.member_id: item for item in session.scenario.revisions}
        if set(expected_by_member) != set(session.runtime.council.advocate_member_ids):
            raise ValueError("scenario must contain exactly one revision per advocate")
        visible = self._revision_refs(session)
        validate_stage_inputs(
            contract,
            tuple(ArtifactKind(reference.artifact_type) for reference in visible),
        )
        for member in session.runtime.council.advocates:
            context = ContextBuilder.member_stage(
                stage=session.record.stage,
                request=session.record.request,
                member=member,
                visible_artifacts=visible,
            )

            def apply(current: OfflineSession, output: Revision) -> OfflineSession:
                record = _update_record(
                    current.record,
                    revisions=_append_unique(
                        current.record.revisions,
                        output,
                        identity=lambda item: item.member_id,
                    ),
                )
                links = list(current.lineage)
                for reason in output.reasons:
                    del reason
                links.append(
                    LineageLink(
                        source_artifact_id=output.original_proposal_id,
                        target_artifact_id=output.revision_id,
                        relationship="revised_as",
                    )
                )
                return _replace_session(current, record=record, lineage=tuple(links))

            session, _ = await self._call(
                session,
                expected=expected_by_member[member.member_id],
                resulting_stage=DeliberationStage.REVISIONS_COMPLETE,
                procedural_role="advocate",
                prompt_path=contract.prompt_template or "",
                context=context,
                apply=apply,
                output_dir=output_dir,
                member_id=member.member_id,
                interrupt_after=interrupt_after,
            )
        validate_stage_outputs(
            contract,
            tuple(ArtifactKind.REVISION for _ in session.record.revisions),
        )
        return self._advance(session, DeliberationStage.REVISIONS_COMPLETE, output_dir)

    def _revision_refs(self, session: OfflineSession) -> tuple[ArtifactReference, ...]:
        refs: list[ArtifactReference] = []
        if session.record.frame_register is not None:
            refs.append(_reference(session.record.frame_register, ArtifactKind.FRAME_REGISTER))
        refs.extend(
            _reference(proposal, ArtifactKind.STRATEGY_PROPOSAL, owner_member_id=proposal.member_id)
            for proposal in session.record.proposals
        )
        refs.extend(
            _reference(snapshot.claim_register, ArtifactKind.CLAIM_REGISTER)
            for snapshot in session.protocol_trace.claim_register_snapshots
            if snapshot.phase is ChallengePhase.PROPOSAL
        )
        refs.extend(
            _reference(plan, ArtifactKind.CHALLENGE_PLAN)
            for plan in session.protocol_trace.challenge_plans
            if plan.phase is ChallengePhase.PROPOSAL
        )
        refs.extend(
            _reference(challenge, ArtifactKind.CHALLENGE)
            for challenge in session.protocol_trace.challenges
            if challenge.phase is ChallengePhase.PROPOSAL
        )
        refs.extend(
            _reference(response, ArtifactKind.CHALLENGE_RESPONSE)
            for response in session.record.challenge_responses
            if response.challenge_id.startswith("proposal-")
        )
        refs.extend(
            _reference(resolution, ArtifactKind.EVIDENCE_RESOLUTION)
            for resolution in session.record.evidence_resolutions
        )
        refs.extend(
            _reference(decision, ArtifactKind.CONTINUATION_DECISION)
            for decision in session.protocol_trace.continuation_decisions
        )
        return tuple(refs)

    async def _adjudicate(
        self,
        session: OfflineSession,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        contract = session.runtime.protocol.contract_for(DeliberationStage.ADJUDICATED)
        visible = tuple(
            [
                *(
                    _reference(item, ArtifactKind.INTERPRETATION, owner_member_id=item.member_id)
                    for item in session.record.interpretations
                ),
                *(
                    _reference(item, ArtifactKind.STRATEGY_PROPOSAL, owner_member_id=item.member_id)
                    for item in session.record.proposals
                ),
                *(
                    _reference(item, ArtifactKind.REVISION, owner_member_id=item.member_id)
                    for item in session.record.revisions
                ),
                *self._revision_refs(session),
            ]
        )
        context = ContextBuilder.seneschal_stage(
            stage=session.record.stage,
            request=session.record.request,
            visible_artifacts=visible,
        )

        def apply(current: OfflineSession, output: Adjudication) -> OfflineSession:
            record = _update_record(
                current.record,
                adjudication=output,
                minority_objections=output.minority_objections,
            )
            links = list(current.lineage)
            for revision in current.record.revisions:
                links.append(
                    LineageLink(
                        source_artifact_id=revision.revision_id,
                        target_artifact_id=output.adjudication_id,
                        relationship=(
                            "considered_in_adjudication"
                        ),
                    )
                )
            return _replace_session(current, record=record, lineage=tuple(links))

        session, _ = await self._call(
            session,
            expected=session.scenario.adjudication,
            resulting_stage=DeliberationStage.ADJUDICATED,
            procedural_role="seneschal",
            prompt_path=contract.prompt_template or "",
            context=context,
            apply=apply,
            output_dir=output_dir,
            interrupt_after=interrupt_after,
        )
        validate_stage_outputs(contract, (ArtifactKind.ADJUDICATION,))
        return self._advance(session, DeliberationStage.ADJUDICATED, output_dir)

    async def _plan(
        self,
        session: OfflineSession,
        output_dir: str | Path,
        interrupt_after: str | None,
    ) -> OfflineSession:
        contract = session.runtime.protocol.contract_for(DeliberationStage.PLAN_COMPLETE)
        visible = (
            _reference(session.record.adjudication, ArtifactKind.ADJUDICATION),
            *(
                _reference(item, ArtifactKind.REVISION, owner_member_id=item.member_id)
                for item in session.record.revisions
            ),
            *(
                _reference(item, ArtifactKind.EVIDENCE_RESOLUTION)
                for item in session.record.evidence_resolutions
            ),
        )
        context = ContextBuilder.seneschal_stage(
            stage=session.record.stage,
            request=session.record.request,
            visible_artifacts=visible,
        )

        def apply(current: OfflineSession, output):
            record = _update_record(current.record, plan=output)
            links = list(current.lineage)
            links.append(
                LineageLink(
                    source_artifact_id=current.record.adjudication.adjudication_id,
                    target_artifact_id="actionable-plan",
                    relationship="implemented_as_plan",
                )
            )
            return _replace_session(current, record=record, lineage=tuple(links))

        session, _ = await self._call(
            session,
            expected=session.scenario.plan,
            resulting_stage=DeliberationStage.PLAN_COMPLETE,
            procedural_role="seneschal",
            prompt_path=contract.prompt_template or "",
            context=context,
            apply=apply,
            output_dir=output_dir,
            interrupt_after=interrupt_after,
        )
        validate_stage_outputs(contract, (ArtifactKind.ACTIONABLE_PLAN,))
        return self._advance(session, DeliberationStage.PLAN_COMPLETE, output_dir)

    def _replace_scenario_resolutions(
        self,
        session: OfflineSession,
        replacements: tuple[EvidenceResolution, ...],
    ) -> OfflineSession:
        frame_ids = set(self._phase_request_ids(session.scenario.frame_rounds))
        proposal_ids = set(self._phase_request_ids(session.scenario.proposal_rounds))
        frame = {
            item.evidence_request_id: item
            for item in session.scenario.frame_evidence_resolutions
        }
        proposal = {
            item.evidence_request_id: item
            for item in session.scenario.proposal_evidence_resolutions
        }
        for replacement in replacements:
            request_id = replacement.evidence_request_id
            if request_id in frame_ids:
                frame[request_id] = replacement
            elif request_id in proposal_ids:
                proposal[request_id] = replacement
            else:
                raise ValueError(f"replacement references unknown evidence request {request_id!r}")
        scenario = _replace_model(
            session.scenario,
            frame_evidence_resolutions=tuple(
                frame[request_id] for request_id in self._phase_request_ids(session.scenario.frame_rounds)
            ),
            proposal_evidence_resolutions=tuple(
                proposal[request_id]
                for request_id in self._phase_request_ids(session.scenario.proposal_rounds)
            ),
        )
        return _replace_session(session, scenario=scenario)


def checkpoint_for(output_dir: str | Path) -> Path:
    """Return the authoritative checkpoint path for CLI and tests."""

    return session_path(output_dir)
