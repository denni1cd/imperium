"""Regression tests for OpenAI Structured Outputs schema adaptation."""

from __future__ import annotations

import pytest

from imperium.domain.models import Interpretation
from imperium.providers.openai_schema import (
    StructuredSchemaError,
    adapt_pydantic_schema,
    restore_pydantic_payload,
)


def test_interpretation_schema_converts_dynamic_map_to_entry_array() -> None:
    original = Interpretation.model_json_schema()
    adapted = adapt_pydantic_schema(original)

    assert set(adapted["required"]) == set(adapted["properties"])
    influence = adapted["properties"]["value_influence"]
    assert influence["type"] == "array"
    assert influence["items"] == {
        "type": "object",
        "properties": {
            "key": {"type": "string"},
            "value": {"type": "string"},
        },
        "required": ["key", "value"],
        "additionalProperties": False,
    }

    restored = restore_pydantic_payload(
        {
            "value_influence": [
                {"key": "economy", "value": "Bound the first live expense."},
                {"key": "resilience", "value": "Stop on provider failure."},
            ]
        },
        original,
    )
    assert restored["value_influence"] == {
        "economy": "Bound the first live expense.",
        "resilience": "Stop on provider failure.",
    }


def test_structured_map_rejects_duplicate_keys() -> None:
    original = Interpretation.model_json_schema()

    with pytest.raises(StructuredSchemaError, match="duplicate structured map key"):
        restore_pydantic_payload(
            {
                "value_influence": [
                    {"key": "economy", "value": "first"},
                    {"key": "economy", "value": "second"},
                ]
            },
            original,
        )
