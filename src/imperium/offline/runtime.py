"""Freeze exact Stage 4 configuration and prompt content for deterministic resume."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from imperium import __version__
from imperium.configuration import (
    load_council_configuration,
    load_protocol_configuration,
    load_value_vocabulary,
)
from imperium.offline.models import FrozenRuntime, FrozenTextArtifact


def text_sha256(content: str) -> str:
    """Return the lowercase SHA-256 digest of UTF-8 text."""

    return sha256(content.encode("utf-8")).hexdigest()


def freeze_runtime(project_root: str | Path) -> FrozenRuntime:
    """Load approved configuration and freeze every referenced prompt exactly."""

    root = Path(project_root).resolve()
    values_path = root / "config" / "values.yaml"
    council_path = root / "config" / "council.yaml"
    protocol_path = root / "config" / "protocol.yaml"

    vocabulary = load_value_vocabulary(values_path)
    council = load_council_configuration(council_path, vocabulary=vocabulary)
    protocol = load_protocol_configuration(
        protocol_path,
        vocabulary=vocabulary,
        council=council,
    )

    source_paths = {values_path, council_path, protocol_path}
    source_paths.update(
        root / contract.prompt_template
        for contract in protocol.stage_contracts
        if contract.prompt_template
    )
    source_paths.update(
        root / turn.prompt_template
        for contract in protocol.stage_contracts
        for turn in contract.challenge_turns
    )

    frozen: list[FrozenTextArtifact] = []
    for path in sorted(source_paths):
        content = path.read_text(encoding="utf-8")
        frozen.append(
            FrozenTextArtifact(
                path=path.relative_to(root).as_posix(),
                sha256=text_sha256(content),
                content=content,
            )
        )

    return FrozenRuntime(
        package_version=__version__,
        vocabulary=vocabulary,
        council=council,
        protocol=protocol,
        sources=tuple(frozen),
    )
