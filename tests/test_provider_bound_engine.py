"""Gate 2 tests for session-level provider injection and artifact authority."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel

from imperium.domain.enums import (
    ChallengePhase,
    ContinuationReason,
    DeliberationStage,
    EvidenceOutcome,
    StopReason,
)
from imperium.domain.models import (
    ChallengeResponse,
    DeliberationRecord,
    EvidenceRequest,
    EvidenceResolution,
)
from imperium.domain.protocol import ChallengeArtifact, ChallengePlan, ContinuationDecision
from imperium.engine.protocol_rules import InvalidProtocolArtifact
from imperium.offline.engine import OfflineDeliberationEngine, _call_key
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.provider_engine import (
    MissingEvidenceDisposition,
    ProviderBoundDeliberationEngine,
)
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
    """Delegate to replay while proving one injected instance handles every turn."""

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


@pytest.mark.asyncio
async def test_default_replay_provider_preserves_complete_stage4_result(
    tmp_path: Path,
) -> None:
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
    assert tuple(call.call_key for call in engine.session_provider.calls) == (
        session.completed_call_keys
    )
    assert _deterministic_record(session.record) == _deterministic_record(
        baseline.record
    )
    assert session.protocol_trace == baseline.protocol_trace
    assert session.lifecycle_history == baseline.lifecycle_history
    assert session.completed_call_keys == baseline.completed_call_keys
    assert tuple(
        (item.evidence_request_id, item.outcome, item.replaced_outcome)
        for item in session.evidence_history
    ) == tuple(
        (item.evidence_request_id, item.outcome, item.replaced_outcome)
        for item in baseline.evidence_history
    )
    assert session.lineage == baseline.lineage
    assert session.turns == baseline.turns


@pytest.mark.asyncio
async def test_one_injected_provider_handles_all_turns_without_output_drift(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    provider = RecordingProvider(
        ReplayProvider(build_replay_records(scenario, model="gate2-simulated"))
    )
    engine = ProviderBoundDeliberationEngine(
        provider=provider,
        model="gate2-simulated",
    )

    session = await engine.run(
        scenario,
        project_root=ROOT,
        output_dir=tmp_path / "injected",
    )

    assert session.record.stage is DeliberationStage.PLAN_COMPLETE
    assert engine.session_provider is provider
    assert len(provider.calls) == 36
    assert tuple(call.call_key for call in provider.calls) == session.completed_call_keys
    assert {call.provider for call in session.record.model_calls} == {
        "gate2-injected-replay"
    }
    assert session.record.plan == scenario.plan
    assert session.record.adjudication == scenario.adjudication


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
        ":challenger:" in call.call_key
        and call.call_key.startswith("frame_challenges_complete:")
        for call in provider.calls
    )
    assert not any(
        ":target:" in call.call_key
        and call.call_key.startswith("frame_challenges_complete:")
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
    accepted = next(
        item
        for item in session.protocol_trace.challenges
        if item.challenge_id == original.challenge_id
    )
    assert accepted.statement == changed.statement


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
    accepted = next(
        item
        for item in session.protocol_trace.continuation_decisions
        if item.phase is ChallengePhase.PROPOSAL and item.completed_round == 1
    )
    assert accepted == stop


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


@pytest.mark.asyncio
async def test_provider_generated_evidence_id_uses_exact_explicit_resolution(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    original = scenario.proposal_rounds[1].responses[0]
    request = EvidenceRequest(
        evidence_request_id="provider-new-evidence-id",
        requester_member_id=original.member_id,
        disputed_claim="The provider generated a new decision-critical evidence request.",
        decision_impact="The scope decision changes if the evidence is not available.",
        requested_information="Provide an explicit matched disposition for this exact ID.",
        preferred_source="operator-supplied Gate 2 fixture",
    )
    changed_response = original.model_copy(update={"evidence_request": request})
    response_key = _key(
        DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
        "target",
        ChallengeResponse,
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        subject=original.challenge_id,
        member_id=original.member_id,
    )
    resolution = EvidenceResolution(
        evidence_request_id=request.evidence_request_id,
        outcome=EvidenceOutcome.GATHERED,
        evidence=("The operator explicitly matched the provider-generated request ID.",),
        source_references=("test:provider-generated-evidence",),
    )
    provider = _provider_for(scenario, {response_key: changed_response})

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
async def test_provider_generated_evidence_id_without_disposition_fails_closed(
    tmp_path: Path,
) -> None:
    scenario = build_challenged_scenario()
    original = scenario.proposal_rounds[1].responses[0]
    request = EvidenceRequest(
        evidence_request_id="provider-unmatched-evidence-id",
        requester_member_id=original.member_id,
        disputed_claim="A provider request cannot borrow an unrelated fixture disposition.",
        decision_impact="The evidence stage must stop rather than invent a mapping.",
        requested_information="Require an exact matching disposition.",
        preferred_source="operator input",
    )
    changed_response = original.model_copy(update={"evidence_request": request})
    response_key = _key(
        DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
        "target",
        ChallengeResponse,
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        subject=original.challenge_id,
        member_id=original.member_id,
    )
    provider = _provider_for(scenario, {response_key: changed_response})

    with pytest.raises(MissingEvidenceDisposition, match="provider-unmatched-evidence-id"):
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
    engine = ProviderBoundDeliberationEngine(
        provider=provider,
        max_context_bytes=1,
    )

    with pytest.raises(ProviderError, match="context for .* limit is 1 bytes"):
        await engine.run(
            build_challenged_scenario(),
            project_root=ROOT,
            output_dir=tmp_path / "bounded",
        )

    assert provider.calls == 0
