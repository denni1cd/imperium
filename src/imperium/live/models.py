"""Inspectable Stage 5 live-provider smoke artifacts."""

from __future__ import annotations

from typing import Annotated

from pydantic import Field

from imperium.domain.models import Interpretation, NonEmptyStr, StrictModel


class CodexSmokeReport(StrictModel):
    """Credential-safe result of one isolated live Interpretation call."""

    session_id: NonEmptyStr
    call_key: NonEmptyStr
    member_id: NonEmptyStr
    provider: NonEmptyStr
    model: NonEmptyStr
    reasoning_effort: NonEmptyStr
    response_id: str | None = None
    input_tokens: Annotated[int, Field(ge=0)]
    output_tokens: Annotated[int, Field(ge=0)]
    latency_ms: Annotated[int, Field(ge=0)]
    retries: Annotated[int, Field(ge=0)]
    output: Interpretation
