"""Provider-neutral structured generation contract."""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel, Field, model_validator

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import NonEmptyStr, StrictModel

OutputT = TypeVar("OutputT", bound=BaseModel)


class ProviderError(RuntimeError):
    """Raised when a model provider cannot return a valid requested artifact."""


class ProviderAmbiguousError(ProviderError):
    """Raised when a provider may have consumed resources but its outcome is unknown."""


class CallMetadata(StrictModel):
    """Stable identifiers and lifecycle context for a provider invocation."""

    session_id: NonEmptyStr
    call_key: NonEmptyStr
    stage: DeliberationStage
    member_id: str | None = None


class ModelResult(StrictModel, Generic[OutputT]):
    """Validated output plus provider-neutral usage metadata."""

    output: OutputT
    provider: NonEmptyStr
    model: NonEmptyStr
    response_id: str | None = None
    input_tokens: int = Field(default=0, ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    retries: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def cached_tokens_are_part_of_input(self):
        if self.cached_input_tokens > self.input_tokens:
            raise ValueError("cached input tokens cannot exceed total input tokens")
        return self


class ModelProvider(Protocol):
    """Minimal interface required by the Imperium engine."""

    async def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        output_type: type[OutputT],
        metadata: CallMetadata,
    ) -> ModelResult[OutputT]:
        """Generate and validate one structured deliberation artifact."""
        ...
