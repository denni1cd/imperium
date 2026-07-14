"""Ensure every Stage 5 model output has a safe Structured Outputs schema."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pytest
from pydantic import BaseModel

from imperium.domain.models import (
    ActionablePlan,
    Adjudication,
    ChallengeResponse,
    FrameRegister,
    Interpretation,
    Revision,
    StrategyProposal,
)
from imperium.domain.protocol import (
    ChallengeArtifact,
    ChallengePlan,
    ClaimRegister,
    ContinuationDecision,
)
from imperium.providers.openai_schema import adapt_pydantic_schema


LIVE_OUTPUT_TYPES: tuple[type[BaseModel], ...] = (
    Interpretation,
    FrameRegister,
    ClaimRegister,
    ChallengePlan,
    ChallengeArtifact,
    ChallengeResponse,
    StrategyProposal,
    Revision,
    ContinuationDecision,
    Adjudication,
    ActionablePlan,
)

_FORBIDDEN_WIRE_KEYWORDS = {
    "title",
    "default",
    "minLength",
    "maxLength",
    "pattern",
    "propertyNames",
    "prefixItems",
    "allOf",
    "oneOf",
    "not",
    "if",
    "then",
    "else",
    "dependentRequired",
    "dependentSchemas",
    "unevaluatedProperties",
}


def _validate_node(node: Any, *, path: str = "$") -> None:
    if isinstance(node, list):
        for index, item in enumerate(node):
            _validate_node(item, path=f"{path}[{index}]")
        return
    if not isinstance(node, Mapping):
        return

    forbidden = _FORBIDDEN_WIRE_KEYWORDS.intersection(node)
    assert not forbidden, f"{path} contains unsupported keywords: {sorted(forbidden)}"

    if node.get("type") == "object":
        properties = node.get("properties")
        assert isinstance(properties, Mapping), f"{path} object lacks properties"
        assert node.get("additionalProperties") is False, (
            f"{path} object must reject additional properties"
        )
        assert node.get("required") == list(properties), (
            f"{path} must require every declared property in declaration order"
        )

    for key, value in node.items():
        _validate_node(value, path=f"{path}.{key}")


@pytest.mark.parametrize("output_type", LIVE_OUTPUT_TYPES, ids=lambda model: model.__name__)
def test_every_live_output_schema_adapts_to_closed_openai_subset(
    output_type: type[BaseModel],
) -> None:
    adapted = adapt_pydantic_schema(output_type.model_json_schema())

    assert adapted.get("type") == "object"
    _validate_node(adapted)
