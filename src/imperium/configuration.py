"""Load and validate versioned Imperium configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from imperium.domain.vocabulary import ValueVocabulary


def load_value_vocabulary(path: str | Path) -> ValueVocabulary:
    """Load an approved strategic value vocabulary from YAML.

    The YAML document is treated as untrusted configuration. It must contain a mapping
    and pass the complete :class:`ValueVocabulary` contract before it can be used.
    """

    source = Path(path)
    try:
        raw: Any = yaml.safe_load(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"unable to read value vocabulary from {source}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid YAML in value vocabulary {source}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError(f"value vocabulary {source} must contain a YAML mapping")

    return ValueVocabulary.model_validate(raw)
