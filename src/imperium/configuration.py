"""Load and validate versioned Imperium configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from imperium.domain.council import CouncilConfiguration
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
