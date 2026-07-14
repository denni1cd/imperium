"""Focused integrity tests for Stage 4 frozen runtime and context inspection."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from imperium.engine.context import ContextBuilder
from imperium.offline.engine import OfflineDeliberationEngine
from imperium.offline.fixtures import build_challenged_scenario
from imperium.offline.models import FrozenTextArtifact, OfflineSession
from imperium.offline.persistence import load_session
from imperium.offline.runtime import freeze_runtime, text_sha256


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_source_rejects_content_digest_mismatch() -> None:
    with pytest.raises(ValidationError, match="digest does not match"):
        FrozenTextArtifact(
            path="prompts/example.md",
            sha256=text_sha256("original"),
            content="tampered",
        )


def test_offline_session_rejects_tampered_scenario_digest() -> None:
    runtime = freeze_runtime(ROOT)
    scenario = build_challenged_scenario()
    session = OfflineSession(
        session_id="offline-test",
        scenario=scenario,
        runtime=runtime,
        record={
            "session_id": "offline-test",
            "request": scenario.request.model_dump(mode="json"),
        },
    )
    payload = session.model_dump(mode="json")
    payload["scenario"]["description"] = "tampered scenario"

    with pytest.raises(ValidationError, match="scenario digest"):
        OfflineSession.model_validate(payload)


def test_advocate_context_serializes_complete_approved_profile() -> None:
    runtime = freeze_runtime(ROOT)
    member = runtime.council.advocates[0]
    scenario = build_challenged_scenario()
    context = ContextBuilder.independent_interpretation(scenario.request, member)
    payload = json.loads(context.model_dump_json())

    assert payload["member"]["member_id"] == member.member_id
    assert payload["member"]["operating_constraints"] == list(member.operating_constraints)
    assert payload["member"]["role"] == member.role.value
    assert payload["member"]["profile_version"] == member.profile_version


def test_load_session_rejects_malformed_checkpoint(tmp_path: Path) -> None:
    checkpoint = tmp_path / "session.json"
    checkpoint.write_text('{"session_id": "broken"}\n', encoding="utf-8")

    with pytest.raises(ValidationError):
        load_session(checkpoint)


@pytest.mark.asyncio
async def test_checkpoint_rejects_tampered_accepted_replay_artifact(
    tmp_path: Path,
) -> None:
    session = await OfflineDeliberationEngine().run(
        build_challenged_scenario(),
        project_root=ROOT,
        output_dir=tmp_path / "session",
    )
    payload = session.model_dump(mode="json")
    payload["record"]["interpretations"][0]["core_decision"] = "tampered result"

    with pytest.raises(ValidationError, match="frozen scenario"):
        OfflineSession.model_validate(payload)
