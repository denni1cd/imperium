"""Human-inspectable JSON export for deliberation sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from imperium.domain.models import DeliberationRecord
from imperium.engine.record_validation import validate_deliberation_record


def export_record(record: DeliberationRecord, destination: str | Path) -> Path:
    """Atomically write a complete, internally consistent deliberation record."""

    validate_deliberation_record(record)

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = record.model_dump_json(indent=2)

    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(payload)
        temporary.write("\n")
        temporary_path = Path(temporary.name)

    try:
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return path


def load_record(source: str | Path) -> DeliberationRecord:
    """Load and validate an exported deliberation record."""

    path = Path(source)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    record = DeliberationRecord.model_validate(payload)
    validate_deliberation_record(record)
    return record
