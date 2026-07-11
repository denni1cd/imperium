"""Deterministic provider for lifecycle and contract tests without model usage."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from typing import TypeVar

from pydantic import BaseModel

from imperium.providers.base import CallMetadata, ModelResult, ProviderError

OutputT = TypeVar("OutputT", bound=BaseModel)


class FakeProvider:
    """Returns queued Pydantic artifacts in invocation order."""

    def __init__(self, responses: Iterable[BaseModel] = ()) -> None:
        self._responses: deque[BaseModel] = deque(responses)
        self.calls: list[CallMetadata] = []

    def queue(self, *responses: BaseModel) -> None:
        self._responses.extend(responses)

    @property
    def remaining(self) -> int:
        return len(self._responses)

    async def generate(
        self,
        *,
        model: str,
        instructions: str,
        input_text: str,
        output_type: type[OutputT],
        metadata: CallMetadata,
    ) -> ModelResult[OutputT]:
        del instructions, input_text
        self.calls.append(metadata)
        if not self._responses:
            raise ProviderError(f"no fake response queued for call {metadata.call_key}")

        response = self._responses.popleft()
        if not isinstance(response, output_type):
            raise ProviderError(
                f"queued response for {metadata.call_key} is {type(response).__name__}; "
                f"expected {output_type.__name__}"
            )

        return ModelResult[OutputT](
            output=response,
            provider="fake",
            model=model,
        )
