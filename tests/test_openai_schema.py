"""Regression tests for OpenAI Structured Outputs schema adaptation."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from pydantic import ValidationError

from imperium.domain.models import Interpretation
from imperium.providers.openai_schema import (
    StructuredSchemaError,
    adapt_pydantic_schema,
    restore_pydantic_payload,
)


def _contains_keyword(value: Any, keyword: str) -> bool:
    if isinstance(value, Mapping):
        return keyword in value or any(
            _contains_keyword(item, keyword) for item in value.values()
        )
    if isinstance(value, list):
        return any(_contains_keyword(item, keyword) for item in value)
    return False


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


def test_interpretation_schema_removes_decimal_regex_lookaround() -> None:
    original = Interpretation.model_json_schema()
    confidence_schema = original["properties"]["confidence"]
    assert _contains_keyword(confidence_schema, "pattern")

    adapted = adapt_pydantic_schema(original)

    assert not _contains_keyword(adapted, "pattern")


def test_domain_validation_remains_authoritative_after_pattern_removal() -> None:
    with pytest.raises(ValidationError, match="confidence"):
        Interpretation.model_validate(
            {
                "member_id": "steward",
                "core_decision": "Whether the one-call provider boundary works.",
                "desired_outcome": "A validated live interpretation.",
                "initial_inclination": "Run one bounded smoke call.",
                "value_influence": {"economy": "Spend only one live call."},
                "confidence": "not-a-decimal",
            }
        )


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
