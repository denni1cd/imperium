"""Deterministic synthetic scenarios for Stage 4 validation and CI."""

from __future__ import annotations

from decimal import Decimal

from imperium.domain.enums import (
    ChallengeDisposition,
    ChallengePhase,
    ClaimKind,
    ContinuationReason,
    EvidenceOutcome,
    Materiality,
    StopReason,
)
from imperium.domain.models import (
    ActionablePlan,
    ActionStep,
    Adjudication,
    ChallengeResponse,
    EvidenceRequest,
    EvidenceResolution,
    Frame,
    FrameRegister,
    Interpretation,
    MinorityObjection,
    Revision,
    SovereignRequest,
    StrategyProposal,
)
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengeAssignment,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
    NormalizedClaim,
)
from imperium.offline.models import DebateRoundFixture, OfflineScenario


ADVOCATES = ("steward", "vanguard", "architect", "castellan")


def _request() -> SovereignRequest:
    return SovereignRequest(
        request_id="request-stage4-pilot",
        original_text=(
            "Decide whether to invest in an offline strategic council prototype and produce "
            "a bounded plan that tests whether debate improves decisions before live-model work."
        ),
        goals=(
            "Validate the complete Imperium deliberation lifecycle.",
            "Produce an actionable, reversible implementation plan.",
        ),
        hard_constraints=(
            "Use only synthetic or replayed reasoning artifacts.",
            "Do not authorize live providers or autonomous execution.",
        ),
        prohibitions=(
            "Do not treat scripted agreement as proof of strategic improvement.",
        ),
        supplied_facts=(
            "The value vocabulary, fixed council, and protocol 1.3 are approved.",
            "Stage 4 is an offline process validation rather than a live-model experiment.",
        ),
    )


def _interpretations() -> tuple[Interpretation, ...]:
    return (
        Interpretation(
            interpretation_id="interpretation-steward",
            member_id="steward",
            core_decision="Whether the validation value justifies the implementation cost.",
            desired_outcome="A bounded test that avoids platform investment before evidence.",
            opportunities=("Retire structural uncertainty cheaply.",),
            risks=("The engine could become a costly framework before proving usefulness.",),
            assumptions=("A compact deterministic vertical slice can expose the key failures.",),
            initial_inclination="Fund only a narrowly scoped offline vertical slice.",
            value_influence={"economy": "Demand evidence before expanding scope."},
            confidence=Decimal("0.78"),
        ),
        Interpretation(
            interpretation_id="interpretation-vanguard",
            member_id="vanguard",
            core_decision="Whether to move fast enough to test the council hypothesis now.",
            desired_outcome="A complete demonstration that exercises real multi-turn debate.",
            opportunities=("Convert extensive design work into observable behavior.",),
            risks=("More design delay could consume momentum without producing evidence.",),
            assumptions=("A broad Stage 4 implementation is needed to make the test meaningful.",),
            initial_inclination="Implement the complete vertical slice immediately.",
            value_influence={"urgency": "Prefer a decisive end-to-end test over more planning."},
            confidence=Decimal("0.84"),
        ),
        Interpretation(
            interpretation_id="interpretation-architect",
            member_id="architect",
            core_decision="Which minimal reusable execution primitives Stage 4 should establish.",
            desired_outcome="A provider-neutral core reusable for live and experimental stages.",
            opportunities=("Reuse frozen contexts, call keys, and checkpoints later.",),
            risks=("One-off scripting could create a dead-end demonstration.",),
            assumptions=("A small session envelope and runner can remain reusable without a framework.",),
            initial_inclination="Build reusable primitives only where Stage 4 directly requires them.",
            value_influence={"leverage": "Favor reusable boundaries over duplicated orchestration."},
            confidence=Decimal("0.74"),
        ),
        Interpretation(
            interpretation_id="interpretation-castellan",
            member_id="castellan",
            core_decision="Whether the prototype can fail safely and resume without corrupting state.",
            desired_outcome="A deterministic run with explicit halt, recovery, and stop conditions.",
            opportunities=("Prove the system cannot silently skip protocol failures.",),
            risks=("Resume or evidence bugs could make the record look complete when it is not.",),
            assumptions=("Atomic checkpoints and fail-closed validation are sufficient for offline use.",),
            initial_inclination="Proceed only with corruption, halt, and interruption tests.",
            value_influence={"resilience": "Require recovery evidence before live-provider work."},
            confidence=Decimal("0.81"),
        ),
    )


