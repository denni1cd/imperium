"""Non-interactive Codex CLI provider for bounded local live tests."""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import tempfile
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from imperium.providers.base import CallMetadata, ModelResult, ProviderError
from imperium.providers.openai_schema import (
    StructuredSchemaError,
    adapt_pydantic_schema,
    restore_pydantic_payload,
)

OutputT = TypeVar("OutputT", bound=BaseModel)


@dataclass(frozen=True)
class _ProcessResult:
    returncode: int
    stdout: str
    stderr: str


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "-_." else "_" for character in value)


def _walk_mappings(value: Any) -> Iterable[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        yield value
        for nested in value.values():
            yield from _walk_mappings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_mappings(nested)


def _first_int(mapping: Mapping[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        candidate = mapping.get(key)
        if isinstance(candidate, int) and candidate >= 0:
            return candidate
    return None


def _extract_usage(events: tuple[Mapping[str, Any], ...]) -> tuple[int, int]:
    input_keys = ("input_tokens", "inputTokens", "prompt_tokens", "promptTokens")
    output_keys = ("output_tokens", "outputTokens", "completion_tokens", "completionTokens")
    for event in reversed(events):
        for mapping in _walk_mappings(event):
            input_tokens = _first_int(mapping, input_keys)
            output_tokens = _first_int(mapping, output_keys)
            if input_tokens is not None and output_tokens is not None:
                return input_tokens, output_tokens
    return 0, 0


def _extract_string(events: tuple[Mapping[str, Any], ...], keys: tuple[str, ...]) -> str | None:
    for event in reversed(events):
        for mapping in _walk_mappings(event):
            for key in keys:
                candidate = mapping.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()
    return None


def _parse_jsonl(stdout: str) -> tuple[Mapping[str, Any], ...]:
    events: list[Mapping[str, Any]] = []
    for line in stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            candidate = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if isinstance(candidate, Mapping):
            events.append(candidate)
    return tuple(events)


def _windows_wrapped_command(command: list[str]) -> list[str]:
    executable = Path(command[0])
    if os.name != "nt" or executable.suffix.casefold() not in {".cmd", ".bat"}:
        return command
    command_processor = os.environ.get("COMSPEC", "cmd.exe")
    return [command_processor, "/d", "/s", "/c", subprocess.list2cmdline(command)]


class CodexCliProvider:
    """Invoke one fresh schema-constrained Codex process per model call.

    This provider intentionally uses an empty temporary workspace, read-only
    sandboxing, ephemeral sessions, no project rules, and no automatic retries.
    Authentication remains owned by the user's existing Codex installation.
    """

    def __init__(
        self,
        *,
        executable: str = "codex",
        timeout_seconds: float = 300.0,
        event_log_dir: str | Path | None = None,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("Codex timeout must be positive")
        self.executable = executable
        self.timeout_seconds = timeout_seconds
        self.event_log_dir = Path(event_log_dir).resolve() if event_log_dir else None

    def _resolve_executable(self) -> str:
        resolved = shutil.which(self.executable)
        if resolved is None:
            raise ProviderError(
                f"Codex executable {self.executable!r} was not found on PATH; "
                "install Codex CLI and sign in before running the live smoke test"
            )
        return resolved

    def _build_command(
        self,
        *,
        executable: str,
        workspace: Path,
        schema_path: Path,
        output_path: Path,
        model: str,
    ) -> list[str]:
        command = [
            executable,
            "--ask-for-approval",
            "never",
            "exec",
            "--ephemeral",
            "--ignore-rules",
            "--ignore-user-config",
            "--json",
            "--color",
            "never",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--cd",
            str(workspace),
            "--output-schema",
            str(schema_path),
            "--output-last-message",
            str(output_path),
        ]
        if model.strip():
            command.extend(("--model", model.strip()))
        command.append("-")
        return _windows_wrapped_command(command)

    async def _run_process(self, command: list[str], *, input_text: str) -> _ProcessResult:
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(input=input_text.encode("utf-8")),
                timeout=self.timeout_seconds,
            )
        except TimeoutError as exc:
            process.kill()
            await process.communicate()
            raise ProviderError(
                f"Codex CLI timed out after {self.timeout_seconds:g} seconds; "
                "the call was not retried"
            ) from exc
        return _ProcessResult(
            returncode=process.returncode or 0,
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
        )

    def _write_event_log(
        self,
        *,
        metadata: CallMetadata,
        stdout: str,
        stderr: str,
    ) -> None:
        if self.event_log_dir is None:
            return
        self.event_log_dir.mkdir(parents=True, exist_ok=True)
        stem = _safe_name(metadata.call_key)
        (self.event_log_dir / f"{stem}.jsonl").write_text(stdout, encoding="utf-8")
        if stderr.strip():
            (self.event_log_dir / f"{stem}.stderr.txt").write_text(stderr, encoding="utf-8")

    async def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        output_type: type[OutputT],
        metadata: CallMetadata,
    ) -> ModelResult[OutputT]:
        """Run one isolated Codex call and validate its final structured artifact."""

        executable = self._resolve_executable()
        started = perf_counter()
        original_schema = output_type.model_json_schema()
        wire_schema = adapt_pydantic_schema(original_schema)
        with tempfile.TemporaryDirectory(prefix="imperium-codex-") as temporary:
            workspace = Path(temporary).resolve()
            schema_path = workspace / "output-schema.json"
            output_path = workspace / "final-output.json"
            schema_path.write_text(
                json.dumps(wire_schema, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            command = self._build_command(
                executable=executable,
                workspace=workspace,
                schema_path=schema_path,
                output_path=output_path,
                model=model,
            )
            prompt = (
                f"{instructions.strip()}\n\n"
                "Return only the requested structured artifact. Do not inspect files, "
                "run commands, or infer context not present below. Fields described as "
                "mapping entry arrays must contain unique key/value objects.\n\n"
                f"Imperium stage context:\n{input_text}"
            )
            process_result = await self._run_process(command, input_text=prompt)
            self._write_event_log(
                metadata=metadata,
                stdout=process_result.stdout,
                stderr=process_result.stderr,
            )
            if process_result.returncode != 0:
                diagnostic = process_result.stderr.strip() or process_result.stdout.strip()
                raise ProviderError(
                    f"Codex CLI exited with code {process_result.returncode}: "
                    f"{diagnostic[-2000:]}"
                )
            if not output_path.exists():
                raise ProviderError("Codex CLI completed without writing the final structured output")
            raw_output = output_path.read_text(encoding="utf-8")
            try:
                wire_payload = json.loads(raw_output)
                restored_payload = restore_pydantic_payload(wire_payload, original_schema)
                output = output_type.model_validate(restored_payload)
            except (json.JSONDecodeError, StructuredSchemaError, ValidationError) as exc:
                raise ProviderError(
                    f"Codex CLI output does not match {output_type.__name__}"
                ) from exc

        events = _parse_jsonl(process_result.stdout)
        input_tokens, output_tokens = _extract_usage(events)
        response_id = _extract_string(
            events,
            ("response_id", "responseId", "thread_id", "threadId", "turn_id", "turnId"),
        )
        actual_model = _extract_string(events, ("model", "model_name", "modelName"))
        latency_ms = max(0, round((perf_counter() - started) * 1000))
        return ModelResult[OutputT](
            output=output,
            provider="codex-cli",
            model=actual_model or model.strip() or "codex-config-default",
            response_id=response_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
            retries=0,
        )
