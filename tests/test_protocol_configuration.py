"""Tests for the approved Stage 3 protocol configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from imperium.configuration import (
    load_council_configuration,
    load_protocol_configuration,
    load_value_vocabulary,
)
from imperium.domain.enums import (
    ArtifactKind,
    DeliberationStage,
    ProtocolActor,
)
from imperium.domain.protocol import ProtocolConfiguration


ROOT = Path(__file__).resolve().parents[1]
VOCABULARY_PATH = ROOT / "config" / "values.yaml"
COUNCIL_PATH = ROOT / "config" / "council.yaml"
PROTOCOL_PATH = ROOT / "config" / "protocol.yaml"


def _load_dependencies():
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    council = load_council_configuration(COUNCIL_PATH, vocabulary=vocabulary)
    protocol = load_protocol_configuration(
        PROTOCOL_PATH,
        vocabulary=vocabulary,
        council=council,
    )
    return vocabulary, council, protocol


def test_protocol_loads_and_covers_every_lifecycle_transition() -> None:
    _, _, protocol = _load_dependencies()

    assert protocol.version == "1.0"
    assert len(protocol.stage_contracts) == len(DeliberationStage) - 1
    assert protocol.stage_contracts[0].prerequisite_stage is DeliberationStage.CREATED
    assert protocol.stage_contracts[-1].resulting_stage is DeliberationStage.PLAN_COMPLETE


def test_independent_interpretation_is_blind_and_advocate_owned() -> None:
    _, _, protocol = _load_dependencies()
    contract = protocol.contract_for(DeliberationStage.INTERPRETATIONS_COMPLETE)

    assert contract.actor is ProtocolActor.ADVOCATE
    assert contract.blind is True
    assert contract.per_advocate is True
    assert set(contract.allowed_input_artifacts) == {
        ArtifactKind.SOVEREIGN_REQUEST,
        ArtifactKind.COUNCIL_SNAPSHOT,
    }
    assert contract.required_output_artifacts == (ArtifactKind.INTERPRETATION,)


def test_protocol_has_explicit_post_proposal_evidence_resolution() -> None:
    _, _, protocol = _load_dependencies()
    contract = protocol.contract_for(DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED)

    assert contract.actor is ProtocolActor.ENGINE
    assert contract.prerequisite_stage is DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE
    assert contract.required_output_artifacts == (ArtifactKind.EVIDENCE_RESOLUTION,)


def test_first_experiments_cannot_use_abbreviated_path() -> None:
    _, _, protocol = _load_dependencies()

    assert protocol.abbreviated_path.enabled_for_initial_experiments is False
    assert "actionable-plan contract" in " ".join(
        protocol.abbreviated_path.permitted_skips
    ).lower()


def test_protocol_versions_match_approved_dependencies() -> None:
    vocabulary, council, protocol = _load_dependencies()

    assert protocol.vocabulary_version == vocabulary.version
    assert protocol.council_version == council.version


def test_loader_rejects_missing_prompt_templates(tmp_path: Path) -> None:
    vocabulary = load_value_vocabulary(VOCABULARY_PATH)
    council = load_council_configuration(COUNCIL_PATH, vocabulary=vocabulary)
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    copied = config_dir / "protocol.yaml"
    copied.write_text(PROTOCOL_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(ValueError, match="missing prompt templates"):
        load_protocol_configuration(copied, vocabulary=vocabulary, council=council)


def test_protocol_rejects_out_of_order_stage_contracts() -> None:
    _, _, protocol = _load_dependencies()
    raw = protocol.model_dump(mode="json")
    contracts = raw["stage_contracts"]
    contracts[3], contracts[4] = contracts[4], contracts[3]

    with pytest.raises(ValidationError, match="expected"):
        ProtocolConfiguration.model_validate(raw)
