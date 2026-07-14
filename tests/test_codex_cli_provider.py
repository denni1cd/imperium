"""Tests for the bounded Stage 5 Codex CLI provider gate."""

from __future__ import annotations

import json
from pathlib import Path, PureWindowsPath

import pytest

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import Interpretation
from imperium.live.smoke import run_codex_smoke
from imperium.providers import codex_cli
from imperium.providers.base import CallMetadata, ModelResult, ProviderError
from imperium.providers.codex_cli import CodexCliProvider, _ProcessResult


def _interpretation_payload() -> dict[str, object]:
    return {
        "interpretation_id": "live-smoke-interpretation",
        "member_id": "steward",
        "core_decision": "Whether one isolated live call is justified before broader testing.",
        "desired_outcome": "A bounded evidence-producing next step.",
        "opportunities": ["Validate structured live generation."],
        "risks": ["A successful call could be overgeneralized."],
        "assumptions": ["The CLI can honor the supplied schema and isolated context."],
        "missing_information": [],
        "initial_inclination": "Run one isolated call and stop for review.",
        "value_influence": {"economy": "Limit spending until the provider boundary works."},
        "confidence": "0.76",
    }


@pytest.mark.asyncio
async def test_codex_provider_builds_isolated_command_and_validates_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = CodexCliProvider(timeout_seconds=30, event_log_dir=tmp_path / "events")
    monkeypatch.setattr(provider, "_resolve_executable", lambda: "/usr/bin/codex")
    observed: dict[str, object] = {}

    async def fake_run(command: list[str], *, input_text: str) -> _ProcessResult:
        observed["command"] = command
        observed["input"] = input_text
        schema_path = Path(command[command.index("--output-schema") + 1])
        output_path = Path(command[command.index("--output-last-message") + 1])
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        assert schema["title"] == "Interpretation"
        output_path.write_text(json.dumps(_interpretation_payload()), encoding="utf-8")
        return _ProcessResult(
            returncode=0,
            stdout=(
                '{"type":"thread.started","thread_id":"thread-123","model":"gpt-test"}\n'
                '{"type":"turn.completed","usage":{"input_tokens":321,"output_tokens":87}}\n'
            ),
            stderr="",
        )

    monkeypatch.setattr(provider, "_run_process", fake_run)
    result = await provider.generate(
        model="gpt-test",
        instructions="Interpret the request independently.",
        input_text='{"member":{"member_id":"steward"}}',
        output_type=Interpretation,
        metadata=CallMetadata(
            session_id="smoke",
            call_key="smoke:steward",
            stage=DeliberationStage.COUNCIL_SELECTED,
            member_id="steward",
        ),
    )

    command = observed["command"]
    assert isinstance(command, list)
    assert "--ephemeral" in command
    assert "--ignore-rules" in command
    assert "--ignore-user-config" in command
    assert "--sandbox" in command
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert "--skip-git-repo-check" in command
    assert command[-1] == "-"
    assert "Do not inspect files" in str(observed["input"])
    assert result.output.member_id == "steward"
    assert result.provider == "codex-cli"
    assert result.model == "gpt-test"
    assert result.response_id == "thread-123"
    assert result.input_tokens == 321
    assert result.output_tokens == 87
    assert result.retries == 0
    assert (tmp_path / "events" / "smoke_steward.jsonl").exists()


@pytest.mark.asyncio
async def test_codex_provider_preserves_nonzero_exit_without_retry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = CodexCliProvider(timeout_seconds=30)
    monkeypatch.setattr(provider, "_resolve_executable", lambda: "/usr/bin/codex")

    async def fake_run(command: list[str], *, input_text: str) -> _ProcessResult:
        del command, input_text
        return _ProcessResult(returncode=17, stdout="", stderr="authentication required")

    monkeypatch.setattr(provider, "_run_process", fake_run)
    with pytest.raises(ProviderError, match="exited with code 17"):
        await provider.generate(
            model="",
            instructions="Interpret.",
            input_text="{}",
            output_type=Interpretation,
            metadata=CallMetadata(
                session_id="smoke",
                call_key="smoke:failure",
                stage=DeliberationStage.COUNCIL_SELECTED,
                member_id="steward",
            ),
        )


@pytest.mark.asyncio
async def test_codex_provider_rejects_invalid_structured_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = CodexCliProvider(timeout_seconds=30)
    monkeypatch.setattr(provider, "_resolve_executable", lambda: "/usr/bin/codex")

    async def fake_run(command: list[str], *, input_text: str) -> _ProcessResult:
        del input_text
        output_path = Path(command[command.index("--output-last-message") + 1])
        output_path.write_text('{"member_id":"steward"}', encoding="utf-8")
        return _ProcessResult(returncode=0, stdout="{}\n", stderr="")

    monkeypatch.setattr(provider, "_run_process", fake_run)
    with pytest.raises(ProviderError, match="does not match Interpretation"):
        await provider.generate(
            model="",
            instructions="Interpret.",
            input_text="{}",
            output_type=Interpretation,
            metadata=CallMetadata(
                session_id="smoke",
                call_key="smoke:invalid",
                stage=DeliberationStage.COUNCIL_SELECTED,
                member_id="steward",
            ),
        )


def test_windows_cmd_launcher_uses_command_processor(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(codex_cli.os, "name", "nt")
    monkeypatch.setattr(codex_cli, "Path", PureWindowsPath)
    monkeypatch.setenv("COMSPEC", r"C:\Windows\System32\cmd.exe")

    wrapped = codex_cli._windows_wrapped_command(
        [r"C:\Users\Zero\AppData\Roaming\npm\codex.cmd", "exec", "-"]
    )

    assert wrapped[:4] == [r"C:\Windows\System32\cmd.exe", "/d", "/s", "/c"]
    assert "codex.cmd" in wrapped[4]
    assert "exec" in wrapped[4]


@pytest.mark.asyncio
async def test_live_smoke_writes_report_without_running_real_codex(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_generate(self, **kwargs):
        del self
        assert kwargs["output_type"] is Interpretation
        context = json.loads(kwargs["input_text"])
        assert context["member"]["member_id"] == "steward"
        return ModelResult[Interpretation](
            output=Interpretation.model_validate(_interpretation_payload()),
            provider="codex-cli",
            model="gpt-test",
            response_id="thread-123",
            input_tokens=321,
            output_tokens=87,
            latency_ms=1200,
            retries=0,
        )

    monkeypatch.setattr(CodexCliProvider, "generate", fake_generate)
    root = Path(__file__).resolve().parents[1]
    report = await run_codex_smoke(
        project_root=root,
        output_dir=tmp_path,
        model="gpt-test",
    )

    assert report.output.member_id == "steward"
    assert report.input_tokens == 321
    persisted = json.loads((tmp_path / "smoke-report.json").read_text(encoding="utf-8"))
    assert persisted["response_id"] == "thread-123"
    assert persisted["output"]["member_id"] == "steward"
