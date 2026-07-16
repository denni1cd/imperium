"""Gate 2 tests for session-level provider injection and artifact authority."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from imperium.domain.enums import (
    ChallengeDisposition,
    ChallengePhase,
    ContinuationReason,
    DeliberationStage,
    EvidenceOutcome,
    SessionStatus,
    StopReason,
)
from imperium.domain.models import (
    ChallengeResponse,
    DeliberationRecord,
    EvidenceRequest,
    EvidenceResolution,
)
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
)
from imperium.engine.protocol_rules import InvalidProtocolArtifact
from imperium.offline.engine import _call_key
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.provider_engine import (
    MissingEvidenceDisposition,
    OfflineDeliberationEngine,
    ProviderBoundDeliberationEngine,
)
from imperium.offline.persistence import load_session
from imperium.offline.replay_script import build_replay_records
from imperium.providers.base import CallMetadata, ModelResult, ProviderError
from imperium.providers.replay import ReplayProvider

ROOT = Path(__file__).resolve().parents[1]
OutputT = TypeVar("OutputT", bound=BaseModel)


def _deterministic_record(record: DeliberationRecord) -> dict[str, object]:
    payload = record.model_dump(mode="json")
    for call in payload["model_calls"]:
        call.pop("created_at", None)
    return payload


class RecordingProvider:
    def __init__(self, replay: ReplayProvider) -> None:
        self.replay = replay
        self.calls: list[CallMetadata] = []

    async def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        output_type: type[OutputT],
        metadata: CallMetadata,
    ) -> ModelResult[OutputT]:
        self.calls.append(metadata)
        result = await self.replay.generate(
            model=model,
            instructions=instructions,
            input_text=input_text,
            output_type=output_type,
            metadata=metadata,
        )
        return ModelResult[OutputT](
            output=result.output,
            provider="gate2-injected-replay",
            model=result.model,
            response_id=result.response_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )


class OverrideProvider:
    """Return selected valid artifacts that intentionally contradict the fixture."""

    def __init__(self, replay: ReplayProvider, overrides: dict[str, BaseModel]) -> None:
        self.replay = replay
        self.overrides = overrides
        self.calls: list[CallMetadata] = []
        self.inputs: dict[str, str] = {}

    async def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        output_type: type[OutputT],
        metadata: CallMetadata,
    ) -> ModelResult[OutputT]:
        self.calls.append(metadata)
        self.inputs[metadata.call_key] = input_text
        override = self.overrides.get(metadata.call_key)
        if override is not None:
            return ModelResult[OutputT](
                output=output_type.model_validate(override.model_dump(mode="python")),
                provider="gate2-override",
                model=model,
            )
        result = await self.replay.generate(
            model=model,
            instructions=instructions,
            input_text=input_text,
            output_type=output_type,
            metadata=metadata,
        )
        return ModelResult[OutputT](
            output=result.output,
            provider="gate2-override",
            model=result.model,
            response_id=result.response_id,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            latency_ms=result.latency_ms,
            retries=result.retries,
        )


class FailingIfCalledProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def generate(self, **kwargs):
        del kwargs
        self.calls += 1
        raise AssertionError("provider must not run after context preflight fails")


def _provider_for(scenario, overrides: dict[str, BaseModel]) -> OverrideProvider:
    return OverrideProvider(
        ReplayProvider(build_replay_records(scenario, model="gate2-authority")),
        overrides,
    )


def _key(
    stage: DeliberationStage,
    role: str,
    output_type: type[BaseModel],
    *,
    phase: ChallengePhase | None = None,
    round_number: int | None = None,
    subject: str | None = None,
    member_id: str | None = None,
) -> str:
    return _call_key(
        resulting_stage=stage,
        role=role,
        output_type=output_type,
        phase=phase,
        round_number=round_number,
        subject=subject,
        member_id=member_id,
    )


def _provider_evidence_override(scenario, request_id: str):
    original = scenario.proposal_rounds[1].responses[0]
    request = EvidenceRequest(
        evidence_request_id=request_id,
        requester_member_id=original.member_id,
        disputed_claim="A provider generated a decision-critical evidence request.",
        decision_impact="The scope decision changes if evidence is unavailable.",
        requested_information="Provide an exact disposition for this accepted request ID.",
        preferred_source="operator-supplied Gate 2 input",
    )
    response = original.model_copy(update={"evidence_request": request})
    key = _key(
        DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
        "target",
        ChallengeResponse,
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        subject=original.challenge_id,
        member_id=original.member_id,
    )
    return key, request, response


@pytest.mark.asyncio
async def test_default_replay_preserves_stage4_decisions_and_artifacts(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    baseline = await OfflineDeliberationEngine(model="gate2-default-replay").run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "baseline",
    )
    engine = ProviderBoundDeliberationEngine(model="gate2-default-replay")
    session = await engine.run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "provider-bound",
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert session.artifact_authority == "provider"
    assert isinstance(engine.session_provider, ReplayProvider)
    assert len(engine.session_provider.calls) == 36
    assert tuple(call.call_key for call in engine.session_provider.calls) == session.completed_call_keys
    assert _deterministic_record(session.record) == _deterministic_record(baseline.record)
    assert session.protocol_trace == baseline.protocol_trace
    assert session.lifecycle_history == baseline.lifecycle_history
    assert session.completed_call_keys == baseline.completed_call_keys
    assert session.evidence_history == baseline.evidence_history
    assert session.lineage == baseline.lineage
    assert tuple(turn.call_key for turn in session.turns) == tuple(
        turn.call_key for turn in baseline.turns
    )
    assert tuple(turn.output_artifact_id for turn in session.turns) == tuple(
        turn.output_artifact_id for turn in baseline.turns
    )


@pytest.mark.asyncio
async def test_one_injected_provider_handles_all_turns(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = RecordingProvider(
        ReplayProvider(build_replay_records(scenario, model="gate2-simulated"))
    )
    engine = ProviderBoundDeliberationEngine(provider=provider, model="gate2-simulated")
    session = await engine.run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "injected",
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert engine.session_provider is provider
    assert len(provider.calls) == 36
    assert tuple(call.call_key for call in provider.calls) == session.completed_call_keys
    assert {call.provider for call in session.record.model_calls} == {"gate2-injected-replay"}


@pytest.mark.asyncio
async def test_returned_empty_plan_suppresses_fixture_exchange(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    plan_key = _key(
        DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        "seneschal",
        ChallengePlan,
        phase=ChallengePhase.FRAME,
        round_number=1,
        subject="plan",
    )
    empty_plan = ChallengePlan(
        plan_id="provider-empty-frame-plan",
        phase=ChallengePhase.FRAME,
        round_number=1,
        no_challenge_reason="The provider found no additional material frame challenge.",
    )
    provider = _provider_for(scenario, {plan_key: empty_plan})
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-authority",
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "empty-plan",
    )

    accepted = next(
        item
        for item in session.protocol_trace.challenge_plans
        if item.phase is ChallengePhase.FRAME and item.round_number == 1
    )
    assert accepted == empty_plan
    assert not any(
        call.call_key.startswith("frame_challenges_complete:")
        and (":challenger:" in call.call_key or ":target:" in call.call_key)
        for call in provider.calls
    )


@pytest.mark.asyncio
async def test_returned_challenge_is_exposed_to_target_context(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    original = scenario.frame_rounds[0].challenges[0]
    changed = original.model_copy(
        update={"statement": "Provider-authored challenge text visible only if routing is real."}
    )
    challenge_key = _key(
        DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        "challenger",
        ChallengeArtifact,
        phase=ChallengePhase.FRAME,
        round_number=1,
        subject=original.challenge_id,
        member_id=original.challenger_member_id,
    )
    target_key = _key(
        DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        "target",
        ChallengeResponse,
        phase=ChallengePhase.FRAME,
        round_number=1,
        subject=original.challenge_id,
        member_id=original.target_member_id,
    )
    provider = _provider_for(scenario, {challenge_key: changed})
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-authority",
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "challenge-context",
    )

    assert changed.statement in provider.inputs[target_key]
    assert next(
        item
        for item in session.protocol_trace.challenges
        if item.challenge_id == original.challenge_id
    ).statement == changed.statement


@pytest.mark.asyncio
async def test_seneschal_continuation_context_contains_responses(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    provider = _provider_for(scenario, {})
    continuation_key = _key(
        DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        "seneschal",
        ContinuationDecision,
        phase=ChallengePhase.FRAME,
        round_number=1,
        subject="continuation",
    )
    response = scenario.frame_rounds[0].responses[0]

    await ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-authority",
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "seneschal-response-context",
    )

    assert response.response in provider.inputs[continuation_key]
    assert f"{response.challenge_id}:response" in provider.inputs[continuation_key]


@pytest.mark.asyncio
async def test_returned_stop_decision_prevents_scripted_second_round(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    continuation_key = _key(
        DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
        "seneschal",
        ContinuationDecision,
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        subject="continuation",
    )
    stop = ContinuationDecision(
        decision_id="provider-proposal-stop-r1",
        phase=ChallengePhase.PROPOSAL,
        completed_round=1,
        continue_debate=False,
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="The provider judged the proposal phase complete after one round.",
    )
    provider = _provider_for(scenario, {continuation_key: stop})
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-authority",
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "stop-r1",
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert not any(":r2:" in call.call_key for call in provider.calls)
    assert next(
        item
        for item in session.protocol_trace.continuation_decisions
        if item.phase is ChallengePhase.PROPOSAL and item.completed_round == 1
    ) == stop


@pytest.mark.asyncio
async def test_provider_cannot_request_third_round(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    continuation_key = _key(
        DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
        "seneschal",
        ContinuationDecision,
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        subject="continuation",
    )
    invalid_continue = ContinuationDecision(
        decision_id="provider-invalid-r3-request",
        phase=ChallengePhase.PROPOSAL,
        completed_round=2,
        continue_debate=True,
        reasons=(ContinuationReason.UNRESOLVED_MATERIAL_CLAIM,),
        unresolved_claim_ids=("claim-vanguard-scope",),
        next_action="Run a prohibited third proposal round.",
        justification="Used only to prove the protocol safety limit rejects it.",
    )
    provider = _provider_for(scenario, {continuation_key: invalid_continue})

    with pytest.raises(InvalidProtocolArtifact, match="cannot continue past"):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2-authority",
        ).run(
            scenario,
            project_root=ROOT,
            output_dir=tmp_path / "third-round",
        )

    failed = load_session(tmp_path / "third-round" / "session.json")
    assert continuation_key not in failed.completed_call_keys
    assert all(turn.call_key != continuation_key for turn in failed.turns)
    assert invalid_continue not in failed.protocol_trace.continuation_decisions


@pytest.mark.asyncio
async def test_protocol_invalid_plan_is_not_committed(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    plan_key = _key(
        DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        "seneschal",
        ChallengePlan,
        phase=ChallengePhase.FRAME,
        round_number=1,
        subject="plan",
    )
    original = scenario.frame_rounds[0].plan
    invalid = original.model_copy(
        update={
            "assignments": (
                original.assignments[0].model_copy(
                    update={"target_claim_id": "schema-valid-but-unknown-claim"}
                ),
            )
        }
    )
    output = tmp_path / "invalid-plan"

    with pytest.raises(InvalidProtocolArtifact, match="unknown claim"):
        await ProviderBoundDeliberationEngine(
            provider=_provider_for(scenario, {plan_key: invalid}),
            model="gate2-authority",
        ).run(scenario, project_root=ROOT, output_dir=output)

    failed = load_session(output / "session.json")
    assert plan_key not in failed.completed_call_keys
    assert all(turn.call_key != plan_key for turn in failed.turns)
    assert invalid not in failed.protocol_trace.challenge_plans


def test_cosmetic_claim_rewrite_is_not_material_new_input() -> None:
    scenario = build_challenged_scenario()
    previous = scenario.proposal_rounds[0].claim_register
    cosmetic = previous.model_copy(
        update={
            "register_id": "cosmetic-register",
            "claims": (
                previous.claims[0].model_copy(
                    update={"supporting_evidence": ("Reordered presentation only.",)}
                ),
                *previous.claims[1:],
            ),
        }
    )

    assert ProviderBoundDeliberationEngine._claims_with_new_input(previous, cosmetic) == ()


def test_only_incorporated_refinement_is_material_new_input() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        first.responses,
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=1,
    ) == ("claim-vanguard-scope",)


def test_unincorporated_refinement_is_not_material_new_input() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds
    unchanged = second.claim_register.model_copy(
        update={
            "claims": (
                first.claim_register.claims[0],
                *second.claim_register.claims[1:],
            )
        }
    )

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        unchanged,
        first.responses,
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=1,
    ) == ()


def test_non_refine_response_cannot_unlock_repetition() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds
    scope_response = first.responses[0].model_copy(
        update={"disposition": ChallengeDisposition.DEFEND}
    )

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        (scope_response,),
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=1,
    ) == ()


def test_other_round_refinement_cannot_unlock_repetition() -> None:
    scenario = build_challenged_scenario()
    first, second = scenario.proposal_rounds

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        first.claim_register,
        second.claim_register,
        first.responses,
        first.challenges,
        phase=ChallengePhase.PROPOSAL,
        prior_round_number=2,
    ) == ()


def test_genuinely_new_claim_id_is_material_new_input() -> None:
    scenario = build_challenged_scenario()
    previous = scenario.proposal_rounds[0].claim_register
    new_claim = previous.claims[0].model_copy(
        update={"claim_id": "claim-new-material-input"}
    )
    current = ClaimRegister(
        register_id="register-with-new-claim",
        phase=previous.phase,
        claims=(*previous.claims, new_claim),
    )

    assert ProviderBoundDeliberationEngine._claims_with_new_input(
        previous, current
    ) == ("claim-new-material-input",)


@pytest.mark.asyncio
async def test_provider_generated_evidence_id_uses_exact_resolution(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    response_key, request, response = _provider_evidence_override(
        scenario, "provider-new-evidence-id"
    )
    resolution = EvidenceResolution(
        evidence_request_id=request.evidence_request_id,
        outcome=EvidenceOutcome.GATHERED,
        evidence=("The operator explicitly matched the provider-generated request ID.",),
        source_references=("test:provider-generated-evidence",),
    )
    provider = _provider_for(scenario, {response_key: response})
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-authority",
        evidence_resolutions={request.evidence_request_id: resolution},
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "matched-evidence",
    )

    assert request in session.record.evidence_requests
    assert resolution in session.record.evidence_resolutions
    assert all(
        item.evidence_request_id != "evidence-fixture-coverage"
        for item in session.record.evidence_resolutions
    )


@pytest.mark.asyncio
async def test_provider_generated_evidence_wait_resumes_by_accepted_id(tmp_path: Path) -> None:
    scenario = build_challenged_scenario()
    response_key, request, response = _provider_evidence_override(
        scenario, "provider-clarification-id"
    )
    waiting_resolution = EvidenceResolution(
        evidence_request_id=request.evidence_request_id,
        outcome=EvidenceOutcome.USER_CLARIFICATION_REQUIRED,
        remaining_uncertainty=("The operator has not supplied the requested clarification.",),
    )
    output = tmp_path / "provider-waiting"
    waiting = await ProviderBoundDeliberationEngine(
        provider=_provider_for(scenario, {response_key: response}),
        model="gate2-authority",
        evidence_resolutions={request.evidence_request_id: waiting_resolution},
    ).run(
        scenario,
        project_root=ROOT,
        output_dir=output,
    )
    assert waiting.status is SessionStatus.WAITING_FOR_USER

    replacement = EvidenceResolution(
        evidence_request_id=request.evidence_request_id,
        outcome=EvidenceOutcome.GATHERED,
        evidence=("The operator supplied the clarification for the accepted request ID.",),
        source_references=("test:provider-evidence-resume",),
    )
    resumed = await ProviderBoundDeliberationEngine(
        provider=_provider_for(scenario, {response_key: response}),
        model="gate2-authority",
    ).resume(
        output / "session.json",
        evidence_replacements=(replacement,),
    )

    assert resumed.status is SessionStatus.COMPLETE
    assert replacement in resumed.record.evidence_resolutions
    assert resumed.evidence_history[-1].replaced_outcome is EvidenceOutcome.USER_CLARIFICATION_REQUIRED


@pytest.mark.asyncio
async def test_provider_generated_evidence_without_disposition_fails_closed(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    response_key, request, response = _provider_evidence_override(
        scenario, "provider-unmatched-evidence-id"
    )
    provider = _provider_for(scenario, {response_key: response})

    with pytest.raises(MissingEvidenceDisposition, match=request.evidence_request_id):
        await ProviderBoundDeliberationEngine(
            provider=provider,
            model="gate2-authority",
        ).run(
            scenario,
            project_root=ROOT,
            output_dir=tmp_path / "unmatched-evidence",
        )


@pytest.mark.asyncio
async def test_context_ceiling_fails_before_provider_invocation(tmp_path: Path) -> None:
    provider = FailingIfCalledProvider()
    engine = ProviderBoundDeliberationEngine(provider=provider, max_context_bytes=1)
    with pytest.raises(ProviderError, match="context for .* limit is 1 bytes"):
        await engine.run(
            build_challenged_scenario(),
            project_root=ROOT,
            output_dir=tmp_path / "bounded",
        )
    assert provider.calls == 0
