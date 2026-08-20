"""Replay previously captured model artifacts without new model calls."""

from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Mapping, Sequence
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from imperium.providers.base import CallMetadata, ModelResult, ProviderError

OutputT = TypeVar("OutputT", bound=BaseModel)


class ReplayProvider:
    """Returns recorded payloads keyed by stable call names.

    Each record must contain an ``output`` object. Optional usage fields mirror
    :class:`ModelResult` and default to zero when omitted.
    """

    def __init__(self, records: Mapping[str, Sequence[Mapping[str, Any]]]) -> None:
        self._records: dict[str, deque[Mapping[str, Any]]] = defaultdict(deque)
        for call_key, entries in records.items():
            self._records[call_key].extend(entries)
        self.calls: list[CallMetadata] = []

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
        queue = self._records.get(metadata.call_key)
        if not queue:
            raise ProviderError(f"no replay record available for call {metadata.call_key}")

        record = queue.popleft()
        if "output" not in record:
            raise ProviderError(f"replay record {metadata.call_key} is missing 'output'")

        try:
            output = output_type.model_validate(record["output"])
        except ValidationError as exc:
            raise ProviderError(
                f"replay record {metadata.call_key} does not match {output_type.__name__}"
            ) from exc

        return ModelResult[OutputT](
            output=output,
            provider=str(record.get("provider", "replay")),
            model=str(record.get("model", model)),
            response_id=record.get("response_id"),
            input_tokens=int(record.get("input_tokens", 0)),
            cached_input_tokens=int(record.get("cached_input_tokens", 0)),
            output_tokens=int(record.get("output_tokens", 0)),
            latency_ms=int(record.get("latency_ms", 0)),
            retries=int(record.get("retries", 0)),
        )
