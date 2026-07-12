"""Verify that an Imperium run contains actual multi-turn confrontation."""

from __future__ import annotations

from pydantic import model_validator

from imperium.domain.enums import ChallengePhase
from imperium.domain.models import NonEmptyStr, StrictModel
from imperium.domain.offline import OfflineDeliberationSession


class DebateVerificationReport(StrictModel):
    """Inspectable proof that a run did more than aggregate independent submissions."""

    passed: bool
    direct_exchange_count: int
    consequential_impact_count: int
    phases_with_direct_exchange: tuple[ChallengePhase, ...]
    targeted_members: tuple[NonEmptyStr, ...]
    failures: tuple[NonEmptyStr, ...] = ()

    @model_validator(mode="after")
    def status_matches_failures(self) -> "DebateVerificationReport":
        if self.passed and self.failures:
            raise ValueError("a passing debate report cannot contain failures")
        if not self.passed and not self.failures:
            raise ValueError("a failing debate report must explain what is missing")
        return self


class DebateVerificationError(ValueError):
    """Raised when a completed full-protocol session contains no real debate."""


def verify_actual_debate(
    session: OfflineDeliberationSession,
    *,
    require_both_phases: bool = True,
    minimum_targeted_members: int = 2,
) -> DebateVerificationReport:
    """Require direct cross-member challenges, responses, and later consequences.

    A challenge plan alone does not count. Every planned assignment must have a direct
    challenger articulation, a response from the targeted advocate, and a traceable
    consequence in that advocate's later proposal or revision.
    """

    if minimum_targeted_members < 1:
        raise ValueError("minimum_targeted_members must be at least one")

    failures: list[str] = []
    exchanges = session.debate_exchanges
    impacts = session.debate_impacts
    exchange_by_id = {exchange.exchange_id: exchange for exchange in exchanges}
    impacts_by_exchange: dict[str, list] = {}
    for impact in impacts:
        impacts_by_exchange.setdefault(impact.exchange_id, []).append(impact)

    planned_assignments = {
        assignment.challenge_id: assignment
        for plan in session.protocol_trace.challenge_plans
        for assignment in plan.assignments
    }
    missing_exchanges = set(planned_assignments) - set(exchange_by_id)
    if missing_exchanges:
        failures.append(
            "planned challenges without direct challenger/target exchange: "
            f"{sorted(missing_exchanges)}"
        )

    unexpected_exchanges = set(exchange_by_id) - set(planned_assignments)
    if unexpected_exchanges:
        failures.append(
            "direct exchanges without a validated challenge assignment: "
            f"{sorted(unexpected_exchanges)}"
        )

    missing_impacts = {
        exchange_id
        for exchange_id in exchange_by_id
        if not impacts_by_exchange.get(exchange_id)
    }
    if missing_impacts:
        failures.append(
            "direct exchanges with no later strategic consequence: "
            f"{sorted(missing_impacts)}"
        )

    for exchange_id, exchange in exchange_by_id.items():
        if exchange.challenge.challenger_member_id == exchange.response.member_id:
            failures.append(
                f"exchange {exchange_id!r} was not cross-member confrontation"
            )
        for impact in impacts_by_exchange.get(exchange_id, []):
            if impact.member_id != exchange.assignment.target_member_id:
                failures.append(
                    f"exchange {exchange_id!r} impact was not recorded by the challenged member"
                )

    phases = tuple(sorted({exchange.phase for exchange in exchanges}, key=lambda item: item.value))
    if not exchanges:
        failures.append("no direct cross-member debate exchanges were recorded")
    if require_both_phases:
        required = {ChallengePhase.FRAME, ChallengePhase.PROPOSAL}
        missing_phases = required - set(phases)
        if missing_phases:
            failures.append(
                "full protocol requires direct confrontation in both debate phases; "
                f"missing: {sorted(phase.value for phase in missing_phases)}"
            )

    targeted_members = tuple(
        sorted({exchange.assignment.target_member_id for exchange in exchanges})
    )
    if len(targeted_members) < minimum_targeted_members:
        failures.append(
            "debate must confront at least "
            f"{minimum_targeted_members} distinct advocate(s)"
        )

    return DebateVerificationReport(
        passed=not failures,
        direct_exchange_count=len(exchanges),
        consequential_impact_count=len(impacts),
        phases_with_direct_exchange=phases,
        targeted_members=targeted_members,
        failures=tuple(failures),
    )


def require_actual_debate(
    session: OfflineDeliberationSession,
    *,
    require_both_phases: bool = True,
    minimum_targeted_members: int = 2,
) -> DebateVerificationReport:
    """Return a passing report or reject a panel-only/session-summary substitute."""

    report = verify_actual_debate(
        session,
        require_both_phases=require_both_phases,
        minimum_targeted_members=minimum_targeted_members,
    )
    if not report.passed:
        raise DebateVerificationError("; ".join(report.failures))
    return report