def _frame_register() -> FrameRegister:
    return FrameRegister(
        shared_frames=(
            Frame(
                frame_id="frame-shared-validation",
                label="Validation before expansion",
                description="Stage 4 should test the protocol before live-model investment.",
                advocate_member_ids=ADVOCATES,
                decision_impact="Supports a bounded offline implementation rather than a broad platform.",
            ),
        ),
        contested_frames=(
            Frame(
                frame_id="frame-scope-speed",
                label="Completeness versus implementation economy",
                description="The council disagrees about how much must be built for a meaningful test.",
                advocate_member_ids=("steward", "vanguard", "architect"),
                decision_impact="Controls implementation scope and the first usable checkpoint.",
            ),
        ),
        unique_frames=(
            Frame(
                frame_id="frame-recovery",
                label="Recovery integrity",
                description="The prototype must prove interruption and resume behavior.",
                advocate_member_ids=("castellan",),
                decision_impact="Adds explicit checkpoint and corruption acceptance tests.",
            ),
        ),
        interpretive_disagreements=(
            "Whether completeness requires broad capability or only complete protocol coverage.",
        ),
        value_disagreements=(
            "Urgency favors immediate implementation while economy favors the smallest falsifiable slice.",
        ),
    )


def _frame_claims() -> ClaimRegister:
    return ClaimRegister(
        register_id="frame-register-r0",
        phase=ChallengePhase.FRAME,
        claims=(
            NormalizedClaim(
                claim_id="frame-claim-completeness",
                source_artifact_id="interpretation-vanguard",
                source_member_id="vanguard",
                kind=ClaimKind.INTERPRETATION,
                statement="A broad Stage 4 implementation is required for a meaningful test.",
                materiality=Materiality.HIGH,
                decision_impact="This claim controls the implementation size and cost.",
            ),
        ),
    )


def _frame_round() -> DebateRoundFixture:
    claims = _frame_claims()
    assignment = ChallengeAssignment(
        challenge_id="frame-scope-r1",
        phase=ChallengePhase.FRAME,
        round_number=1,
        challenger_member_id="steward",
        target_member_id="vanguard",
        target_artifact_id="interpretation-vanguard",
        target_claim_id="frame-claim-completeness",
        materiality=Materiality.HIGH,
        reason="Broad implementation may spend heavily before the core protocol is proven executable.",
        expected_consequence="Narrow completeness to observable protocol coverage or defend the extra scope.",
    )
    plan = ChallengePlan(
        plan_id="frame-plan-r1",
        phase=ChallengePhase.FRAME,
        round_number=1,
        assignments=(assignment,),
    )
    challenge = ChallengeArtifact(
        challenge_id=assignment.challenge_id,
        phase=assignment.phase,
        round_number=assignment.round_number,
        challenger_member_id=assignment.challenger_member_id,
        target_member_id=assignment.target_member_id,
        target_artifact_id=assignment.target_artifact_id,
        target_claim_id=assignment.target_claim_id,
        statement="Which broad capabilities are necessary to falsify the protocol hypothesis now?",
        failure_consequence="Unnecessary architecture could delay the first evidence and obscure failure.",
    )
    response = ChallengeResponse(
        challenge_id=assignment.challenge_id,
        member_id="vanguard",
        disposition=ChallengeDisposition.REFINE,
        response="Completeness means every approved transition and direct debate turn, not a broad platform.",
        revised_claim=(
            "A complete protocol vertical slice, with bounded persistence and resume, is required "
            "for a meaningful test."
        ),
    )
    decision = ContinuationDecision(
        decision_id="frame-continuation-r1",
        phase=ChallengePhase.FRAME,
        completed_round=1,
        continue_debate=False,
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="The refined frame reconciles completeness with a bounded implementation.",
    )
    return DebateRoundFixture(
        phase=ChallengePhase.FRAME,
        round_number=1,
        claim_register=claims,
        claim_snapshot_round=0,
        plan=plan,
        challenges=(challenge,),
        responses=(response,),
        continuation=decision,
    )


