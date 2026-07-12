"""Resumable Stage 4 engine with direct multi-turn council confrontation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from imperium.domain.council import CouncilConfiguration, CouncilMemberProfile
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
    Challenge,
    ChallengeResponse,
    DeliberationRecord,
    EvidenceRequest,
    EvidenceResolution,
    Interpretation,
    ModelCallRecord,
    SovereignRequest,
)
from imperium.domain.offline import (
    DebateExchange,
    DebateImpact,
    FrameComparisonOutput,
    OfflineDeliberationSession,
    RevisionOutput,
    StageCheckpoint,
    StrategyDevelopmentOutput,
)
from imperium.domain.protocol import (
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    ProtocolConfiguration,
)
from imperium.domain.protocol_trace import ClaimRegisterSnapshot, ProtocolTrace
from imperium.engine.debate_verification import require_actual_debate
from imperium.engine.lifecycle import LifecycleState
from imperium.engine.protocol_rules import (
    validate_challenge_plan,
    validate_continuation_decision,
    validate_stage_inputs,
    validate_stage_outputs,
)
from imperium.engine.record_validation import validate_deliberation_record
from imperium.providers.base import CallMetadata, ModelProvider, ModelResult

OutputT = TypeVar("OutputT", bound=BaseModel)


class EvidenceResolver(Protocol):
    """Provider-independent resolution for engine-owned evidence stages."""

    async def resolve(self, request: EvidenceRequest) -> EvidenceResolution:
        """Resolve one request through an approved evidence outcome."""


class StaticEvidenceResolver:
    """Deterministic evidence resolver for offline and replay tests."""

    def __init__(self, resolutions: Mapping[str, EvidenceResolution] | None = None) -> None:
        self._resolutions = dict(resolutions or {})

    async def resolve(self, request: EvidenceRequest) -> EvidenceResolution:
        resolution = self._resolutions.get(request.evidence_request_id)
        if resolution is None:
            raise ValueError(
                "no offline evidence resolution is configured for "
                f"{request.evidence_request_id!r}"
            )
        return resolution


class OfflineEngineError(RuntimeError):
    """Raised when the offline engine cannot preserve the approved protocol."""


class OfflineDeliberationEngine:
    """Execute the complete protocol without Codex or paid API calls.

    Debate phases are intentionally multi-call. The Seneschal selects bounded targets,
    each challenger articulates its own challenge, each target answers directly, and
    the target later records the consequence in its proposal or revision.
    """

    def __init__(
        self,
        *,
        council: CouncilConfiguration,
        protocol: ProtocolConfiguration,
        provider: ModelProvider,
        evidence_resolver: EvidenceResolver | None = None,
        model: str = "offline-replay",
        prompt_root: str | Path = ".",
    ) -> None:
        self.council = council
        self.protocol = protocol
        self.provider = provider
        self.evidence_resolver = evidence_resolver or StaticEvidenceResolver()
        self.model = model
        self.prompt_root = Path(prompt_root)
        if protocol.council_version != council.version:
            raise ValueError("protocol and council versions must match")

    def new_session(self, request: SovereignRequest) -> OfflineDeliberationSession:
        """Create a preserved, resumable session before any council exposure."""

        return OfflineDeliberationSession(record=DeliberationRecord(request=request))

    async def run(
        self,
        session: OfflineDeliberationSession,
        *,
        stop_after: DeliberationStage | None = None,
        checkpoint_path: str | Path | None = None,
    ) -> OfflineDeliberationSession:
        """Advance from the current stage until completion or a requested checkpoint."""

        while session.record.stage is not DeliberationStage.PLAN_COMPLETE:
            if session.record.status in {SessionStatus.WAITING_FOR_USER, SessionStatus.PAUSED}:
                return session
            next_stage = LifecycleState(
                stage=session.record.stage,
                history=session.lifecycle_history,
            ).expected_next_stage
            if next_stage is None:
                raise OfflineEngineError("offline lifecycle has no next stage")
            session = await self._run_stage(session, next_stage)
            if checkpoint_path is not None:
                from imperium.persistence.offline import export_offline_session

                export_offline_session(session, checkpoint_path)
            if stop_after is next_stage:
                return session

        require_actual_debate(session, require_both_phases=True)
        validate_deliberation_record(session.record)
        return session

    async def _run_stage(
        self,
        session: OfflineDeliberationSession,
        stage: DeliberationStage,
    ) -> OfflineDeliberationSession:
        before_calls = len(session.record.model_calls)
        dispatch = {
            DeliberationStage.REQUEST_PRESERVED: self._preserve_request,
            DeliberationStage.COUNCIL_SELECTED: self._select_council,
            DeliberationStage.INTERPRETATIONS_COMPLETE: self._interpret,
            DeliberationStage.FRAMES_COMPARED: self._compare_frames,
            DeliberationStage.FRAME_CHALLENGES_COMPLETE: self._challenge_frames,
            DeliberationStage.EVIDENCE_RESOLVED: self._resolve_frame_evidence,
            DeliberationStage.STRATEGIES_COMPLETE: self._develop_strategies,
            DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE: self._challenge_proposals,
            DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED: self._resolve_proposal_evidence,
            DeliberationStage.REVISIONS_COMPLETE: self._revise,
            DeliberationStage.ADJUDICATED: self._adjudicate,
            DeliberationStage.PLAN_COMPLETE: self._produce_plan,
        }
        session = await dispatch[stage](session)
        new_calls = session.record.model_calls[before_calls:]
        contract = self.protocol.contract_for(stage)
        checkpoint = StageCheckpoint(
            stage_id=contract.stage_id,
            resulting_stage=stage,
            provider_call_keys=tuple(call.call_id for call in new_calls),
        )
        return session.model_copy(update={"checkpoints": (*session.checkpoints, checkpoint)})

    def _advance(
        self,
        session: OfflineDeliberationSession,
        stage: DeliberationStage,
        *,
        record_updates: dict[str, Any] | None = None,
        session_updates: dict[str, Any] | None = None,
    ) -> OfflineDeliberationSession:
        state = LifecycleState(stage=session.record.stage, history=session.lifecycle_history)
        advanced = state.advance(stage)
        updates = dict(record_updates or {})
        updates["stage"] = stage
        record = session.record.model_copy(update=updates)
        combined = dict(session_updates or {})
        combined.update({"record": record, "lifecycle_history": advanced.history})
        return session.model_copy(update=combined)

    async def _generate(
        self,
        session: OfflineDeliberationSession,
        *,
        call_key: str,
        stage: DeliberationStage,
        output_type: type[OutputT],
        payload: Any,
        prompt_template: str,
        member: CouncilMemberProfile | None = None,
    ) -> tuple[OutputT, OfflineDeliberationSession]:
        prompt_path = self.prompt_root / prompt_template
        instructions = prompt_path.read_text(encoding="utf-8")
        input_text = json.dumps(_jsonable(payload), indent=2, sort_keys=True)
        result: ModelResult[OutputT] = await self.provider.generate(
            model=self.model,
            instructions=instructions,
            input_text=input_text,
            output_type=output_type,
            metadata=CallMetadata(
                session_id=session.record.session_id,
                call_key=call_key,
                stage=stage,
                member_id=member.member_id if member else None,
            ),
        )
        call = ModelCallRecord(
            call_id=call_key,
            provider=result.provider,
            model=result.model,
            stage=stage,
            member_id=member.member_id if member else None,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )
        record = session.record.model_copy(
            update={"model_calls": (*session.record.model_calls, call)}
        )
        return result.output, session.model_copy(update={"record": record})

    async def _preserve_request(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.REQUEST_PRESERVED)
        validate_stage_inputs(contract, (ArtifactKind.SOVEREIGN_REQUEST,))
        validate_stage_outputs(contract, (ArtifactKind.SOVEREIGN_REQUEST,))
        return self._advance(session, DeliberationStage.REQUEST_PRESERVED)

    async def _select_council(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.COUNCIL_SELECTED)
        validate_stage_inputs(
            contract, (ArtifactKind.SOVEREIGN_REQUEST, ArtifactKind.COUNCIL_SNAPSHOT)
        )
        validate_stage_outputs(contract, (ArtifactKind.COUNCIL_SNAPSHOT,))
        members = self.council.members
        return self._advance(
            session,
            DeliberationStage.COUNCIL_SELECTED,
            record_updates={
                "member_snapshots": members,
                "selected_member_ids": tuple(member.member_id for member in members),
            },
        )

    async def _interpret(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.INTERPRETATIONS_COMPLETE)
        validate_stage_inputs(
            contract, (ArtifactKind.SOVEREIGN_REQUEST, ArtifactKind.COUNCIL_SNAPSHOT)
        )
        interpretations: list[Interpretation] = []
        for member in self.council.advocates:
            output, session = await self._generate(
                session,
                call_key=f"interpretation:{member.member_id}",
                stage=DeliberationStage.INTERPRETATIONS_COMPLETE,
                output_type=Interpretation,
                payload={"request": session.record.request, "member": member},
                prompt_template=contract.prompt_template or "prompts/interpretation.md",
                member=member,
            )
            if output.member_id != member.member_id:
                raise OfflineEngineError("blind interpretation returned for the wrong advocate")
            interpretations.append(output)
        validate_stage_outputs(contract, (ArtifactKind.INTERPRETATION,))
        return self._advance(
            session,
            DeliberationStage.INTERPRETATIONS_COMPLETE,
            record_updates={"interpretations": tuple(interpretations)},
        )

    async def _compare_frames(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.FRAMES_COMPARED)
        output, session = await self._generate(
            session,
            call_key="frame-comparison",
            stage=DeliberationStage.FRAMES_COMPARED,
            output_type=FrameComparisonOutput,
            payload={"request": session.record.request, "interpretations": session.record.interpretations},
            prompt_template=contract.prompt_template or "prompts/compare_frames.md",
            member=self.council.seneschal,
        )
        snapshot = ClaimRegisterSnapshot(
            phase=ChallengePhase.FRAME,
            round_number=0,
            claim_register=output.claim_register,
        )
        trace = session.protocol_trace.model_copy(
            update={
                "claim_register_snapshots": (
                    *session.protocol_trace.claim_register_snapshots,
                    snapshot,
                )
            }
        )
        validate_stage_outputs(
            contract, (ArtifactKind.CLAIM_REGISTER, ArtifactKind.FRAME_REGISTER)
        )
        return self._advance(
            session,
            DeliberationStage.FRAMES_COMPARED,
            record_updates={"frame_register": output.frame_register},
            session_updates={"protocol_trace": trace},
        )

    async def _challenge_frames(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        claims = self._latest_claims(session, ChallengePhase.FRAME)
        session = await self._run_debate_phase(session, ChallengePhase.FRAME, claims)
        contract = self.protocol.contract_for(DeliberationStage.FRAME_CHALLENGES_COMPLETE)
        validate_stage_outputs(
            contract,
            (
                ArtifactKind.CHALLENGE_PLAN,
                ArtifactKind.CHALLENGE_RESPONSE,
                ArtifactKind.CONTINUATION_DECISION,
            ),
        )
        return self._advance(session, DeliberationStage.FRAME_CHALLENGES_COMPLETE)

    async def _resolve_frame_evidence(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        session = await self._resolve_evidence(session, ChallengePhase.FRAME)
        contract = self.protocol.contract_for(DeliberationStage.EVIDENCE_RESOLVED)
        validate_stage_outputs(contract, (ArtifactKind.EVIDENCE_RESOLUTION,))
        return self._advance(session, DeliberationStage.EVIDENCE_RESOLVED)

    async def _develop_strategies(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.STRATEGIES_COMPLETE)
        proposals = []
        impacts: list[DebateImpact] = []
        frame_exchanges = tuple(
            exchange
            for exchange in session.debate_exchanges
            if exchange.phase is ChallengePhase.FRAME
        )
        for member in self.council.advocates:
            output, session = await self._generate(
                session,
                call_key=f"strategy:{member.member_id}",
                stage=DeliberationStage.STRATEGIES_COMPLETE,
                output_type=StrategyDevelopmentOutput,
                payload={
                    "request": session.record.request,
                    "member": member,
                    "frame_register": session.record.frame_register,
                    "frame_exchanges": frame_exchanges,
                    "evidence": session.record.evidence_resolutions,
                },
                prompt_template=contract.prompt_template or "prompts/proposal.md",
                member=member,
            )
            if output.proposal.member_id != member.member_id:
                raise OfflineEngineError("strategy proposal returned for the wrong advocate")
            _require_target_impacts(member.member_id, frame_exchanges, output.debate_impacts)
            proposals.append(output.proposal)
            impacts.extend(output.debate_impacts)
        validate_stage_outputs(contract, (ArtifactKind.STRATEGY_PROPOSAL,))
        return self._advance(
            session,
            DeliberationStage.STRATEGIES_COMPLETE,
            record_updates={"proposals": tuple(proposals)},
            session_updates={"debate_impacts": (*session.debate_impacts, *impacts)},
        )

    async def _challenge_proposals(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        claims, session = await self._generate(
            session,
            call_key="proposal-claim-register",
            stage=DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
            output_type=ClaimRegister,
            payload={"request": session.record.request, "proposals": session.record.proposals},
            prompt_template="prompts/normalize_proposals.md",
            member=self.council.seneschal,
        )
        if claims.phase is not ChallengePhase.PROPOSAL:
            raise OfflineEngineError("proposal normalization returned the wrong challenge phase")
        snapshot = ClaimRegisterSnapshot(
            phase=ChallengePhase.PROPOSAL,
            round_number=0,
            claim_register=claims,
        )
        trace = session.protocol_trace.model_copy(
            update={
                "claim_register_snapshots": (
                    *session.protocol_trace.claim_register_snapshots,
                    snapshot,
                )
            }
        )
        session = session.model_copy(update={"protocol_trace": trace})
        session = await self._run_debate_phase(session, ChallengePhase.PROPOSAL, claims)
        contract = self.protocol.contract_for(DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE)
        validate_stage_outputs(
            contract,
            (
                ArtifactKind.CLAIM_REGISTER,
                ArtifactKind.CHALLENGE_PLAN,
                ArtifactKind.CHALLENGE_RESPONSE,
                ArtifactKind.CONTINUATION_DECISION,
            ),
        )
        return self._advance(session, DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE)

    async def _resolve_proposal_evidence(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        session = await self._resolve_evidence(session, ChallengePhase.PROPOSAL)
        contract = self.protocol.contract_for(DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED)
        validate_stage_outputs(contract, (ArtifactKind.EVIDENCE_RESOLUTION,))
        return self._advance(session, DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED)

    async def _revise(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.REVISIONS_COMPLETE)
        revisions = []
        impacts: list[DebateImpact] = []
        proposal_exchanges = tuple(
            exchange
            for exchange in session.debate_exchanges
            if exchange.phase is ChallengePhase.PROPOSAL
        )
        proposals = {proposal.member_id: proposal for proposal in session.record.proposals}
        for member in self.council.advocates:
            output, session = await self._generate(
                session,
                call_key=f"revision:{member.member_id}",
                stage=DeliberationStage.REVISIONS_COMPLETE,
                output_type=RevisionOutput,
                payload={
                    "request": session.record.request,
                    "member": member,
                    "proposal": proposals[member.member_id],
                    "proposal_exchanges": proposal_exchanges,
                    "evidence": session.record.evidence_resolutions,
                },
                prompt_template=contract.prompt_template or "prompts/revision.md",
                member=member,
            )
            if output.revision.member_id != member.member_id:
                raise OfflineEngineError("revision returned for the wrong advocate")
            if output.revision.original_proposal_id != proposals[member.member_id].proposal_id:
                raise OfflineEngineError("revision does not identify the advocate's original proposal")
            _require_target_impacts(member.member_id, proposal_exchanges, output.debate_impacts)
            revisions.append(output.revision)
            impacts.extend(output.debate_impacts)
        validate_stage_outputs(contract, (ArtifactKind.REVISION,))
        return self._advance(
            session,
            DeliberationStage.REVISIONS_COMPLETE,
            record_updates={"revisions": tuple(revisions)},
            session_updates={"debate_impacts": (*session.debate_impacts, *impacts)},
        )

    async def _adjudicate(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        require_actual_debate(session, require_both_phases=True)
        contract = self.protocol.contract_for(DeliberationStage.ADJUDICATED)
        output, session = await self._generate(
            session,
            call_key="adjudication",
            stage=DeliberationStage.ADJUDICATED,
            output_type=Adjudication,
            payload={
                "request": session.record.request,
                "interpretations": session.record.interpretations,
                "frame_register": session.record.frame_register,
                "debate_exchanges": session.debate_exchanges,
                "debate_impacts": session.debate_impacts,
                "evidence": session.record.evidence_resolutions,
                "proposals": session.record.proposals,
                "revisions": session.record.revisions,
            },
            prompt_template=contract.prompt_template or "prompts/adjudication.md",
            member=self.council.seneschal,
        )
        validate_stage_outputs(contract, (ArtifactKind.ADJUDICATION,))
        return self._advance(
            session,
            DeliberationStage.ADJUDICATED,
            record_updates={
                "adjudication": output,
                "minority_objections": output.minority_objections,
            },
        )

    async def _produce_plan(
        self, session: OfflineDeliberationSession
    ) -> OfflineDeliberationSession:
        contract = self.protocol.contract_for(DeliberationStage.PLAN_COMPLETE)
        output, session = await self._generate(
            session,
            call_key="actionable-plan",
            stage=DeliberationStage.PLAN_COMPLETE,
            output_type=ActionablePlan,
            payload={
                "request": session.record.request,
                "adjudication": session.record.adjudication,
                "revisions": session.record.revisions,
                "evidence": session.record.evidence_resolutions,
            },
            prompt_template=contract.prompt_template or "prompts/actionable_plan.md",
            member=self.council.seneschal,
        )
        validate_stage_outputs(contract, (ArtifactKind.ACTIONABLE_PLAN,))
        return self._advance(
            session,
            DeliberationStage.PLAN_COMPLETE,
            record_updates={"plan": output, "status": SessionStatus.COMPLETE},
        )

    async def _run_debate_phase(
        self,
        session: OfflineDeliberationSession,
        phase: ChallengePhase,
        claims: ClaimRegister,
    ) -> OfflineDeliberationSession:
        prior_plans = tuple(
            plan for plan in session.protocol_trace.challenge_plans if plan.phase is phase
        )
        round_number = len(prior_plans) + 1
        current_claims = claims
        while True:
            plan_prompt = (
                "prompts/challenge_frames.md"
                if phase is ChallengePhase.FRAME
                else "prompts/challenge_proposals.md"
            )
            plan, session = await self._generate(
                session,
                call_key=f"{phase.value}:challenge-plan:r{round_number}",
                stage=(
                    DeliberationStage.FRAME_CHALLENGES_COMPLETE
                    if phase is ChallengePhase.FRAME
                    else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
                ),
                output_type=ChallengePlan,
                payload={
                    "request": session.record.request,
                    "claims": current_claims,
                    "council": self.council,
                    "prior_plans": prior_plans,
                },
                prompt_template=plan_prompt,
                member=self.council.seneschal,
            )
            validate_challenge_plan(
                plan,
                claims=current_claims,
                council=self.council,
                policy=self.protocol.challenge_policy,
                prior_plans=prior_plans,
            )
            trace = session.protocol_trace.model_copy(
                update={"challenge_plans": (*session.protocol_trace.challenge_plans, plan)}
            )
            session = session.model_copy(update={"protocol_trace": trace})

            exchanges: list[DebateExchange] = []
            for assignment in plan.assignments:
                challenger = self._member(assignment.challenger_member_id)
                target = self._member(assignment.target_member_id)
                challenge, session = await self._generate(
                    session,
                    call_key=f"{phase.value}:challenge:r{round_number}:{assignment.challenge_id}",
                    stage=(
                        DeliberationStage.FRAME_CHALLENGES_COMPLETE
                        if phase is ChallengePhase.FRAME
                        else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
                    ),
                    output_type=Challenge,
                    payload={
                        "request": session.record.request,
                        "assignment": assignment,
                        "claim_register": current_claims,
                        "challenger": challenger,
                    },
                    prompt_template="prompts/articulate_challenge.md",
                    member=challenger,
                )
                response, session = await self._generate(
                    session,
                    call_key=f"{phase.value}:response:r{round_number}:{assignment.challenge_id}",
                    stage=(
                        DeliberationStage.FRAME_CHALLENGES_COMPLETE
                        if phase is ChallengePhase.FRAME
                        else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
                    ),
                    output_type=ChallengeResponse,
                    payload={
                        "request": session.record.request,
                        "assignment": assignment,
                        "challenge": challenge,
                        "target": target,
                    },
                    prompt_template="prompts/respond_to_challenge.md",
                    member=target,
                )
                exchanges.append(
                    DebateExchange(
                        phase=phase,
                        round_number=round_number,
                        assignment=assignment,
                        challenge=challenge,
                        response=response,
                    )
                )

            decision, session = await self._generate(
                session,
                call_key=f"{phase.value}:continuation:r{round_number}",
                stage=(
                    DeliberationStage.FRAME_CHALLENGES_COMPLETE
                    if phase is ChallengePhase.FRAME
                    else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
                ),
                output_type=ContinuationDecision,
                payload={
                    "request": session.record.request,
                    "claims": current_claims,
                    "plan": plan,
                    "exchanges": exchanges,
                },
                prompt_template="prompts/assess_debate_round.md",
                member=self.council.seneschal,
            )
            validate_continuation_decision(
                decision,
                claims=current_claims,
                policy=self.protocol.challenge_policy,
            )
            trace = session.protocol_trace.model_copy(
                update={
                    "continuation_decisions": (
                        *session.protocol_trace.continuation_decisions,
                        decision,
                    )
                }
            )
            record = session.record.model_copy(
                update={
                    "challenges": (
                        *session.record.challenges,
                        *(exchange.challenge for exchange in exchanges),
                    ),
                    "challenge_responses": (
                        *session.record.challenge_responses,
                        *(exchange.response for exchange in exchanges),
                    ),
                    "evidence_requests": (
                        *session.record.evidence_requests,
                        *(
                            exchange.response.evidence_request
                            for exchange in exchanges
                            if exchange.response.evidence_request is not None
                        ),
                    ),
                }
            )
            session = session.model_copy(
                update={
                    "record": record,
                    "protocol_trace": trace,
                    "debate_exchanges": (*session.debate_exchanges, *exchanges),
                }
            )
            if not decision.continue_debate:
                return session

            updated_claims, session = await self._generate(
                session,
                call_key=f"{phase.value}:claim-register:r{round_number}",
                stage=(
                    DeliberationStage.FRAME_CHALLENGES_COMPLETE
                    if phase is ChallengePhase.FRAME
                    else DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
                ),
                output_type=ClaimRegister,
                payload={"prior_claims": current_claims, "exchanges": exchanges},
                prompt_template="prompts/normalize_after_debate.md",
                member=self.council.seneschal,
            )
            snapshot = ClaimRegisterSnapshot(
                phase=phase,
                round_number=round_number,
                claim_register=updated_claims,
                supersedes_register_id=current_claims.register_id,
            )
            trace = session.protocol_trace.model_copy(
                update={
                    "claim_register_snapshots": (
                        *session.protocol_trace.claim_register_snapshots,
                        snapshot,
                    )
                }
            )
            session = session.model_copy(update={"protocol_trace": trace})
            current_claims = updated_claims
            prior_plans = (*prior_plans, plan)
            round_number += 1

    async def _resolve_evidence(
        self,
        session: OfflineDeliberationSession,
        phase: ChallengePhase,
    ) -> OfflineDeliberationSession:
        challenge_ids = {
            exchange.exchange_id for exchange in session.debate_exchanges if exchange.phase is phase
        }
        requests = tuple(
            response.evidence_request
            for response in session.record.challenge_responses
            if response.challenge_id in challenge_ids and response.evidence_request is not None
        )
        resolutions: list[EvidenceResolution] = []
        status = SessionStatus.ACTIVE
        for request in requests:
            resolution = await self.evidence_resolver.resolve(request)
            if resolution.evidence_request_id != request.evidence_request_id:
                raise OfflineEngineError("evidence resolver returned a mismatched request identifier")
            resolutions.append(resolution)
            if resolution.outcome is EvidenceOutcome.USER_CLARIFICATION_REQUIRED:
                status = SessionStatus.WAITING_FOR_USER
            elif resolution.outcome is EvidenceOutcome.DELIBERATION_PAUSED:
                status = SessionStatus.PAUSED
        record = session.record.model_copy(
            update={
                "evidence_resolutions": (
                    *session.record.evidence_resolutions,
                    *resolutions,
                ),
                "status": status,
            }
        )
        return session.model_copy(update={"record": record})

    def _latest_claims(
        self,
        session: OfflineDeliberationSession,
        phase: ChallengePhase,
    ) -> ClaimRegister:
        candidates = [
            snapshot
            for snapshot in session.protocol_trace.claim_register_snapshots
            if snapshot.phase is phase
        ]
        if not candidates:
            raise OfflineEngineError(f"no claim register exists for {phase.value} debate")
        return max(candidates, key=lambda item: item.round_number).claim_register

    def _member(self, member_id: str) -> CouncilMemberProfile:
        return next(member for member in self.council.members if member.member_id == member_id)


def _jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, Mapping):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _require_target_impacts(
    member_id: str,
    exchanges: tuple[DebateExchange, ...],
    impacts: tuple[DebateImpact, ...],
) -> None:
    targeted = {
        exchange.exchange_id
        for exchange in exchanges
        if exchange.assignment.target_member_id == member_id
    }
    recorded = {impact.exchange_id for impact in impacts}
    missing = targeted - recorded
    unexpected = recorded - targeted
    if missing:
        raise OfflineEngineError(
            f"advocate {member_id!r} did not record consequences for direct challenges: "
            f"{sorted(missing)}"
        )
    if unexpected:
        raise OfflineEngineError(
            f"advocate {member_id!r} claimed impacts from exchanges that did not target it: "
            f"{sorted(unexpected)}"
        )
