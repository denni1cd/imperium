"""Local-only Stage 5 Codex smoke command."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from imperium.live.smoke import run_codex_smoke


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run one isolated schema-constrained Codex CLI interpretation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    smoke = subparsers.add_parser("smoke", help="Spend tokens on exactly one live call.")
    smoke.add_argument("--output-dir", type=Path, required=True)
    smoke.add_argument("--model", default="", help="Optional explicit Codex model override.")
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
        model=args.model,
        executable=args.codex_executable,
        timeout_seconds=args.timeout_seconds,
    )
    print(
        f"session={report.session_id} member={report.member_id} provider={report.provider} "
        f"model={report.model} input_tokens={report.input_tokens} "
        f"output_tokens={report.output_tokens} latency_ms={report.latency_ms} "
        f"report={args.output_dir / 'smoke-report.json'}"
    )
    return 0


def main() -> int:
    return asyncio.run(_run(_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