def _proposal(
    member_id: str,
    proposal_id: str,
    title: str,
    summary: str,
    actions: tuple[str, ...],
    benefits: tuple[str, ...],
    risks: tuple[str, ...],
    sacrifices: tuple[str, ...],
    confidence: str,
) -> StrategyProposal:
    return StrategyProposal(
        proposal_id=proposal_id,
        member_id=member_id,
        title=title,
        summary=summary,
        proposed_actions=actions,
        expected_benefits=benefits,
        assumptions=("Synthetic replay can validate process execution without live reasoning.",),
        tradeoffs=("More fixture coverage increases implementation size but reduces hidden gaps.",),
        risks=risks,
        sacrifices=sacrifices,
        decision_triggers=("Proceed to live integration only after all offline acceptance paths pass.",),
        reconsideration_conditions=(
            "Stop or revise Stage 4 if the protocol cannot be executed without bypasses.",
        ),
        confidence=Decimal(confidence),
    )


def _proposals() -> tuple[StrategyProposal, ...]:
    return (
        _proposal(
            "steward",
            "proposal-steward",
            "Minimum complete vertical slice",
            "Implement only orchestration, replay fixtures, validation, persistence, and review exports.",
            ("Build one complete challenged fixture.", "Add halt and resume tests."),
            ("Produces evidence with bounded implementation cost.",),
            ("A narrow fixture may miss later integration friction.",),
            ("Defer live providers and experiment infrastructure.",),
            "0.83",
        ),
        _proposal(
            "vanguard",
            "proposal-vanguard",
            "Full Stage 4 acceptance sweep",
            "Implement every planned synthetic path in one decisive Stage 4 effort.",
            ("Build all complete and halted fixtures.", "Publish inspectable CI artifacts."),
            ("Ends design uncertainty and creates a concrete local test.",),
            ("Scope may become too broad for the first implementation pass.",),
            ("Accept higher initial effort to reach a meaningful gate quickly.",),
            "0.86",
        ),
        _proposal(
            "architect",
            "proposal-architect",
            "Reusable offline session core",
            "Create a compact frozen runtime, session envelope, deterministic call router, and derived views.",
            ("Define reusable session contracts.", "Route all scripted artifacts through ReplayProvider."),
            ("The same core can support future live providers without changing protocol semantics.",),
            ("Reusable abstractions could drift toward framework building.",),
            ("Spend modest extra effort on stable boundaries and call keys.",),
            "0.77",
        ),
        _proposal(
            "castellan",
            "proposal-castellan",
            "Fail-closed resumable validation",
            "Make checkpoints, halt states, corrupted-state rejection, and interruption recovery mandatory.",
            ("Checkpoint before and after calls.", "Test waiting, pause, corruption, and resume."),
            ("Prevents a plausible-looking but internally inconsistent session.",),
            ("Recovery requirements add code before live behavior is known.",),
            ("Accept slower completion to protect record integrity.",),
            "0.82",
        ),
    )


def _proposal_claims(round_two: bool = False) -> ClaimRegister:
    scale_statement = (
        "Stage 4 should implement every planned synthetic path before local review."
        if not round_two
        else "Implement the challenged complete path plus explicit empty, halt, conditional, "
        "and interruption acceptance fixtures before local review."
    )
    return ClaimRegister(
        register_id="proposal-register-r1" if round_two else "proposal-register-r0",
        phase=ChallengePhase.PROPOSAL,
        claims=(
            NormalizedClaim(
                claim_id="claim-vanguard-scope",
                source_artifact_id="proposal-vanguard",
                source_member_id="vanguard",
                kind=ClaimKind.PROPOSED_ACTION,
                statement=scale_statement,
                materiality=Materiality.HIGH,
                decision_impact="Controls whether Stage 4 is a thin smoke test or a credible local gate.",
            ),
            NormalizedClaim(
                claim_id="claim-castellan-recovery",
                source_artifact_id="proposal-castellan",
                source_member_id="castellan",
                kind=ClaimKind.RISK,
                statement="Checkpoint and resume integrity must be demonstrated before completion.",
                materiality=Materiality.HIGH,
                decision_impact="Controls whether saved sessions can be trusted.",
            ),
            NormalizedClaim(
                claim_id="claim-architect-reuse",
                source_artifact_id="proposal-architect",
                source_member_id="architect",
                kind=ClaimKind.PROPOSED_ACTION,
                statement="Stage 4 should establish reusable frozen-runtime and call-routing primitives.",
                materiality=Materiality.HIGH,
                decision_impact="Controls whether the implementation remains a one-off script.",
            ),
            NormalizedClaim(
                claim_id="claim-steward-cost",
                source_artifact_id="proposal-steward",
                source_member_id="steward",
                kind=ClaimKind.TRADEOFF,
                statement="The implementation must remain bounded to direct Stage 4 acceptance needs.",
                materiality=Materiality.HIGH,
                decision_impact="Controls architecture and maintenance burden.",
            ),
        ),
    )


