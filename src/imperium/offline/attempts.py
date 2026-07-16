"""Inspectable model-attempt and usage-budget contracts for Stage 5 Gate 2E."""

from __future__ import annotations

from enum import StrEnum
from hashlib import sha256
from typing import Iterable, Self

from pydantic import BaseModel, Field, model_validator

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import NonEmptyStr, StrictModel


class AttemptStatus(StrEnum):
    """Durable state of one provider invocation attempt."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    FAILED = "failed"
    AMBIGUOUS = "ambiguous"
    ABANDONED = "abandoned"
    RETRIED = "retried"


class UsageBudget(StrictModel):
    """Persisted hard limits applied before and after provider invocation."""

    max_attempts: int = Field(default=64, ge=1)
    max_input_tokens: int = Field(default=2_000_000, ge=1)
    max_cached_input_tokens: int = Field(default=2_000_000, ge=0)
    max_output_tokens: int = Field(default=250_000, ge=1)
    input_estimate_bytes_per_token: int = Field(default=3, ge=1)
    output_token_reserve_per_attempt: int = Field(default=4_096, ge=1)


class UsageTotals(StrictModel):
    """Cumulative reported usage across every launched attempt."""

    attempts_launched: int = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)


class ModelAttempt(StrictModel):
    """Durable before-and-after record for one provider invocation."""

    attempt_id: NonEmptyStr
    call_key: NonEmptyStr
    attempt_number: int = Field(ge=1)
    status: AttemptStatus
    stage: DeliberationStage
    member_id: str | None = None
    model: NonEmptyStr
    provider: str | None = None
    response_id: str | None = None
    prompt_sha256: NonEmptyStr
    input_sha256: NonEmptyStr
    estimated_input_tokens: int = Field(default=0, ge=0)
    output_sha256: str | None = None
    output_artifact_id: str | None = None
    input_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    retry_of_attempt_id: str | None = None
    superseded_by_attempt_id: str | None = None
    error_type: str | None = None
    error_message: str | None = None
    disposition_reason: str | None = None

    @model_validator(mode="after")
    def validate_state(self) -> Self:
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("cached input tokens cannot exceed total input tokens")
        if self.status is AttemptStatus.PENDING:
            if any(
                value is not None
                for value in (
                    self.provider,
                    self.response_id,
                    self.output_sha256,
                    self.output_artifact_id,
                    self.error_type,
                    self.error_message,
                )
            ):
                raise ValueError("pending attempts cannot contain terminal provider or error data")
            if any((self.input_tokens, self.cached_input_tokens, self.output_tokens, self.latency_ms)):
                raise ValueError("pending attempts cannot contain reported usage")
        elif self.status is AttemptStatus.ACCEPTED:
            if not self.provider or not self.output_sha256 or not self.output_artifact_id:
                raise ValueError("accepted attempts require provider and output identity metadata")
            if self.error_type is not None or self.error_message is not None:
                raise ValueError("accepted attempts cannot contain error metadata")
        elif self.status in {AttemptStatus.FAILED, AttemptStatus.AMBIGUOUS}:
            if not self.error_type or not self.error_message:
                raise ValueError("failed and ambiguous attempts require error metadata")
        elif self.status is AttemptStatus.RETRIED:
            if not self.superseded_by_attempt_id or not self.disposition_reason:
                raise ValueError("retried attempts require a successor and disposition reason")
        elif self.status is AttemptStatus.ABANDONED and not self.disposition_reason:
            raise ValueError("abandoned attempts require a disposition reason")
        return self


def artifact_digest(artifact: BaseModel) -> str:
    """Return the canonical digest persisted for one structured output artifact."""

    return sha256(artifact.model_dump_json().encode("utf-8")).hexdigest()


def estimate_input_tokens(input_text: str, budget: UsageBudget) -> int:
    """Conservatively estimate input tokens from serialized UTF-8 bytes."""

    byte_count = len(input_text.encode("utf-8"))
    divisor = budget.input_estimate_bytes_per_token
    return max(1, (byte_count + divisor - 1) // divisor)


def usage_totals(attempts: Iterable[ModelAttempt]) -> UsageTotals:
    """Sum every launched attempt, including failed or ambiguous attempts."""

    items = tuple(attempts)
    return UsageTotals(
        attempts_launched=len(items),
        input_tokens=sum(item.input_tokens for item in items),
        cached_input_tokens=sum(item.cached_input_tokens for item in items),
        output_tokens=sum(item.output_tokens for item in items),
    )


class UsageBudgetExceeded(RuntimeError):
    """Raised when a provider call would exceed a persisted usage budget."""


class RetryAuthorizationRequired(RuntimeError):
    """Raised when a second attempt is requested without an explicit disposition."""
