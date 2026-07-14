"""Atomic checkpoint and review-artifact persistence for Stage 4."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from imperium.engine.record_validation import validate_deliberation_record
from imperium.offline.models import OfflineSession
from imperium.offline.render import render_transcript


def _atomic_write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="\n",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        temporary.write(content)
        if not content.endswith("\n"):
            temporary.write("\n")
        temporary_path = Path(temporary.name)
    try:
        os.replace(temporary_path, path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    return path


def _json_text(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str)


def session_path(output_dir: str | Path) -> Path:
    return Path(output_dir) / "session.json"


def write_checkpoint(session: OfflineSession, output_dir: str | Path) -> Path:
    """Atomically persist the authoritative resumable session envelope."""

    validate_deliberation_record(session.record)
    return _atomic_write_text(
        session_path(output_dir),
        session.model_dump_json(indent=2),
    )


def load_session(source: str | Path) -> OfflineSession:
    """Load and validate one authoritative Stage 4 session envelope."""

    payload = json.loads(Path(source).read_text(encoding="utf-8"))
    session = OfflineSession.model_validate(payload)
    validate_deliberation_record(session.record)
    return session


def write_review_artifacts(session: OfflineSession, output_dir: str | Path) -> tuple[Path, ...]:
    """Write all synthetic review views derived from authoritative structured state."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    written = [write_checkpoint(session, destination)]
    written.append(
        _atomic_write_text(
            destination / "record.json",
            session.record.model_dump_json(indent=2),
        )
    )
    written.append(
        _atomic_write_text(
            destination / "protocol_trace.json",
            session.protocol_trace.model_dump_json(indent=2),
        )
    )
    written.append(
        _atomic_write_text(
            destination / "manifest.json",
            session.runtime.model_dump_json(indent=2),
        )
    )
    written.append(
        _atomic_write_text(
            destination / "lineage.json",
            _json_text(
                {
                    "turns": [turn.model_dump(mode="json") for turn in session.turns],
                    "evidence_history": [
                        event.model_dump(mode="json") for event in session.evidence_history
                    ],
                    "lineage": [link.model_dump(mode="json") for link in session.lineage],
                }
            ),
        )
    )
    written.append(_atomic_write_text(destination / "transcript.md", render_transcript(session)))
    if session.record.plan is not None:
        written.append(
            _atomic_write_text(
                destination / "plan.json",
                session.record.plan.model_dump_json(indent=2),
            )
        )
    return tuple(written)
