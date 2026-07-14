"""Local-only Stage 5 Codex smoke command."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from imperium.live.smoke import run_codex_smoke
from imperium.providers.codex_cli import (
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_REASONING_EFFORT,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run one isolated schema-constrained Codex CLI interpretation using "
            f"{DEFAULT_CODEX_MODEL} with {DEFAULT_CODEX_REASONING_EFFORT} reasoning."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    smoke = subparsers.add_parser(
        "smoke",
        help="Spend tokens on exactly one Terra Light live call.",
    )
    smoke.add_argument("--output-dir", type=Path, required=True)
    smoke.add_argument("--codex-executable", default="codex")
    smoke.add_argument("--timeout-seconds", type=float, default=300.0)
    return parser


async def _run(args: argparse.Namespace) -> int:
    if args.command != "smoke":
        raise ValueError(f"unsupported live command: {args.command}")
    root = Path(__file__).resolve().parents[3]
    report = await run_codex_smoke(
        project_root=root,
        output_dir=args.output_dir,
        executable=args.codex_executable,
        timeout_seconds=args.timeout_seconds,
    )
    print(
        f"session={report.session_id} member={report.member_id} provider={report.provider} "
        f"model={report.model} reasoning={DEFAULT_CODEX_REASONING_EFFORT} "
        f"input_tokens={report.input_tokens} output_tokens={report.output_tokens} "
        f"latency_ms={report.latency_ms} report={args.output_dir / 'smoke-report.json'}"
    )
    return 0


def main() -> int:
    return asyncio.run(_run(_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
