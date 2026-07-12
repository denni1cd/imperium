"""End-to-end Stage 4 test with direct frame and proposal confrontation."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest

from imperium.configuration import (
    load_council_configuration,
    load_protocol_configuration,
    load_value_vocabulary,
)
from imperium.domain.enums import (
    ChallengeDisposition,
    ChallengePhase,
    ClaimKind,
    DeliberationStage,
    Materiality,
    StopReason,
)
from imperium.domain.models import (
    ActionStep,
    ActionablePlan,
    Adjudication,
    Challenge,
    ChallengeResponse,
    Frame,
    FrameRegister,
    Interpretation,
    MinorityObjection,
    Revision,
    SovereignRequest,
    StrategyProposal,
)
from imperium.domain.offline import (
    DebateImpact,
    FrameComparisonOutput,
    RevisionOutput,
    StrategyDevelopmentOutput,
)
from imperium.domain.protocol import (
    ChallengeAssignment,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    NormalizedClaim,
)
from imperium.engine.debate_verification import require_actual_debate
from imperium.engine.offline import OfflineDeliberationEngine
from imperium.persistence.offline import export_offline_session, load_offline_session
from imperium.providers.replay import ReplayProvider

ROOT = Path(__file__).resolve().parents[2]


def _record(output):
    return {"output": output.model_dump(mode="json"), "provider": "replay", "model": "offline"}


def _interpretation(member_id: str, inclination: str, emphasis: str) -> Interpretation:
    return Interpretation(
        interpretation_id=f"interp-{member_id}",
        member_id=member_id,
        core_decision="Whether to build a reusable workflow platform now or validate demand with a manual pilot.",
        desired_outcome="Gain reliable evidence while preserving a credible path to useful automation.",
        opportunities=("A pilot can expose the real recurring workflow.",),
        risks=("A premature platform may optimize assumptions rather than demonstrated needs.",),
        assumptions=("The workflow will recur if the pilot succeeds.",),
        missing_information=("Observed pilot demand and operator burden.",),
        initial_inclination=inclination,
        value_influence={emphasis: f"The {emphasis} priority controls this interpretation."},
        confidence=Decimal("0.72"),
    )


def _proposal(
    member_id: str,
    proposal_id: str,
    title: str,
    summary: str,
    actions: tuple[str, ...],
) -> StrategyProposal:
    return StrategyProposal(
        proposal_id=proposal_id,
        member_id=member_id,
        title=title,
        summary=summary,
        proposed_actions=actions,
        expected_benefits=("Produces decision-relevant evidence without a full platform commitment.",),
        assumptions=("A two-week pilot is long enough to expose recurring work.",),
        tradeoffs=("Defers full automation until evidence exists.",),
        risks=("The pilot may underrepresent later scale.",),
        sacrifices=("Some immediate leverage is postponed.",),
        decision_triggers=("Build reusable components only after repeated demand is observed.",),
        reconsideration_conditions=("Reconsider if the pilot cannot collect representative evidence.",),
        confidence=Decimal("0.74"),
    )


def _revision(
    member_id: str,
    revision_id: str,
    original: StrategyProposal,
    revised: StrategyProposal,
    reason: str,
) -> Revision:
    return Revision(
        revision_id=revision_id,
        member_id=member_id,
        original_proposal_id=original.proposal_id,
        revised_proposal=revised,
        changes=("The proposal now reflects direct council challenge.",),
        reasons=(reason,),
        expected_effect="Improves the plan's balance of learning, commitment, and downside control.",
        confidence=Decimal("0.79"),
    )


def _replay_records() -> dict[str, list[dict]]:
    interpretations = {
        "steward": _interpretation("steward", "Run a bounded manual pilot first.", "economy"),
        "vanguard": _interpretation("vanguard", "Act immediately to preserve momentum.", "urgency"),
        "architect": _interpretation("architect", "Capture reusable structure during the pilot.", "leverage"),
        "castellan": _interpretation("castellan", "Keep the first commitment reversible.", "resilience"),
    }

    frame_claims = ClaimRegister(
        register_id="frame-register-0",
        phase=ChallengePhase.FRAME,
        claims=(
            NormalizedClaim(
                claim_id="frame-claim-vanguard",
                source_artifact_id="interp-vanguard",
                source_member_id="vanguard",
                kind=ClaimKind.FORECAST,
                statement="Delay will materially reduce learning and momentum.",
                materiality=Materiality.HIGH,
                decision_impact="This claim determines whether immediate commitment is justified.",
                contested_by_member_ids=("castellan",),
            ),
            NormalizedClaim(
                claim_id="frame-claim-steward",
                source_artifact_id="interp-steward",
                source_member_id="steward",
                kind=ClaimKind.ASSUMPTION,
                statement="A full platform before repeat demand is proven creates avoidable cost.",
                materiality=Materiality.HIGH,
                decision_impact="This claim determines whether reusable architecture should be deferred.",
                contested_by_member_ids=("vanguard",),
            ),
        ),
    )
    frame_output = FrameComparisonOutput(
        claim_register=frame_claims,
        frame_register=FrameRegister(
            shared_frames=(
                Frame(
                    frame_id="frame-shared",
                    label="Evidence before scale",
                    description="All advocates require evidence before irreversible platform investment.",
                    advocate_member_ids=("steward", "vanguard", "architect", "castellan"),
                    decision_impact="The dispute concerns the size and design of the first commitment.",
                ),
            ),
            contested_frames=(
                Frame(
                    frame_id="frame-timing",
                    label="Immediate action versus protected pacing",
                    description="Vanguard emphasizes delay while Castellan emphasizes bounded exposure.",
                    advocate_member_ids=("vanguard", "castellan"),
                    decision_impact="Changes the scope and reversibility of the first step.",
                ),
            ),
            value_disagreements=("Urgency versus resilience and economy.",),
        ),
    )

    frame_assignment_1 = ChallengeAssignment(
        challenge_id="frame-challenge-vanguard",
        phase=ChallengePhase.FRAME,
        round_number=1,
        challenger_member_id="castellan",
        target_member_id="vanguard",
        target_artifact_id="interp-vanguard",
        target_claim_id="frame-claim-vanguard",
        materiality=Materiality.HIGH,
        reason="Urgency may be overstated relative to reversible learning.",
        expected_consequence="Vanguard must narrow immediate commitment or defend the cost of delay.",
    )
    frame_assignment_2 = ChallengeAssignment(
        challenge_id="frame-challenge-steward",
        phase=ChallengePhase.FRAME,
        round_number=1,
        challenger_member_id="vanguard",
        target_member_id="steward",
        target_artifact_id="interp-steward",
        target_claim_id="frame-claim-steward",
        materiality=Materiality.HIGH,
        reason="Cost caution may become delay that prevents useful evidence.",
        expected_consequence="Steward must distinguish a bounded pilot from premature platform investment.",
    )
    frame_plan = ChallengePlan(
        plan_id="frame-plan-1",
        phase=ChallengePhase.FRAME,
        round_number=1,
        assignments=(frame_assignment_1, frame_assignment_2),
    )
    frame_challenge_1 = Challenge(
        challenge_id="frame-challenge-vanguard",
        challenger_member_id="castellan",
        target_member_id="vanguard",
        target_artifact_id="interp-vanguard",
        disputed_claim="Delay will materially reduce learning and momentum.",
        materiality="high",
        failure_consequence="The council may treat urgency as justification for an irreversible build.",
    )
    frame_response_1 = ChallengeResponse(
        challenge_id="frame-challenge-vanguard",
        member_id="vanguard",
        disposition=ChallengeDisposition.REFINE,
        response="Immediate action is valuable, but it should be a two-week reversible pilot rather than a full build.",
        revised_claim="Delay should be avoided through an immediate reversible pilot, not platform commitment.",
    )
    frame_challenge_2 = Challenge(
        challenge_id="frame-challenge-steward",
        challenger_member_id="vanguard",
        target_member_id="steward",
        target_artifact_id="interp-steward",
        disputed_claim="A full platform before repeat demand is proven creates avoidable cost.",
        materiality="high",
        failure_consequence="Cost caution could block the evidence needed to make a better decision.",
    )
    frame_response_2 = ChallengeResponse(
        challenge_id="frame-challenge-steward",
        member_id="steward",
        disposition=ChallengeDisposition.DEFEND,
        response="The objection is to a platform, not to action; a capped manual pilot is the economical evidence-producing step.",
    )
    frame_stop = ContinuationDecision(
        decision_id="frame-stop-1",
        phase=ChallengePhase.FRAME,
        completed_round=1,
        continue_debate=False,
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="The timing disagreement now converges on immediate but reversible evidence gathering.",
    )

    proposals = {
        "steward": _proposal(
            "steward",
            "proposal-steward",
            "Capped manual pilot",
            "Run a tightly bounded manual pilot before spending on reusable architecture.",
            ("Define a two-week pilot budget.", "Track repeated manual work and operator burden."),
        ),
        "vanguard": _proposal(
            "vanguard",
            "proposal-vanguard",
            "Immediate reversible pilot",
            "Start now, but keep the first commitment reversible and evidence-focused.",
            ("Launch the pilot immediately.", "Set a decision date at the end of week two."),
        ),
        "architect": _proposal(
            "architect",
            "proposal-architect",
            "Pilot with reusable harness",
            "Build a small reusable harness while operating the pilot.",
            ("Create a reusable event schema.", "Automate pilot logging before demand is confirmed."),
        ),
        "castellan": _proposal(
            "castellan",
            "proposal-castellan",
            "Protected pilot",
            "Run the pilot with rollback, workload, and failure controls.",
            ("Cap time and spend.", "Define rollback and stop conditions before launch."),
        ),
    }

    frame_impacts = {
        "steward": (
            DebateImpact(
                exchange_id="frame-challenge-steward",
                member_id="steward",
                resulting_artifact_id="proposal-steward",
                disposition=ChallengeDisposition.DEFEND,
                explanation="Steward clarified that economy supports a capped evidence-producing pilot rather than inaction.",
                reasoning_strengthened=True,
            ),
        ),
        "vanguard": (
            DebateImpact(
                exchange_id="frame-challenge-vanguard",
                member_id="vanguard",
                resulting_artifact_id="proposal-vanguard",
                disposition=ChallengeDisposition.REFINE,
                explanation="Vanguard changed immediate action from platform commitment to a reversible pilot.",
                position_changed=True,
            ),
        ),
    }

    proposal_claims = ClaimRegister(
        register_id="proposal-register-0",
        phase=ChallengePhase.PROPOSAL,
        claims=(
            NormalizedClaim(
                claim_id="proposal-claim-architect",
                source_artifact_id="proposal-architect",
                source_member_id="architect",
                kind=ClaimKind.PROPOSED_ACTION,
                statement="The pilot should include a reusable automation harness before demand is confirmed.",
                materiality=Materiality.HIGH,
                decision_impact="This determines whether Stage 1 includes architecture or only disposable instrumentation.",
                contested_by_member_ids=("steward",),
            ),
            NormalizedClaim(
                claim_id="proposal-claim-castellan",
                source_artifact_id="proposal-castellan",
                source_member_id="castellan",
                kind=ClaimKind.TRADEOFF,
                statement="The pilot requires formal rollback and workload controls before launch.",
                materiality=Materiality.HIGH,
                decision_impact="This determines whether controls delay the immediate pilot.",
                contested_by_member_ids=("vanguard",),
            ),
        ),
    )
    proposal_assignment_1 = ChallengeAssignment(
        challenge_id="proposal-challenge-architect",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        challenger_member_id="steward",
        target_member_id="architect",
        target_artifact_id="proposal-architect",
        target_claim_id="proposal-claim-architect",
        materiality=Materiality.HIGH,
        reason="The reusable harness may recreate premature platform cost.",
        expected_consequence="Architect must bound or remove architecture not needed for learning.",
    )
    proposal_assignment_2 = ChallengeAssignment(
        challenge_id="proposal-challenge-castellan",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        challenger_member_id="vanguard",
        target_member_id="castellan",
        target_artifact_id="proposal-castellan",
        target_claim_id="proposal-claim-castellan",
        materiality=Materiality.HIGH,
        reason="Formal controls may delay a bounded and reversible pilot.",
        expected_consequence="Castellan must show the controls are proportional and quick to establish.",
    )
    proposal_plan = ChallengePlan(
        plan_id="proposal-plan-1",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=(proposal_assignment_1, proposal_assignment_2),
    )
    proposal_challenge_1 = Challenge(
        challenge_id="proposal-challenge-architect",
        challenger_member_id="steward",
        target_member_id="architect",
        target_artifact_id="proposal-architect",
        disputed_claim="The pilot should include a reusable automation harness before demand is confirmed.",
        materiality="high",
        failure_consequence="The pilot could become a platform project before recurrence is demonstrated.",
    )
    proposal_response_1 = ChallengeResponse(
        challenge_id="proposal-challenge-architect",
        member_id="architect",
        disposition=ChallengeDisposition.REFINE,
        response="Only a disposable logging script and stable event schema are justified during the pilot.",
        revised_claim="Use disposable logging plus a stable event schema; defer reusable automation.",
    )
    proposal_challenge_2 = Challenge(
        challenge_id="proposal-challenge-castellan",
        challenger_member_id="vanguard",
        target_member_id="castellan",
        target_artifact_id="proposal-castellan",
        disputed_claim="The pilot requires formal rollback and workload controls before launch.",
        materiality="high",
        failure_consequence="Overbuilt controls could erase the value of immediate action.",
    )
    proposal_response_2 = ChallengeResponse(
        challenge_id="proposal-challenge-castellan",
        member_id="castellan",
        disposition=ChallengeDisposition.DEFEND,
        response="The controls are a one-page cap, stop condition, and workload check that can be set the same day.",
    )
    proposal_stop = ContinuationDecision(
        decision_id="proposal-stop-1",
        phase=ChallengePhase.PROPOSAL,
        completed_round=1,
        continue_debate=False,
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="Architecture is narrowed and safeguards are shown to be proportional.",
    )

    revised_proposals = {
        "steward": proposals["steward"],
        "vanguard": proposals["vanguard"],
        "architect": proposals["architect"].model_copy(
            update={
                "title": "Pilot with disposable instrumentation",
                "summary": "Use a stable event schema and disposable logging; defer reusable automation.",
                "proposed_actions": (
                    "Define a stable event schema.",
                    "Use disposable logging during the pilot.",
                ),
            }
        ),
        "castellan": proposals["castellan"].model_copy(
            update={
                "summary": "Launch immediately after a same-day cap, stop condition, and workload check.",
            }
        ),
    }
    revisions = {
        member_id: _revision(
            member_id,
            f"revision-{member_id}",
            proposals[member_id],
            revised_proposals[member_id],
            "Retained or revised the proposal after direct proposal-phase confrontation.",
        )
        for member_id in proposals
    }
    proposal_impacts = {
        "architect": (
            DebateImpact(
                exchange_id="proposal-challenge-architect",
                member_id="architect",
                resulting_artifact_id="revision-architect",
                disposition=ChallengeDisposition.REFINE,
                explanation="Architect removed premature reusable automation and retained only disposable instrumentation.",
                position_changed=True,
            ),
        ),
        "castellan": (
            DebateImpact(
                exchange_id="proposal-challenge-castellan",
                member_id="castellan",
                resulting_artifact_id="revision-castellan",
                disposition=ChallengeDisposition.DEFEND,
                explanation="Castellan demonstrated that the controls are proportional and do not delay launch.",
                reasoning_strengthened=True,
            ),
        ),
    }

    adjudication = Adjudication(
        adjudication_id="adjudication-1",
        chosen_strategy="Run an immediate two-week manual pilot with disposable logging and same-day safeguards.",
        decisive_reasons=(
            "Frame debate converted urgency from platform commitment into a reversible pilot.",
            "Proposal debate removed premature reusable automation while preserving useful evidence capture.",
            "The remaining safeguards are proportional and can be established without meaningful delay.",
        ),
        accepted_frames=("Evidence before scale", "Immediate but reversible action"),
        rejected_alternatives={
            "Build the reusable platform now": "Repeat demand and workflow shape are not yet demonstrated.",
            "Delay all action": "A bounded pilot produces evidence at low exposure.",
        },
        minority_objections=(
            MinorityObjection(
                member_id="architect",
                objection="Disposable instrumentation may create avoidable rework if demand is immediately obvious.",
                decision_impact="Could justify earlier reusable investment.",
                reconsideration_trigger="Repeated workflows exceed the pilot threshold during week one.",
            ),
        ),
        assumptions=("The pilot can be bounded to two weeks and a fixed workload cap.",),
        actions_requiring_authorization=("Commit staff time to the two-week pilot.",),
        confidence=Decimal("0.86"),
    )
    plan = ActionablePlan(
        decision="Run a two-week manual pilot before building reusable automation.",
        objective="Measure recurrence, operator burden, and value while preserving immediate momentum.",
        immediate_next_action="Define the pilot scope, workload cap, and success threshold in one page.",
        steps=(
            ActionStep(
                order=1,
                action="Define the pilot scope, event schema, workload cap, and stop conditions.",
                owner="user",
                completion_signal="A one-page pilot charter is approved.",
            ),
            ActionStep(
                order=2,
                action="Run the manual workflow with disposable logging for two weeks.",
                dependencies=("Pilot charter approved",),
                completion_signal="Two weeks of workflow, burden, and outcome data are recorded.",
            ),
            ActionStep(
                order=3,
                action="Decide whether observed recurrence justifies reusable automation.",
                dependencies=("Pilot data available",),
                completion_signal="Build, extend the pilot, or stop is explicitly selected.",
            ),
        ),
        checkpoints=("End of week one", "End of week two"),
        risks_and_mitigations={
            "Pilot becomes an unbounded manual process": "Enforce the workload cap and end date.",
            "Disposable logging loses useful evidence": "Use the stable event schema from day one.",
        },
        assumptions=("The pilot can be run without irreversible commitments.",),
        decision_triggers=("Build only if repeated demand and expected savings cross the approved threshold.",),
        stop_or_reconsideration_conditions=(
            "Stop if workload exceeds the cap without proportional value.",
            "Reconsider early automation if repeat demand is demonstrated in week one.",
        ),
    )

    records = {
        f"interpretation:{member_id}": [_record(output)]
        for member_id, output in interpretations.items()
    }
    records.update(
        {
            "frame-comparison": [_record(frame_output)],
            "frame:challenge-plan:r1": [_record(frame_plan)],
            "frame:challenge:r1:frame-challenge-vanguard": [_record(frame_challenge_1)],
            "frame:response:r1:frame-challenge-vanguard": [_record(frame_response_1)],
            "frame:challenge:r1:frame-challenge-steward": [_record(frame_challenge_2)],
            "frame:response:r1:frame-challenge-steward": [_record(frame_response_2)],
            "frame:continuation:r1": [_record(frame_stop)],
            "proposal-claim-register": [_record(proposal_claims)],
            "proposal:challenge-plan:r1": [_record(proposal_plan)],
            "proposal:challenge:r1:proposal-challenge-architect": [_record(proposal_challenge_1)],
            "proposal:response:r1:proposal-challenge-architect": [_record(proposal_response_1)],
            "proposal:challenge:r1:proposal-challenge-castellan": [_record(proposal_challenge_2)],
            "proposal:response:r1:proposal-challenge-castellan": [_record(proposal_response_2)],
            "proposal:continuation:r1": [_record(proposal_stop)],
            "adjudication": [_record(adjudication)],
            "actionable-plan": [_record(plan)],
        }
    )
    for member_id, proposal in proposals.items():
        records[f"strategy:{member_id}"] = [
            _record(
                StrategyDevelopmentOutput(
                    proposal=proposal,
                    debate_impacts=frame_impacts.get(member_id, ()),
                )
            )
        ]
    for member_id, revision in revisions.items():
        records[f"revision:{member_id}"] = [
            _record(
                RevisionOutput(
                    revision=revision,
                    debate_impacts=proposal_impacts.get(member_id, ()),
                )
            )
        ]
    return records


def _engine(provider: ReplayProvider) -> OfflineDeliberationEngine:
    vocabulary = load_value_vocabulary(ROOT / "config" / "values.yaml")
    council = load_council_configuration(
        ROOT / "config" / "council.yaml", vocabulary=vocabulary
    )
    protocol = load_protocol_configuration(
        ROOT / "config" / "protocol.yaml",
        vocabulary=vocabulary,
        council=council,
    )
    return OfflineDeliberationEngine(
        council=council,
        protocol=protocol,
        provider=provider,
        prompt_root=ROOT,
    )


@pytest.mark.asyncio
async def test_offline_vertical_slice_is_direct_debate_and_resumable(tmp_path: Path) -> None:
    request = SovereignRequest(
        original_text="Should we build a reusable workflow orchestrator now or run a manual pilot first?",
        goals=("Choose a practical next step that creates evidence and useful progress.",),
        hard_constraints=("Do not make an irreversible platform commitment without evidence.",),
    )
    first_provider = ReplayProvider(_replay_records())
    first_engine = _engine(first_provider)
    checkpoint = tmp_path / "offline-session.json"

    session = await first_engine.run(
        first_engine.new_session(request),
        stop_after=DeliberationStage.STRATEGIES_COMPLETE,
        checkpoint_path=checkpoint,
    )
    assert session.record.stage is DeliberationStage.STRATEGIES_COMPLETE
    assert [
        call.call_key for call in first_provider.calls if "frame:" in call.call_key
    ] == [
        "frame:challenge-plan:r1",
        "frame:challenge:r1:frame-challenge-vanguard",
        "frame:response:r1:frame-challenge-vanguard",
        "frame:challenge:r1:frame-challenge-steward",
        "frame:response:r1:frame-challenge-steward",
        "frame:continuation:r1",
    ]

    restored = load_offline_session(checkpoint)
    second_provider = ReplayProvider(_replay_records())
    completed = await _engine(second_provider).run(restored, checkpoint_path=checkpoint)

    assert completed.record.stage is DeliberationStage.PLAN_COMPLETE
    assert completed.record.plan is not None
    assert completed.record.plan.immediate_next_action.startswith("Define the pilot scope")
    report = require_actual_debate(completed)
    assert report.direct_exchange_count == 4
    assert report.consequential_impact_count == 4
    assert set(report.phases_with_direct_exchange) == {
        ChallengePhase.FRAME,
        ChallengePhase.PROPOSAL,
    }
    assert {exchange.challenge.challenger_member_id for exchange in completed.debate_exchanges} == {
        "castellan",
        "vanguard",
        "steward",
    }
    assert len(completed.checkpoints) == 12

    reloaded = load_offline_session(checkpoint)
    assert reloaded.record.plan == completed.record.plan
    assert reloaded.debate_exchanges == completed.debate_exchanges
    assert reloaded.debate_impacts == completed.debate_impacts
