"""Derived human-readable and machine-readable Stage 4 views."""

from __future__ import annotations

from imperium.offline.models import OfflineSession


def render_transcript(session: OfflineSession) -> str:
    """Render a concise transcript from authoritative structured artifacts."""

    record = session.record
    lines = [
        "# Imperium Offline Deliberation",
        "",
        f"- Session: `{session.session_id}`",
        f"- Scenario: `{session.scenario.scenario_id}`",
        f"- Protocol: `{session.runtime.protocol.version}`",
        f"- Stage: `{record.stage.value}`",
        f"- Status: `{record.status.value}`",
        "",
        "## Sovereign Request",
        "",
        record.request.original_text,
        "",
        "## Blind Interpretations",
        "",
    ]

    profiles = {member.member_id: member for member in record.member_snapshots}
    for interpretation in record.interpretations:
        profile = profiles[interpretation.member_id]
        label = profile.presentation.get("label", profile.title)
        lines.extend(
            [
                f"### {label}",
                "",
                f"**Core decision:** {interpretation.core_decision}",
                "",
                f"**Initial inclination:** {interpretation.initial_inclination}",
                "",
            ]
        )

    if record.proposals:
        lines.extend(["## Initial Strategies", ""])
        for proposal in record.proposals:
            label = profiles[proposal.member_id].presentation.get(
                "label", profiles[proposal.member_id].title
            )
            lines.extend(
                [
                    f"### {label}: {proposal.title}",
                    "",
                    proposal.summary,
                    "",
                ]
            )

    if session.protocol_trace.challenges:
        lines.extend(["## Debate", ""])
        responses = {response.challenge_id: response for response in record.challenge_responses}
        for challenge in session.protocol_trace.challenges:
            challenger = profiles[challenge.challenger_member_id].presentation.get(
                "label", challenge.challenger_member_id
            )
            target = profiles[challenge.target_member_id].presentation.get(
                "label", challenge.target_member_id
            )
            response = responses.get(challenge.challenge_id)
            lines.extend(
                [
                    f"### {challenger} → {target}",
                    "",
                    challenge.statement,
                    "",
                ]
            )
            if response is not None:
                lines.extend(
                    [
                        f"**Response ({response.disposition.value}):** {response.response}",
                        "",
                    ]
                )

    if record.revisions:
        lines.extend(["## Final Advocate Positions", ""])
        for revision in record.revisions:
            label = profiles[revision.member_id].presentation.get(
                "label", revision.member_id
            )
            lines.extend(
                [
                    f"### {label}",
                    "",
                    revision.revised_proposal.summary,
                    "",
                    f"**Reasoning:** {'; '.join(revision.reasons)}",
                    "",
                ]
            )

    if record.adjudication is not None:
        lines.extend(
            [
                "## Seneschal Adjudication",
                "",
                record.adjudication.chosen_strategy,
                "",
                "**Decisive reasons:**",
                "",
            ]
        )
        lines.extend(f"- {reason}" for reason in record.adjudication.decisive_reasons)
        lines.append("")
        if record.adjudication.minority_objections:
            lines.extend(["**Preserved minority objections:**", ""])
            lines.extend(
                f"- {objection.objection} — reconsider when {objection.reconsideration_trigger}"
                for objection in record.adjudication.minority_objections
            )
            lines.append("")

    if record.plan is not None:
        lines.extend(
            [
                "## Actionable Plan",
                "",
                f"**Decision:** {record.plan.decision}",
                "",
                f"**Immediate next action:** {record.plan.immediate_next_action}",
                "",
            ]
        )
        for step in record.plan.steps:
            owner = f" — {step.owner}" if step.owner else ""
            lines.append(f"{step.order}. {step.action}{owner}")
        lines.append("")
        lines.extend(["**Stop or reconsider when:**", ""])
        lines.extend(
            f"- {condition}" for condition in record.plan.stop_or_reconsideration_conditions
        )
        lines.append("")

    if record.status.value in {"waiting_for_user", "paused", "failed"}:
        lines.extend(["## Halted State", ""])
        if record.evidence_resolutions:
            latest = record.evidence_resolutions[-1]
            lines.append(
                f"Evidence request `{latest.evidence_request_id}` ended with "
                f"`{latest.outcome.value}`."
            )
        if session.failure_reason:
            lines.append(session.failure_reason)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