def _proposal_round_one() -> DebateRoundFixture:
    claims = _proposal_claims()
    assignments = (
        ChallengeAssignment(
            challenge_id="proposal-scope-r1",
            phase=ChallengePhase.PROPOSAL,
            round_number=1,
            challenger_member_id="steward",
            target_member_id="vanguard",
            target_artifact_id="proposal-vanguard",
            target_claim_id="claim-vanguard-scope",
            materiality=Materiality.HIGH,
            reason="The full sweep may exceed the smallest implementation that proves the protocol.",
            expected_consequence="Define the acceptance fixtures that are truly required now.",
        ),
        ChallengeAssignment(
            challenge_id="proposal-recovery-r1",
            phase=ChallengePhase.PROPOSAL,
            round_number=1,
            challenger_member_id="vanguard",
            target_member_id="castellan",
            target_artifact_id="proposal-castellan",
            target_claim_id="claim-castellan-recovery",
            materiality=Materiality.HIGH,
            reason="Recovery work could delay the first complete run.",
            expected_consequence="Show which recovery proof is indispensable for the Stage 4 gate.",
        ),
        ChallengeAssignment(
            challenge_id="proposal-reuse-r1",
            phase=ChallengePhase.PROPOSAL,
            round_number=1,
            challenger_member_id="castellan",
            target_member_id="architect",
            target_artifact_id="proposal-architect",
            target_claim_id="claim-architect-reuse",
            materiality=Materiality.HIGH,
            reason="Reusable primitives can become an untested platform dependency.",
            expected_consequence="Bound reuse to capabilities exercised by current fixtures.",
        ),
        ChallengeAssignment(
            challenge_id="proposal-cost-r1",
            phase=ChallengePhase.PROPOSAL,
            round_number=1,
            challenger_member_id="architect",
            target_member_id="steward",
            target_artifact_id="proposal-steward",
            target_claim_id="claim-steward-cost",
            materiality=Materiality.HIGH,
            reason="An excessively thin slice may create disposable code and require reimplementation.",
            expected_consequence="Identify the minimum stable boundaries worth implementing now.",
        ),
    )
    plan = ChallengePlan(
        plan_id="proposal-plan-r1",
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        assignments=assignments,
    )
    challenges = tuple(
        ChallengeArtifact(
            challenge_id=assignment.challenge_id,
            phase=assignment.phase,
            round_number=assignment.round_number,
            challenger_member_id=assignment.challenger_member_id,
            target_member_id=assignment.target_member_id,
            target_artifact_id=assignment.target_artifact_id,
            target_claim_id=assignment.target_claim_id,
            statement=assignment.reason,
            failure_consequence=assignment.expected_consequence,
        )
        for assignment in assignments
    )
    responses = (
        ChallengeResponse(
            challenge_id="proposal-scope-r1",
            member_id="vanguard",
            disposition=ChallengeDisposition.REFINE,
            response="The required sweep is the complete path plus each distinct halt and resume behavior.",
            revised_claim=(
                "Implement the challenged complete path plus explicit empty, halt, conditional, "
                "and interruption acceptance fixtures before local review."
            ),
        ),
        ChallengeResponse(
            challenge_id="proposal-recovery-r1",
            member_id="castellan",
            disposition=ChallengeDisposition.DEFEND,
            response="One interrupted-call resume and malformed-checkpoint rejection are minimum trust proofs.",
        ),
        ChallengeResponse(
            challenge_id="proposal-reuse-r1",
            member_id="architect",
            disposition=ChallengeDisposition.REFINE,
            response="Reuse is limited to frozen runtime, session envelope, stable call keys, and views exercised now.",
            revised_claim="Only Stage 4-exercised session and routing primitives should be reusable.",
        ),
        ChallengeResponse(
            challenge_id="proposal-cost-r1",
            member_id="steward",
            disposition=ChallengeDisposition.DEFEND,
            response="Stable boundaries are justified only where tests demonstrate immediate Stage 4 use.",
        ),
    )
    continuation = ContinuationDecision(
        decision_id="proposal-continuation-r1",
        phase=ChallengePhase.PROPOSAL,
        completed_round=1,
        continue_debate=True,
        reasons=(ContinuationReason.UNRESOLVED_MATERIAL_CLAIM,),
        unresolved_claim_ids=("claim-vanguard-scope",),
        next_action="Test whether the refined fixture boundary remains too broad.",
        justification="The revised scope claim still controls the implementation gate and cost.",
    )
    return DebateRoundFixture(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        claim_register=claims,
        claim_snapshot_round=0,
        plan=plan,
        challenges=challenges,
        responses=responses,
        continuation=continuation,
    )


