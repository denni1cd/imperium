"""Inspectable Stage 5 live-provider smoke artifacts."""

from __future__ import annotations

from imperium.domain.models import Interpretation, NonEmptyStr, StrictModel


class CodexSmokeReport(StrictModel):
    """Credential-safe result of one isolated live Interpretation call."""

    session_id: NonEmptyStr
    call_key: NonEmptyStr
    member_id: NonEmptyStr
    provider: NonEmptyStr
    model: NonEmptyStr
    response_id: str | None = None
    input_tokens: int
    output_tokens: int
    latency_ms: int
    retries: int
    output: Interpretation
