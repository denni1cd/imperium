"""Provider-neutral structured generation contract."""

from __future__ import annotations

from typing import Generic, Protocol, TypeVar

from pydantic import BaseModel, Field

from imperium.domain.enums import DeliberationStage
from imperium.domain.models import NonEmptyStr, StrictModel

OutputT = TypeVar("OutputT", bound=BaseModel)


class ProviderError(RuntimeError):
    """Raised when a model provider cannot return a valid requested artifact."""


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
    output_tokens: int = Field(default=0, ge=0)
    latency_ms: int = Field(default=0, ge=0)
    retries: int = Field(default=0, ge=0)


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