def _proposal_round_two() -> DebateRoundFixture:
    claims = _proposal_claims(round_two=True)
    assignment = ChallengeAssignment(
        challenge_id="proposal-scope-r2",
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        challenger_member_id="steward",
        target_member_id="vanguard",
        target_artifact_id="proposal-vanguard",
        target_claim_id="claim-vanguard-scope",
        materiality=Materiality.HIGH,
        reason="Does every listed fixture change a distinct execution decision, or can any be deferred?",
        expected_consequence="Defend the fixture set or remove redundant acceptance work.",
    )
    plan = ChallengePlan(
        plan_id="proposal-plan-r2",
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        assignments=(assignment,),
    )
    challenge = ChallengeArtifact(
        challenge_id=assignment.challenge_id,
        phase=assignment.phase,
        round_number=assignment.round_number,
        challenger_member_id=assignment.challenger_member_id,
        target_member_id=assignment.target_member_id,
        target_artifact_id=assignment.target_artifact_id,
        target_claim_id=assignment.target_claim_id,
        statement=assignment.reason,
        failure_consequence=assignment.expected_consequence,
        evidence_needed=("A bounded acceptance matrix linking each fixture to a distinct failure mode.",),
    )
    evidence_request = EvidenceRequest(
        evidence_request_id="evidence-fixture-coverage",
        requester_member_id="vanguard",
        disputed_claim=claims.claims[0].statement,
        decision_impact="The implementation scope changes if fixtures are redundant.",
        requested_information="A synthetic mapping from each fixture to a unique protocol failure mode.",
        preferred_source="stage4 synthetic coverage fixture",
    )
    response = ChallengeResponse(
        challenge_id=assignment.challenge_id,
        member_id="vanguard",
        disposition=ChallengeDisposition.REQUEST_EVIDENCE,
        response="The fixture set should be retained only if each path exposes a distinct failure class.",
        evidence_request=evidence_request,
    )
    continuation = ContinuationDecision(
        decision_id="proposal-continuation-r2",
        phase=ChallengePhase.PROPOSAL,
        completed_round=2,
        continue_debate=False,
        stop_reason=StopReason.PHASE_COMPLETE,
        justification="The challenge phase is complete and the evidence request routes to proposal evidence resolution.",
    )
    return DebateRoundFixture(
        phase=ChallengePhase.PROPOSAL,
        round_number=2,
        claim_register=claims,
        claim_snapshot_round=1,
        supersedes_register_id="proposal-register-r0",
        claims_with_new_input=("claim-vanguard-scope",),
        plan=plan,
        challenges=(challenge,),
        responses=(response,),
        continuation=continuation,
    )


def _gathered_resolution() -> EvidenceResolution:
    return EvidenceResolution(
        evidence_request_id="evidence-fixture-coverage",
        outcome=EvidenceOutcome.GATHERED,
        evidence=(
            "Complete path tests lifecycle composition; empty path tests conditional challenge cardinality; "
            "waiting and pause test halt semantics; conditional tests bounded uncertainty; interruption tests resume integrity.",
        ),
        source_references=("fixture:stage4-coverage-matrix",),
        remaining_uncertainty=("Live-model reasoning quality remains untested.",),
    )


