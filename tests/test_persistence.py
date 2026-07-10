"""Tests for inspectable JSON session records."""

from imperium.domain.models import DeliberationRecord
from imperium.persistence.export import export_record, load_record


def test_record_round_trip(tmp_path, request, member) -> None:
    record = DeliberationRecord(
        request=request,
        member_snapshots=(member,),
        selected_member_ids=(member.member_id,),
    )
    destination = tmp_path / "runs" / record.session_id / "record.json"

    written = export_record(record, destination)
    loaded = load_record(written)

    assert written == destination
    assert loaded == record
    assert destination.read_text(encoding="utf-8").endswith("\n")
