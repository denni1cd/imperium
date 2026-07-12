"""Cross-artifact validation for authoritative deliberation records."""

from __future__ import annotations

from imperium.domain.enums import DeliberationStage, SessionStatus
from imperium.domain.models import DeliberationRecord


class InvalidDeliberationRecord(ValueError):
    """Raised when a record contains contradictory or unauditable state."""


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_deliberation_record(record: DeliberationRecord) -> None:
    """Reject contradictions that would make a saved session unreliable.

    Protocol 1.2 keeps authored challenge artifacts solely in the attached
    ``ProtocolTrace``. The legacy ``DeliberationRecord.challenges`` field is a
    compatibility field and must remain empty so two challenge histories cannot
    diverge.
    """

    snapshot_ids = [member.member_id for member in record.member_snapshots]
    duplicate_snapshots = _duplicates(snapshot_ids)
    if duplicate_snapshots:
        raise InvalidDeliberationRecord(
            f"member profile snapshots must have unique ids: {sorted(duplicate_snapshots)}"
        )

    selected_ids = list(record.selected_member_ids)
    duplicate_selected = _duplicates(selected_ids)
    if duplicate_selected:
        raise InvalidDeliberationRecord(
            f"selected council member ids must be unique: {sorted(duplicate_selected)}"
        )

    available = set(snapshot_ids)
    missing_snapshots = set(selected_ids) - available
    if missing_snapshots:
        raise InvalidDeliberationRecord(
            f"selected members are missing profile snapshots: {sorted(missing_snapshots)}"
        )

    interpretation_ids = [item.member_id for item in record.interpretations]
    duplicate_interpretations = _duplicates(interpretation_ids)
    if duplicate_interpretations:
        raise InvalidDeliberationRecord(
            "each member may have only one blind interpretation: "
            f"{sorted(duplicate_interpretations)}"
        )

    unselected_interpreters = set(interpretation_ids) - set(selected_ids)
    if unselected_interpreters:
        raise InvalidDeliberationRecord(
            "interpretations may only come from selected council members: "
            f"{sorted(unselected_interpreters)}"
        )

    if record.challenges:
        raise InvalidDeliberationRecord(
            "legacy DeliberationRecord challenges must remain empty; "
            "protocol 1.2 stores canonical authored challenges in ProtocolTrace"
        )

    if record.stage is DeliberationStage.PLAN_COMPLETE:
        if record.plan is None:
            raise InvalidDeliberationRecord(
                "a plan-complete record must contain an actionable plan"
            )
        if record.status is not SessionStatus.COMPLETE:
            raise InvalidDeliberationRecord(
                "a plan-complete record must have complete session status"
            )

    if record.status is SessionStatus.COMPLETE:
        if record.stage is not DeliberationStage.PLAN_COMPLETE or record.plan is None:
            raise InvalidDeliberationRecord(
                "a complete session must be at plan_complete with an actionable plan"
            )