def _revisions() -> tuple[Revision, ...]:
    original = {proposal.member_id: proposal for proposal in _proposals()}
    revised = {
        "steward": _proposal(
            "steward",
            "proposal-steward-final",
            "Bounded complete Stage 4",
            "Implement the complete challenged path and only the distinct halt, conditional, empty, and interruption fixtures.",
            ("Build the shared offline runner.", "Exercise each distinct acceptance path."),
            ("Creates a credible local gate without live-provider scope.",),
            ("Fixture code still carries maintenance cost.",),
            ("Defer all experiment and live-provider infrastructure.",),
            "0.88",
        ),
        "vanguard": _proposal(
            "vanguard",
            "proposal-vanguard-final",
            "Decisive but bounded acceptance sweep",
            "Retain every fixture that maps to a distinct protocol failure and remove unrelated platform work.",
            ("Complete all distinct Stage 4 acceptance fixtures.", "Publish synthetic artifacts."),
            ("Ends process uncertainty and enables local inspection.",),
            ("A deterministic success may still overstate readiness for live reasoning.",),
            ("Accept implementation effort only for unique failure coverage.",),
            "0.89",
        ),
        "architect": _proposal(
            "architect",
            "proposal-architect-final",
            "Exercised reusable session primitives",
            "Retain only the frozen runtime, session envelope, stable call router, persistence, and derived views used by tests.",
            ("Implement exercised primitives.", "Avoid extension points not required by Stage 4."),
            ("Supports later provider replacement without building a framework.",),
            ("Some future integration may still require refactoring.",),
            ("Sacrifice speculative extensibility.",),
            "0.84",
        ),
        "castellan": original["castellan"].model_copy(
            update={"proposal_id": "proposal-castellan-final"}
        ),
    }
    return (
        Revision(
            revision_id="revision-steward",
            member_id="steward",
            original_proposal_id=original["steward"].proposal_id,
            revised_proposal=revised["steward"],
            changes=("Accepted the distinct fixture sweep while preserving scope limits.",),
            reasons=("Each retained fixture exposes a different protocol failure mode.",),
            expected_effect="Balances validation coverage with implementation economy.",
            confidence=Decimal("0.88"),
        ),
        Revision(
            revision_id="revision-vanguard",
            member_id="vanguard",
            original_proposal_id=original["vanguard"].proposal_id,
            revised_proposal=revised["vanguard"],
            changes=("Removed broad platform implications and tied scope to unique acceptance failures.",),
            reasons=("The Accountant's challenge exposed redundant interpretations of completeness.",),
            supporting_evidence=("fixture:stage4-coverage-matrix",),
            concessions=("Completeness does not require live providers or experiment tooling.",),
            expected_effect="Preserves urgency while bounding implementation scope.",
            confidence=Decimal("0.89"),
        ),
        Revision(
            revision_id="revision-architect",
            member_id="architect",
            original_proposal_id=original["architect"].proposal_id,
            revised_proposal=revised["architect"],
            changes=("Restricted reuse to primitives exercised by current tests.",),
            reasons=("The Castellan's challenge exposed speculative platform risk.",),
            concessions=("Deferred provider registries and generalized workflow abstractions.",),
            expected_effect="Provides leverage without premature architecture.",
            confidence=Decimal("0.84"),
        ),
        Revision(
            revision_id="revision-castellan",
            member_id="castellan",
            original_proposal_id=original["castellan"].proposal_id,
            revised_proposal=revised["castellan"],
            reasons=("Retained because interruption and halt integrity remain mandatory trust conditions.",),
            unresolved_disagreements=(
                "A green deterministic fixture does not prove live-provider resume safety.",
            ),
            expected_effect="Keeps recovery and corruption failures visible at the next gate.",
            confidence=Decimal("0.84"),
        ),
    )


