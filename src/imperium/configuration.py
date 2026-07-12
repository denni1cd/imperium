"""Load and validate versioned Imperium configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from imperium.domain.council import CouncilConfiguration
from imperium.domain.protocol import ProtocolConfiguration
from imperium.domain.vocabulary import ValueVocabulary


def _load_yaml_mapping(path: str | Path, *, label: str) -> tuple[Path, dict[str, Any]]:
    source = Path(path)
    try:
        raw: Any = yaml.safe_load(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read {label} from {source}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in {label} {source}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"{label} {source} must contain a YAML mapping")
    return source, raw


def load_value_vocabulary(path: str | Path) -> ValueVocabulary:
    """Load an approved strategic value vocabulary from YAML."""

    _, raw = _load_yaml_mapping(path, label="value vocabulary")
    return ValueVocabulary.model_validate(raw)


def load_council_configuration(
    path: str | Path,
    *,
    vocabulary: ValueVocabulary,
) -> CouncilConfiguration:
    """Load the fixed initial council and validate every profile against the vocabulary."""

    _, raw = _load_yaml_mapping(path, label="council configuration")
    council = CouncilConfiguration.model_validate(raw)
    return council.validate_against_vocabulary(vocabulary)


def load_protocol_configuration(
    path: str | Path,
    *,
    vocabulary: ValueVocabulary,
    council: CouncilConfiguration,
) -> ProtocolConfiguration:
    """Load Stage 3 and validate versions plus every referenced prompt contract."""

    source, raw = _load_yaml_mapping(path, label="protocol configuration")
    protocol = ProtocolConfiguration.model_validate(raw)

    if protocol.vocabulary_version != vocabulary.version:
        raise ValueError(
            "protocol vocabulary version does not match loaded vocabulary; "
            f"protocol={protocol.vocabulary_version!r}, vocabulary={vocabulary.version!r}"
        )
    if protocol.council_version != council.version:
        raise ValueError(
            "protocol council version does not match loaded council; "
            f"protocol={protocol.council_version!r}, council={council.version!r}"
        )

    project_root = source.parent.parent
    prompt_paths = {
        contract.prompt_template
        for contract in protocol.stage_contracts
        if contract.prompt_template
    }
    prompt_paths.update(
        turn.prompt_template
        for contract in protocol.stage_contracts
        for turn in contract.challenge_turns
    )
    missing_prompts = sorted(
        prompt_path
        for prompt_path in prompt_paths
        if not (project_root / prompt_path).is_file()
    )
    if missing_prompts:
        raise ValueError(f"protocol references missing prompt templates: {missing_prompts}")

    return protocol
