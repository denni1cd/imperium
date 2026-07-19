"""Credential-safe capture and zero-live-call replay for accepted council outputs."""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Annotated, Any, Self

from pydantic import Field, model_validator

from imperium.domain.enums import DeliberationStage, SessionStatus
from imperium.domain.models import NonEmptyStr, StrictModel
from imperium.offline.attempts import AttemptStatus, UsageBudget, artifact_digest
from imperium.offline.models import OfflineSession
from imperium.offline.persistence import _atomic_write_text
from imperium.offline.replay_script import ReplayRecords


class CapturedCall(StrictModel):
    """One accepted model result sufficient for provider-free replay."""

    call_key: NonEmptyStr
    output_artifact_id: NonEmptyStr
    output_sha256: NonEmptyStr
    payload_sha256: NonEmptyStr
    provider: NonEmptyStr
    model: NonEmptyStr
    response_id: str | None = None
    input_tokens: Annotated[int, Field(ge=0)] = 0
    cached_input_tokens: Annotated[int, Field(ge=0)] = 0
    output_tokens: Annotated[int, Field(ge=0)] = 0
    latency_ms: Annotated[int, Field(ge=0)] = 0
    output: dict[str, Any]

    @model_validator(mode="after")
    def validate_cached_usage(self) -> Self:
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("captured cached input tokens cannot exceed input tokens")
        payload_digest = sha256(
            json.dumps(
                self.output,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest()
        if self.payload_sha256 != payload_digest:
            raise ValueError("captured output payload does not match its digest")
        return self


class CouncilReplayCapture(StrictModel):
    """Versioned accepted-output capture from one complete live council session."""

    schema_version: str = "1.0"
    session_id: NonEmptyStr
    scenario_sha256: NonEmptyStr
    usage_budget: UsageBudget
    calls: tuple[CapturedCall, ...]

    @model_validator(mode="after")
    def validate_capture(self) -> Self:
        if self.schema_version != "1.0":
            raise ValueError(f"unsupported council replay schema {self.schema_version!r}")
        keys = [call.call_key for call in self.calls]
        if not keys:
            raise ValueError("a council replay capture requires accepted calls")
        if len(keys) != len(set(keys)):
            raise ValueError("captured call keys must be unique")
        return self

    def replay_records(self) -> ReplayRecords:
        """Convert the capture into ReplayProvider input without a Codex provider."""

        return {
            call.call_key: [
                {
                    "output": call.output,
                    "provider": call.provider,
                    "model": call.model,
                    "response_id": call.response_id,
                    "input_tokens": call.input_tokens,
                    "cached_input_tokens": call.cached_input_tokens,
                    "output_tokens": call.output_tokens,
                    "latency_ms": call.latency_ms,
                    "retries": 0,
                }
            ]
            for call in self.calls
        }


def capture_completed_session(session: OfflineSession) -> CouncilReplayCapture:
    """Extract only accepted outputs and provider metadata from a complete session."""

    if session.status is not SessionStatus.COMPLETE or (
        session.record.stage is not DeliberationStage.PLAN_COMPLETE
    ):
        raise ValueError("only a complete plan session can be captured for replay")

    accepted = {
        attempt.call_key: attempt
        for attempt in session.attempts
        if attempt.status is AttemptStatus.ACCEPTED
    }
    if set(accepted) != set(session.completed_call_keys):
        raise ValueError("capture requires one accepted attempt for every completed call")
    artifacts = session.accepted_artifact_index()
    calls: list[CapturedCall] = []
    for call_key in session.completed_call_keys:
        attempt = accepted[call_key]
        artifact_id = attempt.output_artifact_id
        if artifact_id is None or artifact_id not in artifacts:
            raise ValueError(f"accepted call {call_key!r} has no canonical output artifact")
        artifact = artifacts[artifact_id]
        digest = artifact_digest(artifact)
        if attempt.output_sha256 != digest:
            raise ValueError(f"accepted call {call_key!r} output digest is inconsistent")
        if attempt.provider is None:
            raise ValueError(f"accepted call {call_key!r} has no provider identity")
        calls.append(
            # A second canonical digest protects the provider-neutral JSON capture
            # itself; output_sha256 remains the engine's typed-artifact digest.
            CapturedCall(
                call_key=call_key,
                output_artifact_id=artifact_id,
                output_sha256=digest,
                payload_sha256=sha256(
                    json.dumps(
                        artifact.model_dump(mode="json"),
                        ensure_ascii=False,
                        separators=(",", ":"),
                        sort_keys=True,
                    ).encode("utf-8")
                ).hexdigest(),
                provider=attempt.provider,
                model=attempt.model,
                response_id=attempt.response_id,
                input_tokens=attempt.input_tokens,
                cached_input_tokens=attempt.cached_input_tokens,
                output_tokens=attempt.output_tokens,
                latency_ms=attempt.latency_ms,
                output=artifact.model_dump(mode="json"),
            )
        )
    return CouncilReplayCapture(
        session_id=session.session_id,
        scenario_sha256=session.scenario_sha256 or "",
        usage_budget=session.usage_budget,
        calls=tuple(calls),
    )


def write_capture(capture: CouncilReplayCapture, path: str | Path) -> Path:
    """Atomically persist a replay capture."""

    return _atomic_write_text(Path(path), capture.model_dump_json(indent=2))


def load_capture(path: str | Path) -> CouncilReplayCapture:
    """Load and strictly validate a replay capture."""

    return CouncilReplayCapture.model_validate_json(Path(path).read_text(encoding="utf-8"))


def _stable_session_payload(session: OfflineSession) -> dict[str, Any]:
    record = json.loads(session.record.model_dump_json())
    for call in record["model_calls"]:
        call.pop("created_at", None)
    return {
        "session_id": session.session_id,
        "scenario": json.loads(session.scenario.model_dump_json()),
        "scenario_sha256": session.scenario_sha256,
        "artifact_authority": session.artifact_authority,
        "runtime": json.loads(session.runtime.model_dump_json()),
        "record": record,
        "protocol_trace": json.loads(session.protocol_trace.model_dump_json()),
        "lifecycle_history": [stage.value for stage in session.lifecycle_history],
        "turns": [json.loads(turn.model_dump_json()) for turn in session.turns],
        "completed_call_keys": list(session.completed_call_keys),
        "usage_budget": json.loads(session.usage_budget.model_dump_json()),
        "evidence_history": [
            json.loads(event.model_dump_json()) for event in session.evidence_history
        ],
        "lineage": [json.loads(link.model_dump_json()) for link in session.lineage],
    }


def verify_replay_equivalence(live: OfflineSession, replay: OfflineSession) -> None:
    """Fail unless replay reproduces the complete accepted deliberation state.

    Attempt failures, retries, and checkpoint counters remain audit history rather than
    provider outputs, so they are not expected to be regenerated by ReplayProvider.
    """

    if _stable_session_payload(live) != _stable_session_payload(replay):
        raise ValueError("captured replay diverged from the accepted live deliberation state")
