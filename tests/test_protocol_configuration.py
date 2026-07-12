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
    ContinuationReason,
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

    assert protocol.version == "1.3"
    assert len(protocol.stage_contracts) == len(DeliberationStage) - 1
    assert protocol.stage_contracts[0].prerequisite_stage is DeliberationStage.CREATED
    assert protocol.stage_contracts[-1].resulting_stage is DeliberationStage.PLAN_COMPLETE


def test_same_phase_continuation_excludes_unresolved_evidence() -> None:
    _, _, protocol = _load_dependencies()

    assert set(protocol.stopping_policy.continuation_reasons) == set(ContinuationReason)
    assert {reason.value for reason in protocol.stopping_policy.continuation_reasons} == {
        "new_material_frame",
        "unresolved_material_claim",
        "adjudication_may_change",
    }


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


def test_challenge_stages_route_conditional_advocate_subturns() -> None:
    _, _, protocol = _load_dependencies()

    for resulting_stage in (
        DeliberationStage.FRAME_CHALLENGES_COMPLETE,
        DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE,
    ):
        contract = protocol.contract_for(resulting_stage)
        assert contract.actor is ProtocolActor.SENESCHAL
        assert tuple(turn.speaker_from_assignment for turn in contract.challenge_turns) == (
            "challenger",
            "target",
        )
        assert tuple(turn.required_output_artifact for turn in contract.challenge_turns) == (
            ArtifactKind.CHALLENGE,
            ArtifactKind.CHALLENGE_RESPONSE,
        )
        assert ArtifactKind.CHALLENGE not in contract.required_output_artifacts
        assert ArtifactKind.CHALLENGE_RESPONSE not in contract.required_output_artifacts
        assert ArtifactKind.CHALLENGE_PLAN in contract.required_output_artifacts
        assert ArtifactKind.CONTINUATION_DECISION in contract.required_output_artifacts
        assert ArtifactKind.CHALLENGE in contract.challenge_turns[1].allowed_input_artifacts


def test_evidence_stages_resolve_each_request_exactly_once() -> None:
    _, _, protocol = _load_dependencies()

    for resulting_stage in (
        DeliberationStage.EVIDENCE_RESOLVED,
        DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED,
    ):
        contract = protocol.contract_for(resulting_stage)
        assert contract.actor is ProtocolActor.ENGINE
        assert contract.required_output_artifacts == ()
        assert len(contract.output_cardinality) == 1
        rule = contract.output_cardinality[0]
        assert rule.output_artifact is ArtifactKind.EVIDENCE_RESOLUTION
        assert rule.count_from_input_artifact is ArtifactKind.EVIDENCE_REQUEST


def test_protocol_has_explicit_post_proposal_evidence_resolution() -> None:
    _, _, protocol = _load_dependencies()
    contract = protocol.contract_for(DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED)

    assert contract.actor is ProtocolActor.ENGINE
    assert contract.prerequisite_stage is DeliberationStage.PROPOSAL_CHALLENGES_COMPLETE


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


def test_protocol_rejects_challenge_stage_without_advocate_subturns() -> None:
    _, _, protocol = _load_dependencies()
    raw = protocol.model_dump(mode="json")
    challenge_contract = next(
        contract
        for contract in raw["stage_contracts"]
        if contract["resulting_stage"] == "proposal_challenges_complete"
    )
    challenge_contract["challenge_turns"] = []

    with pytest.raises(ValidationError, match="must define advocate subturns"):
        ProtocolConfiguration.model_validate(raw)


def test_protocol_rejects_unconditional_challenge_artifacts() -> None:
    _, _, protocol = _load_dependencies()
    raw = protocol.model_dump(mode="json")
    challenge_contract = next(
        contract
        for contract in raw["stage_contracts"]
        if contract["resulting_stage"] == "proposal_challenges_complete"
    )
    challenge_contract["required_output_artifacts"].append("challenge")

    with pytest.raises(ValidationError, match="conditional on assignments"):
        ProtocolConfiguration.model_validate(raw)


def test_protocol_rejects_evidence_stage_without_cardinality_rule() -> None:
    _, _, protocol = _load_dependencies()
    raw = protocol.model_dump(mode="json")
    evidence_contract = next(
        contract
        for contract in raw["stage_contracts"]
        if contract["resulting_stage"] == "proposal_evidence_resolved"
    )
    evidence_contract["output_cardinality"] = []

    with pytest.raises(ValidationError, match="resolve each evidence request exactly once"):
        ProtocolConfiguration.model_validate(raw)
