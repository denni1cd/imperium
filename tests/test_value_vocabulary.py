"""Tests for the approved Stage 1 strategic value vocabulary."""

from decimal import Decimal
from pathlib import Path

import pytest
from pydantic import ValidationError

from imperium.configuration import load_value_vocabulary
from imperium.domain.models import ValueVector
from imperium.domain.vocabulary import (
    StrategicValueDefinition,
    ValueDistinction,
    ValueVocabulary,
)


VOCABULARY_PATH = Path(__file__).resolve().parents[1] / "config" / "values.yaml"
EXPECTED_VALUE_IDS = (
    "ambition",
    "urgency",
    "economy",
    "simplicity",
    "resilience",
    "optionality",
    "leverage",
    "adaptability",
    "human_sustainability",
)


def _definition(value_id: str, *, tensions: tuple[str, ...] = ()) -> StrategicValueDefinition:
    return StrategicValueDefinition(
        value_id=value_id,
        name=value_id.replace("_", " ").title(),
        definition=f"Prioritize {value_id} in strategic decisions.",
        high_weight_behavior=("Notices this value early.", "Accepts tradeoffs for this value."),
        low_weight_behavior=("Allows competing values to dominate.", "Does not force this value."),
        tensions=tensions,
        prohibited_interpretations=(
            "Does not override user intent.",
            "Does not replace evidence with preference.",
        ),
    )


def test_approved_vocabulary_loads_with_expected_values() -> None:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)

    assert vocabulary.version == "1.0"
    assert vocabulary.status == "approved"
    assert vocabulary.value_ids == EXPECTED_VALUE_IDS
    assert len(vocabulary.distinctions) == 8


def test_approved_vocabulary_covers_every_value_with_a_distinction() -> None:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    covered = {
        value_id
        for distinction in vocabulary.distinctions
        for value_id in (distinction.value_a, distinction.value_b)
    }

    assert covered == set(EXPECTED_VALUE_IDS)


def test_complete_normalized_vector_matches_vocabulary() -> None:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    vector = ValueVector(
        weights={
            "ambition": Decimal("0.12"),
            "urgency": Decimal("0.10"),
            "economy": Decimal("0.12"),
            "simplicity": Decimal("0.10"),
            "resilience": Decimal("0.12"),
            "optionality": Decimal("0.10"),
            "leverage": Decimal("0.12"),
            "adaptability": Decimal("0.10"),
            "human_sustainability": Decimal("0.12"),
        }
    )

    assert vocabulary.validate_vector(vector) is vector


def test_vector_rejects_missing_and_unapproved_values() -> None:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    vector = ValueVector(
        weights={
            "ambition": Decimal("0.2"),
            "urgency": Decimal("0.1"),
            "economy": Decimal("0.1"),
            "simplicity": Decimal("0.1"),
            "resilience": Decimal("0.1"),
            "optionality": Decimal("0.1"),
            "leverage": Decimal("0.1"),
            "adaptability": Decimal("0.1"),
            "innovation": Decimal("0.1"),
        }
    )

    with pytest.raises(ValueError, match="missing values.*human_sustainability"):
        vocabulary.validate_vector(vector)


def test_vocabulary_rejects_non_reciprocal_tensions() -> None:
    with pytest.raises(ValidationError, match="non-reciprocal tensions"):
        ValueVocabulary(
            version="test",
            status="approved",
            values=(
                _definition("ambition", tensions=("economy",)),
                _definition("economy"),
            ),
            distinctions=(
                ValueDistinction(
                    value_a="ambition",
                    value_b="economy",
                    scenario="Choose between growth and efficiency.",
                    difference="The values prioritize different outcomes.",
                ),
            ),
        )


def test_vocabulary_rejects_uncovered_values() -> None:
    with pytest.raises(ValidationError, match="missing.*adaptability"):
        ValueVocabulary(
            version="test",
            status="approved",
            values=(
                _definition("ambition"),
                _definition("economy"),
                _definition("adaptability"),
            ),
            distinctions=(
                ValueDistinction(
                    value_a="ambition",
                    value_b="economy",
                    scenario="Choose between growth and efficiency.",
                    difference="The values prioritize different outcomes.",
                ),
            ),
        )


def test_loader_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    source = tmp_path / "values.yaml"
    source.write_text("- ambition\n- economy\n", encoding="utf-8")

    with pytest.raises(ValueError, match="must contain a YAML mapping"):
        load_value_vocabulary(source)
