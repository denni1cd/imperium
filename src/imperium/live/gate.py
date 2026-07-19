"""Full-council Stage 5 Gate 2F runner and manifesto-aligned assessment."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import Field

from imperium.domain.enums import ChallengeDisposition, DeliberationStage, SessionStatus
from imperium.domain.models import EvidenceResolution, NonEmptyStr, StrictModel
from imperium.live.capture import (
    capture_completed_session,
    load_capture,
    verify_replay_equivalence,
    write_capture,
)
from imperium.live.gate_case import build_live_council_scenario
from imperium.offline.attempts import UsageBudget, usage_totals
from imperium.offline.models import OfflineSession
from imperium.offline.persistence import _atomic_write_text
from imperium.offline.provider_engine import ProviderBoundDeliberationEngine
from imperium.offline.replay_script import build_replay_records
from imperium.providers.codex_cli import DEFAULT_CODEX_MODEL, CodexCliProvider
from imperium.providers.replay import ReplayProvider

LIVE_AUTHORIZATION = "RUN_FULL_COUNCIL"


class GateCheck(StrictModel):
    name: NonEmptyStr
    passed: bool
    detail: NonEmptyStr


class CouncilGateAssessment(StrictModel):
    """Automated process checks; strategic quality still requires human review."""

    session_id: NonEmptyStr
    checks: tuple[GateCheck, ...]
    structural_pass: bool
    human_review_required: bool = True
    human_review_focus: tuple[NonEmptyStr, ...] = (
        "Were the perspectives genuinely distinct rather than differently worded?",
        "Did a challenge materially improve, narrow, defend, concede, or withdraw a position?",
        "Is the chosen or hybrid strategy stronger than simple aggregation?",
        "Does the final plan faithfully preserve intent, constraints, objections, and "
        "revision triggers?",
    )


def assess_council_session(session: OfflineSession) -> CouncilGateAssessment:
    """Reject completion-only runs while leaving substantive judgment explicit."""

    advocate_ids = session.runtime.council.advocate_member_ids
    interpretation_ids = tuple(item.member_id for item in session.record.interpretations)
    proposal_ids = tuple(item.member_id for item in session.record.proposals)
    revision_ids = tuple(item.member_id for item in session.record.revisions)
    challenges = session.protocol_trace.challenges
    responses = session.record.challenge_responses
    consequential_responses = tuple(
        response
        for response in responses
        if response.disposition
        in {
            ChallengeDisposition.REFINE,
            ChallengeDisposition.CONCEDE,
            ChallengeDisposition.WITHDRAW,
            ChallengeDisposition.REQUEST_EVIDENCE,
        }
    )
    proposals = {item.proposal_id: item for item in session.record.proposals}
    changed_revisions = tuple(
        revision
        for revision in session.record.revisions
        if revision.changes
        or revision.concessions
        or revision.supporting_evidence
        or revision.revised_proposal != proposals.get(revision.original_proposal_id)
    )
    interpretation_turns = tuple(
        turn for turn in session.turns if turn.output_type == "Interpretation"
    )
    blind_interpretations = all(
        turn.profile_member_id == turn.member_id
        and not any(
            kind in {"interpretation", "council_snapshot"} for kind in turn.visible_artifact_kinds
        )
        for turn in interpretation_turns
    )
    adjudication = session.record.adjudication
    plan = session.record.plan

    checks = (
        GateCheck(
            name="complete full lifecycle",
            passed=(
                session.status is SessionStatus.COMPLETE
                and session.record.stage is DeliberationStage.PLAN_COMPLETE
            ),
            detail=f"status={session.status.value}, stage={session.record.stage.value}",
        ),
        GateCheck(
            name="fixed four-advocate council",
            passed=(
                interpretation_ids == advocate_ids
                and proposal_ids == advocate_ids
                and revision_ids == advocate_ids
            ),
            detail=(
                f"expected={list(advocate_ids)}, interpretations={list(interpretation_ids)}, "
                f"proposals={list(proposal_ids)}, revisions={list(revision_ids)}"
            ),
        ),
        GateCheck(
            name="blind independent interpretations",
            passed=(len(interpretation_turns) == len(advocate_ids) and blind_interpretations),
            detail=f"validated {len(interpretation_turns)} isolated interpretation turns",
        ),
        GateCheck(
            name="member-authored debate exchange",
            passed=(bool(challenges) and len(challenges) == len(responses)),
            detail=f"challenges={len(challenges)}, responses={len(responses)}",
        ),
        GateCheck(
            name="recorded consequential response",
            passed=bool(consequential_responses),
            detail=(
                f"{len(consequential_responses)} responses refined, conceded, withdrew, "
                "or requested decision-relevant evidence"
            ),
        ),
        GateCheck(
            name="post-debate material revision signal",
            passed=bool(changed_revisions),
            detail=f"{len(changed_revisions)} revisions recorded changes, concessions, or evidence",
        ),
        GateCheck(
            name="reasoned Seneschal adjudication",
            passed=bool(
                adjudication
                and adjudication.decisive_reasons
                and adjudication.rejected_alternatives
            ),
            detail=(
                "adjudication includes decisive reasons and rejected alternatives"
                if adjudication
                else "adjudication is missing"
            ),
        ),
        GateCheck(
            name="actionable council result",
            passed=bool(
                plan
                and plan.steps
                and plan.immediate_next_action
                and plan.stop_or_reconsideration_conditions
            ),
            detail=(
                f"steps={len(plan.steps) if plan else 0}; immediate action and stop conditions "
                "required"
            ),
        ),
    )
    return CouncilGateAssessment(
        session_id=session.session_id,
        checks=checks,
        structural_pass=all(check.passed for check in checks),
    )


class CouncilGateRun(StrictModel):
    session_id: NonEmptyStr
    call_count: Annotated[int, Field(ge=0)]
    input_tokens: Annotated[int, Field(ge=0)]
    cached_input_tokens: Annotated[int, Field(ge=0)]
    output_tokens: Annotated[int, Field(ge=0)]
    assessment: CouncilGateAssessment
    capture_path: NonEmptyStr
    replay_verified: bool


async def _finalize_completed_gate(
    *,
    session: OfflineSession,
    project_root: Path,
    destination: Path,
) -> CouncilGateRun:
    assessment = assess_council_session(session)
    if not assessment.structural_pass:
        failed = [check.name for check in assessment.checks if not check.passed]
        raise ValueError(f"live council failed automated gate checks: {failed}")

    capture = capture_completed_session(session)
    capture_path = write_capture(capture, destination / "accepted-replay.json")
    replay = await replay_council_capture(
        project_root=project_root,
        capture_path=capture_path,
        output_dir=destination / "replay",
    )
    verify_replay_equivalence(session, replay)
    totals = usage_totals(session.attempts)
    result = CouncilGateRun(
        session_id=session.session_id,
        call_count=len(session.completed_call_keys),
        input_tokens=totals.input_tokens,
        cached_input_tokens=totals.cached_input_tokens,
        output_tokens=totals.output_tokens,
        assessment=assessment,
        capture_path=str(capture_path),
        replay_verified=True,
    )
    _atomic_write_text(
        destination / "gate-result.json",
        result.model_dump_json(indent=2),
    )
    return result


class CouncilGateEstimate(StrictModel):
    """Provider-free expected-path estimate plus the protocol call ceiling."""

    expected_path_calls: Annotated[int, Field(ge=0)]
    protocol_call_ceiling: Annotated[int, Field(ge=0)]
    estimated_input_tokens: Annotated[int, Field(ge=0)]
    reserved_output_tokens: Annotated[int, Field(ge=0)]
    note: NonEmptyStr


async def estimate_council_gate(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    usage_budget: UsageBudget,
) -> CouncilGateEstimate:
    """Exercise the expected call graph through replay without invoking Codex."""

    scenario = build_live_council_scenario()
    provider = ReplayProvider(build_replay_records(scenario, model=DEFAULT_CODEX_MODEL))
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model=DEFAULT_CODEX_MODEL,
        usage_budget=usage_budget,
    ).run(
        scenario,
        project_root=project_root,
        output_dir=output_dir,
    )
    estimate = CouncilGateEstimate(
        expected_path_calls=len(session.attempts),
        protocol_call_ceiling=59,
        estimated_input_tokens=sum(item.estimated_input_tokens for item in session.attempts),
        reserved_output_tokens=(
            len(session.attempts) * usage_budget.output_token_reserve_per_attempt
        ),
        note=(
            "Expected-path estimates use schema-exemplar routing. Live debate may choose a "
            "different valid path, while persisted usage budgets remain authoritative."
        ),
    )
    _atomic_write_text(
        Path(output_dir) / "gate-estimate.json",
        estimate.model_dump_json(indent=2),
    )
    return estimate


async def replay_council_capture(
    *,
    project_root: str | Path,
    capture_path: str | Path,
    output_dir: str | Path,
) -> OfflineSession:
    """Replay a completed capture through ReplayProvider and make no Codex calls."""

    capture = load_capture(capture_path)
    provider = ReplayProvider(capture.replay_records())
    scenario = build_live_council_scenario()
    engine = ProviderBoundDeliberationEngine(
        provider=provider,
        model=DEFAULT_CODEX_MODEL,
        usage_budget=capture.usage_budget,
    )
    session = await engine.run(
        scenario,
        project_root=project_root,
        output_dir=output_dir,
    )
    if len(provider.calls) != len(capture.calls):
        raise ValueError("replay did not consume every captured call exactly once")
    if session.scenario_sha256 != capture.scenario_sha256:
        raise ValueError("capture does not belong to the frozen live-council scenario")
    return session


async def run_live_council_gate(
    *,
    project_root: str | Path,
    output_dir: str | Path,
    authorization: str,
    usage_budget: UsageBudget,
    executable: str = "codex",
    timeout_seconds: float = 300.0,
) -> CouncilGateRun:
    """Run the complete council once, capture it, and prove provider-free replay."""

    if authorization != LIVE_AUTHORIZATION:
        raise ValueError(
            f"live full-council execution requires authorization={LIVE_AUTHORIZATION!r}"
        )
    root = Path(project_root).resolve()
    destination = Path(output_dir).resolve()
    live_dir = destination / "live"
    provider = CodexCliProvider(
        executable=executable,
        timeout_seconds=timeout_seconds,
        event_log_dir=live_dir / "events",
    )
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model=DEFAULT_CODEX_MODEL,
        usage_budget=usage_budget,
    ).run(
        build_live_council_scenario(),
        project_root=root,
        output_dir=live_dir,
    )
    return await _finalize_completed_gate(
        session=session,
        project_root=root,
        destination=destination,
    )


async def resume_live_council_evidence(
    *,
    project_root: str | Path,
    gate_dir: str | Path,
    checkpoint: str | Path,
    authorization: str,
    evidence_replacements: tuple[EvidenceResolution, ...],
    executable: str = "codex",
    timeout_seconds: float = 300.0,
) -> CouncilGateRun:
    """Resume a halted live gate with exact operator-supplied evidence dispositions."""

    if authorization != LIVE_AUTHORIZATION:
        raise ValueError(
            f"live full-council execution requires authorization={LIVE_AUTHORIZATION!r}"
        )
    root = Path(project_root).resolve()
    destination = Path(gate_dir).resolve()
    provider = CodexCliProvider(
        executable=executable,
        timeout_seconds=timeout_seconds,
        event_log_dir=destination / "live" / "events",
    )
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model=DEFAULT_CODEX_MODEL,
    ).resume(
        checkpoint,
        output_dir=destination / "live",
        evidence_replacements=evidence_replacements,
    )
    return await _finalize_completed_gate(
        session=session,
        project_root=root,
        destination=destination,
    )


async def retry_live_council_attempt(
    *,
    project_root: str | Path,
    gate_dir: str | Path,
    checkpoint: str | Path,
    authorization: str,
    reason: str,
    executable: str = "codex",
    timeout_seconds: float = 300.0,
) -> CouncilGateRun:
    """Explicitly authorize one replacement attempt, then continue the live gate."""

    if authorization != LIVE_AUTHORIZATION:
        raise ValueError(
            f"live full-council execution requires authorization={LIVE_AUTHORIZATION!r}"
        )
    root = Path(project_root).resolve()
    destination = Path(gate_dir).resolve()
    provider = CodexCliProvider(
        executable=executable,
        timeout_seconds=timeout_seconds,
        event_log_dir=destination / "live" / "events",
    )
    session = await ProviderBoundDeliberationEngine(
        provider=provider,
        model=DEFAULT_CODEX_MODEL,
    ).retry_attempt(
        checkpoint,
        reason=reason,
        output_dir=destination / "live",
    )
    return await _finalize_completed_gate(
        session=session,
        project_root=root,
        destination=destination,
    )
