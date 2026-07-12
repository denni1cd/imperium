"""Focused regressions for protocol 1.2 output-cardinality enforcement."""

from pathlib import Path

import pytest

from imperium.configuration import (
    load_council_configuration,
    load_protocol_configuration,
    load_value_vocabulary,
)
from imperium.domain.enums import ArtifactKind, DeliberationStage, EvidenceOutcome
from imperium.domain.models import EvidenceRequest, EvidenceResolution
from imperium.engine.protocol_rules import (
    InvalidProtocolArtifact,
    validate_evidence_resolutions,
    validate_stage_outputs,
)


ROOT = Path(__file__).resolve().parents[1]


def _evidence_contract():
    vocabulary = load_value_vocabulary(ROOT / "config" / "values.yaml")
    council = load_council_configuration(
        ROOT / "config" / "council.yaml",
        vocabulary=vocabulary,
    )
    protocol = load_protocol_configuration(
        ROOT / "config" / "protocol.yaml",
        vocabulary=vocabulary,
        council=council,
    )
    return protocol.contract_for(DeliberationStage.PROPOSAL_EVIDENCE_RESOLVED)


def _request(request_id: str) -> EvidenceRequest:
    return EvidenceRequest(
        evidence_request_id=request_id,
        requester_member_id="steward",
        disputed_claim=f"Claim controlled by {request_id}.",
        decision_impact="The preferred strategy changes if the claim fails.",
        requested_information="Decision-critical fixture evidence.",
        preferred_source="synthetic replay fixture",
    )


def _resolution(request_id: str) -> EvidenceResolution:
    return EvidenceResolution(
        evidence_request_id=request_id,
        outcome=EvidenceOutcome.GATHERED,
        evidence=(f"Synthetic evidence for {request_id}.",),
        source_references=(f"fixture:{request_id}",),
    )


def test_cardinality_stage_requires_explicit_input_artifact_counts() -> None:
    contract = _evidence_contract()

    with pytest.raises(InvalidProtocolArtifact, match="requires supplied input artifacts"):
        validate_stage_outputs(contract, ())


def test_two_evidence_requests_require_two_resolution_outputs() -> None:
    contract = _evidence_contract()
    inputs = (ArtifactKind.EVIDENCE_REQUEST, ArtifactKind.EVIDENCE_REQUEST)
    outputs = (ArtifactKind.EVIDENCE_RESOLUTION, ArtifactKind.EVIDENCE_RESOLUTION)

    validate_stage_outputs(
        contract,
        outputs,
        supplied_input_artifacts=inputs,
    )

    with pytest.raises(InvalidProtocolArtifact, match="expected 2"):
        validate_stage_outputs(
            contract,
            (ArtifactKind.EVIDENCE_RESOLUTION,),
            supplied_input_artifacts=inputs,
        )


def test_two_evidence_requests_map_to_two_distinct_resolutions() -> None:
    requests = (_request("evidence-a"), _request("evidence-b"))
    resolutions = (_resolution("evidence-a"), _resolution("evidence-b"))

    validate_evidence_resolutions(requests, resolutions)

    with pytest.raises(InvalidProtocolArtifact, match="missing=.*evidence-b"):
        validate_evidence_resolutions(requests, resolutions[:1])
