"""Tests for the approved Stage 2 member profiles and fixed initial council."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from imperium.configuration import load_council_configuration, load_value_vocabulary
from imperium.domain.council import CouncilConfiguration
from imperium.domain.enums import CouncilRole


ROOT = Path(__file__).resolve().parents[1]
VOCABULARY_PATH = ROOT / "config" / "values.yaml"
COUNCIL_PATH = ROOT / "config" / "council.yaml"
EXPECTED_ADVOCATES = ("steward", "vanguard", "architect", "castellan")


def _load_council() -> CouncilConfiguration:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    return load_council_configuration(COUNCIL_PATH, vocabulary=vocabulary)


def test_fixed_council_loads_with_four_advocates_and_one_seneschal() -> None:
    council = _load_council()

    assert council.version == "1.0"
    assert council.vocabulary_version == "1.0"
    assert council.fixed_for_initial_experiments is True
    assert tuple(member.member_id for member in council.advocates) == EXPECTED_ADVOCATES
    assert council.seneschal.member_id == "seneschal"
    assert len(council.members) == 5


def test_seneschal_is_procedural_and_not_an_advocate() -> None:
    council = _load_council()

    assert council.seneschal.role is CouncilRole.SENESCHAL
    assert council.seneschal.participates_in_advocacy is False
    assert council.seneschal.member_id not in council.advocate_member_ids
    assert all(member.participates_in_advocacy for member in council.advocates)


def test_advocates_have_distinct_dominant_values_and_vectors() -> None:
    council = _load_council()

    assert {member.member_id: member.dominant_value for member in council.advocates} == {
        "steward": "economy",
        "vanguard": "ambition",
        "architect": "leverage",
        "castellan": "resilience",
    }
    fingerprints = {
        tuple(sorted((key, str(value)) for key, value in member.values.weights.items()))
        for member in council.members
    }
    assert len(fingerprints) == len(council.members)


def test_every_member_has_an_inspectable_differentiation_claim() -> None:
    council = _load_council()

    assert {entry.member_id for entry in council.differentiation} == {
        member.member_id for member in council.members
    }
    by_id = {entry.member_id: entry for entry in council.differentiation}
    for advocate_id in council.advocate_member_ids:
        assert by_id[advocate_id].counterweight_member_ids


def test_council_names_are_metadata_not_member_identifiers() -> None:
    council = _load_council()

    assert {member.member_id for member in council.members} == {
        "seneschal",
        "steward",
        "vanguard",
        "architect",
        "castellan",
    }
    assert {member.presentation_label for member in council.members} == {
        "Seneschal",
        "Accountant",
        "Gazgul",
        "Overmind",
        "Castellan",
    }


def test_known_human_sustainability_coverage_risk_is_preserved() -> None:
    council = _load_council()

    assert any("Human Sustainability" in risk for risk in council.known_coverage_risks)
    assert all(member.dominant_value != "human_sustainability" for member in council.advocates)


def test_council_rejects_identical_member_vectors() -> None:
    council = _load_council()
    raw = council.model_dump(mode="json")
    members = raw["members"]
    steward = next(member for member in members if member["member_id"] == "steward")
    vanguard = next(member for member in members if member["member_id"] == "vanguard")
    vanguard["values"] = steward["values"]

    with pytest.raises(ValidationError, match="must not use identical value vectors"):
        CouncilConfiguration.model_validate(raw)


def test_seneschal_cannot_be_enabled_as_an_advocate() -> None:
    council = _load_council()
    raw = council.model_dump(mode="json")
    seneschal = next(member for member in raw["members"] if member["member_id"] == "seneschal")
    seneschal["participates_in_advocacy"] = True

    with pytest.raises(ValidationError, match="must not participate as an independent advocate"):
        CouncilConfiguration.model_validate(raw)


def test_council_rejects_mismatched_vocabulary_version() -> None:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    council = _load_council().model_copy(update={"vocabulary_version": "2.0"})

    with pytest.raises(ValueError, match="does not match loaded vocabulary"):
        council.validate_against_vocabulary(vocabulary)