def _adjudication() -> Adjudication:
    return Adjudication(
        adjudication_id="adjudication-stage4",
        chosen_strategy=(
            "Implement a bounded complete Stage 4: use the Architect's exercised session core, "
            "the Castellan's fail-closed checkpoints, the Accountant's scope discipline, and "
            "Gazgul's full set of distinct acceptance fixtures."
        ),
        decisive_reasons=(
            "Every retained fixture maps to a distinct protocol or recovery failure.",
            "Reusable code is limited to boundaries exercised by the offline run.",
            "The complete path produces an actionable local checkpoint without live-model scope.",
        ),
        accepted_frames=(
            "Validation before expansion",
            "Recovery integrity",
            "Completeness means protocol coverage rather than platform breadth",
        ),
        rejected_alternatives={
            "proposal-steward": "Its original single-fixture scope missed distinct halt and resume failures.",
            "proposal-vanguard": "Its original full sweep was insufficiently bounded.",
            "proposal-architect": "Its original reuse language could justify speculative architecture.",
            "proposal-castellan": "Its recovery strategy is incorporated but is not sufficient alone.",
        },
        minority_objections=(
            MinorityObjection(
                member_id="castellan",
                objection="Deterministic replay cannot prove live-provider interruption safety.",
                decision_impact="Live integration must remain isolated and reversible.",
                reconsideration_trigger="A live provider is introduced or provider calls gain side effects.",
            ),
        ),
        assumptions=(
            "Replay artifacts are adequate for validating process execution but not reasoning quality.",
        ),
        actions_requiring_authorization=(
            "Merge the completed Stage 4 implementation.",
            "Begin live-provider integration.",
        ),
        confidence=Decimal("0.9"),
    )


def _plan() -> ActionablePlan:
    return ActionablePlan(
        decision="Complete and review the bounded Stage 4 offline engine before any live-provider work.",
        objective="Prove that protocol 1.3 executes faithfully, halts safely, resumes deterministically, and produces an actionable plan.",
        immediate_next_action="Run the challenged synthetic fixture and inspect its exported session artifacts.",
        steps=(
            ActionStep(
                order=1,
                action="Run the complete offline challenged scenario in CI and locally.",
                owner="Imperium maintainer",
                completion_signal="The session reaches plan_complete and exports all required artifacts.",
            ),
            ActionStep(
                order=2,
                action="Run empty, conditional, waiting, paused, and interrupted acceptance paths.",
                owner="Imperium maintainer",
                dependencies=("Complete challenged scenario passes.",),
                completion_signal="Every path reaches its expected validated status without protocol bypasses.",
            ),
            ActionStep(
                order=3,
                action="Review transcript, lineage, minority objection, and actionable plan in chat.",
                owner="User",
                dependencies=("Synthetic artifacts are available.",),
                completion_signal="The user accepts, requests changes, or stops Stage 4.",
            ),
        ),
        checkpoints=(
            "All automated tests pass.",
            "The challenged fixture shows four distinct advocate profiles and direct debate turns.",
            "Resume produces the same final structured result as uninterrupted execution.",
        ),
        risks_and_mitigations={
            "Scripted artifacts may look more persuasive than the process deserves.": "Label outputs as synthetic and defer strategic-quality claims to controlled experiments.",
            "Live providers may not share replay idempotency.": "Keep the Castellan objection and isolate the first live-provider test.",
        },
        assumptions=("Protocol execution correctness is separable from live reasoning quality.",),
        decision_triggers=("Begin Stage 5 only after explicit user approval of Stage 4 artifacts.",),
        stop_or_reconsideration_conditions=(
            "Stop if any stage requires bypassing protocol 1.3 contracts.",
            "Reconsider the session design if resume diverges from uninterrupted output.",
            "Do not generalize replay crash guarantees to live providers without new evidence.",
        ),
    )


