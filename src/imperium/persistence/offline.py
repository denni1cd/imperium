"""Atomic persistence for complete or interrupted Stage 4 sessions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from imperium.domain.offline import OfflineDeliberationSession
from imperium.engine.lifecycle import LifecycleState
from imperium.engine.record_validation import validate_deliberation_record


def validate_offline_session(session: OfflineDeliberationSession) -> None:
    """Validate lifecycle continuity and the embedded deliberation record."""

    LifecycleState(stage=session.record.stage, history=session.lifecycle_history)
    validate_deliberation_record(session.record)
    OfflineDeliberationSession.model_validate(session.model_dump(mode="json"))


def export_offline_session(
    session: OfflineDeliberationSession,
    destination: str | Path,
) -> Path:
    """Atomically persist enough state to inspect or resume the deliberation."""

    validate_offline_session(session)
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = session.model_dump_json(indent=2)

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


def load_offline_session(source: str | Path) -> OfflineDeliberationSession:
    """Load and validate a checkpoint for deterministic resume."""

    path = Path(source)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    session = OfflineDeliberationSession.model_validate(payload)
    validate_offline_session(session)
    return session
