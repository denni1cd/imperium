"""Human-inspectable JSON export for deliberation sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from imperium.domain.models import DeliberationRecord


def export_record(record: DeliberationRecord, destination: str | Path) -> Path:
    """Atomically write a complete deliberation record as formatted JSON."""
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
    return DeliberationRecord.model_validate(payload)