def build_challenged_scenario(
    *,
    evidence_outcome: EvidenceOutcome = EvidenceOutcome.GATHERED,
) -> OfflineScenario:
    """Return the primary multi-turn Stage 4 scenario or one evidence-halt variant."""

    if evidence_outcome is EvidenceOutcome.GATHERED:
        resolution = _gathered_resolution()
    elif evidence_outcome is EvidenceOutcome.PROCEED_CONDITIONALLY:
        resolution = EvidenceResolution(
            evidence_request_id="evidence-fixture-coverage",
            outcome=EvidenceOutcome.PROCEED_CONDITIONALLY,
            remaining_uncertainty=("The fixture matrix has not been independently evaluated.",),
            planning_conditions=(
                "Implement only the listed distinct fixtures and reconsider any new infrastructure request.",
            ),
        )
    elif evidence_outcome is EvidenceOutcome.USER_CLARIFICATION_REQUIRED:
        resolution = EvidenceResolution(
            evidence_request_id="evidence-fixture-coverage",
            outcome=EvidenceOutcome.USER_CLARIFICATION_REQUIRED,
            remaining_uncertainty=(
                "The user has not confirmed whether all halt fixtures are required before local review.",
            ),
        )
    else:
        resolution = EvidenceResolution(
            evidence_request_id="evidence-fixture-coverage",
            outcome=EvidenceOutcome.DELIBERATION_PAUSED,
            remaining_uncertainty=(
                "The scenario cannot responsibly choose implementation scope without a valid fixture boundary.",
            ),
        )

    return OfflineScenario(
        scenario_id=f"challenged-{evidence_outcome.value}",
        description="Multi-turn council scenario exercising direct debate and a revised-claim second round.",
        request=_request(),
        interpretations=_interpretations(),
        frame_register=_frame_register(),
        frame_rounds=(_frame_round(),),
        proposals=_proposals(),
        proposal_rounds=(_proposal_round_one(), _proposal_round_two()),
        proposal_evidence_resolutions=(resolution,),
        revisions=_revisions(),
        adjudication=_adjudication(),
        plan=_plan(),
    )


def build_no_challenge_scenario() -> OfflineScenario:
    """Return a complete scenario whose challenge stages correctly produce zero exchanges."""

    frame_claims = _frame_claims()
    frame_round = DebateRoundFixture(
        phase=ChallengePhase.FRAME,
        round_number=1,
        claim_register=frame_claims,
        claim_snapshot_round=0,
        plan=ChallengePlan(
            plan_id="frame-empty-plan",
            phase=ChallengePhase.FRAME,
            round_number=1,
            no_challenge_reason="The blind interpretations agree on the bounded validation decision.",
        ),
        continuation=ContinuationDecision(
            decision_id="frame-empty-stop",
            phase=ChallengePhase.FRAME,
            completed_round=1,
            continue_debate=False,
            stop_reason=StopReason.NO_MATERIAL_OPEN_ISSUES,
            justification="No material frame claim requires challenge.",
        ),
    )
    proposal_claims = _proposal_claims()
    proposal_round = DebateRoundFixture(
        phase=ChallengePhase.PROPOSAL,
        round_number=1,
        claim_register=proposal_claims,
        claim_snapshot_round=0,
        plan=ChallengePlan(
            plan_id="proposal-empty-plan",
            phase=ChallengePhase.PROPOSAL,
            round_number=1,
            no_challenge_reason="The synthetic proposals are treated as already reconciled for this cardinality fixture.",
        ),
        continuation=ContinuationDecision(
            decision_id="proposal-empty-stop",
            phase=ChallengePhase.PROPOSAL,
            completed_round=1,
            continue_debate=False,
            stop_reason=StopReason.NO_MATERIAL_OPEN_ISSUES,
            justification="No material proposal claim is contested in the empty-plan fixture.",
        ),
    )
    return OfflineScenario(
        scenario_id="no-material-challenge",
        description="Valid complete session with empty challenge plans and zero evidence requests.",
        request=_request(),
        interpretations=_interpretations(),
        frame_register=_frame_register(),
        frame_rounds=(frame_round,),
        proposals=_proposals(),
        proposal_rounds=(proposal_round,),
        revisions=_revisions(),
        adjudication=_adjudication(),
        plan=_plan(),
    )


def scenario_by_name(name: str) -> OfflineScenario:
    """Resolve the stable CLI scenario names."""

    scenarios = {
        "challenged": build_challenged_scenario(),
        "empty": build_no_challenge_scenario(),
        "conditional": build_challenged_scenario(
            evidence_outcome=EvidenceOutcome.PROCEED_CONDITIONALLY
        ),
        "waiting": build_challenged_scenario(
            evidence_outcome=EvidenceOutcome.USER_CLARIFICATION_REQUIRED
        ),
        "paused": build_challenged_scenario(
            evidence_outcome=EvidenceOutcome.DELIBERATION_PAUSED
        ),
    }
    try:
        return scenarios[name]
    except KeyError as exc:
        raise ValueError(f"unknown offline scenario {name!r}; choose {sorted(scenarios)}") from exc
