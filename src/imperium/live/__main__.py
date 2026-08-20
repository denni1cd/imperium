"""Local-only Stage 5 Codex smoke command."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from pydantic import TypeAdapter

from imperium.domain.models import EvidenceResolution
from imperium.live.gate import (
    LIVE_AUTHORIZATION,
    estimate_council_gate,
    replay_council_capture,
    resume_live_council_evidence,
    retry_live_council_attempt,
    run_live_council_gate,
)
from imperium.live.smoke import run_codex_smoke
from imperium.offline.attempts import UsageBudget
from imperium.offline.provider_engine import ProviderBoundDeliberationEngine
from imperium.providers.codex_cli import (
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_REASONING_EFFORT,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run bounded Stage 5 Codex workflows using "
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

    estimate = subparsers.add_parser(
        "council-estimate",
        help="Estimate the full-council expected path with replay and zero live calls.",
    )
    estimate.add_argument("--output-dir", type=Path, required=True)

    council = subparsers.add_parser(
        "council",
        help="Spend tokens on one complete fixed-council Gate 2F run.",
    )
    council.add_argument("--output-dir", type=Path, required=True)
    council.add_argument("--codex-executable", default="codex")
    council.add_argument("--timeout-seconds", type=float, default=300.0)
    council.add_argument(
        "--authorize",
        required=True,
        help=f"Must be exactly {LIVE_AUTHORIZATION!r}.",
    )

    replay = subparsers.add_parser(
        "council-replay",
        help="Replay a captured council session with zero live calls.",
    )
    replay.add_argument("--capture", type=Path, required=True)
    replay.add_argument("--output-dir", type=Path, required=True)

    evidence = subparsers.add_parser(
        "council-resume-evidence",
        help="Resume a halted live council with explicit evidence dispositions.",
    )
    evidence.add_argument("--checkpoint", type=Path, required=True)
    evidence.add_argument("--evidence", type=Path, required=True)
    evidence.add_argument("--output-dir", type=Path, required=True)
    evidence.add_argument("--codex-executable", default="codex")
    evidence.add_argument("--timeout-seconds", type=float, default=300.0)
    evidence.add_argument("--authorize", required=True)

    retry = subparsers.add_parser(
        "council-retry",
        help="Authorize one reasoned replacement attempt and continue the live council.",
    )
    retry.add_argument("--checkpoint", type=Path, required=True)
    retry.add_argument("--output-dir", type=Path, required=True)
    retry.add_argument("--reason", required=True)
    retry.add_argument("--codex-executable", default="codex")
    retry.add_argument("--timeout-seconds", type=float, default=300.0)
    retry.add_argument("--authorize", required=True)

    abandon = subparsers.add_parser(
        "council-abandon",
        help="Abandon one unresolved live attempt without launching a provider.",
    )
    abandon.add_argument("--checkpoint", type=Path, required=True)
    abandon.add_argument("--output-dir", type=Path, required=True)
    abandon.add_argument("--reason", required=True)

    for command in (estimate, council):
        command.add_argument("--max-attempts", type=int, default=64)
        command.add_argument("--max-attempts-per-call", type=int, default=2)
        command.add_argument("--max-input-tokens", type=int, default=2_000_000)
        command.add_argument("--max-cached-input-tokens", type=int, default=2_000_000)
        command.add_argument("--max-output-tokens", type=int, default=250_000)
        command.add_argument("--output-token-reserve", type=int, default=4_096)
    return parser


def _budget(args: argparse.Namespace) -> UsageBudget:
    return UsageBudget(
        max_attempts=args.max_attempts,
        max_attempts_per_call=args.max_attempts_per_call,
        max_input_tokens=args.max_input_tokens,
        max_cached_input_tokens=args.max_cached_input_tokens,
        max_output_tokens=args.max_output_tokens,
        output_token_reserve_per_attempt=args.output_token_reserve,
    )


def _print_gate_result(result) -> None:
    print(
        f"session={result.session_id} calls={result.call_count} "
        f"input_tokens={result.input_tokens} output_tokens={result.output_tokens} "
        f"structural_pass={result.assessment.structural_pass} "
        f"replay_verified={result.replay_verified} human_review_required=true"
    )


async def _run(args: argparse.Namespace) -> int:
    root = Path(__file__).resolve().parents[3]
    if args.command == "smoke":
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
    if args.command == "council-estimate":
        estimate = await estimate_council_gate(
            project_root=root,
            output_dir=args.output_dir,
            usage_budget=_budget(args),
        )
        print(
            f"expected_calls={estimate.expected_path_calls} "
            f"protocol_call_ceiling={estimate.protocol_call_ceiling} "
            f"estimated_input_tokens={estimate.estimated_input_tokens} "
            f"reserved_output_tokens={estimate.reserved_output_tokens}"
        )
        return 0
    if args.command == "council":
        result = await run_live_council_gate(
            project_root=root,
            output_dir=args.output_dir,
            authorization=args.authorize,
            usage_budget=_budget(args),
            executable=args.codex_executable,
            timeout_seconds=args.timeout_seconds,
        )
        _print_gate_result(result)
        return 0
    if args.command == "council-replay":
        session = await replay_council_capture(
            project_root=root,
            capture_path=args.capture,
            output_dir=args.output_dir,
        )
        print(
            f"session={session.session_id} calls={len(session.completed_call_keys)} provider=replay"
        )
        return 0
    if args.command == "council-resume-evidence":
        evidence = TypeAdapter(tuple[EvidenceResolution, ...]).validate_json(
            args.evidence.read_text(encoding="utf-8")
        )
        result = await resume_live_council_evidence(
            project_root=root,
            gate_dir=args.output_dir,
            checkpoint=args.checkpoint,
            authorization=args.authorize,
            evidence_replacements=evidence,
            executable=args.codex_executable,
            timeout_seconds=args.timeout_seconds,
        )
        _print_gate_result(result)
        return 0
    if args.command == "council-retry":
        result = await retry_live_council_attempt(
            project_root=root,
            gate_dir=args.output_dir,
            checkpoint=args.checkpoint,
            authorization=args.authorize,
            reason=args.reason,
            executable=args.codex_executable,
            timeout_seconds=args.timeout_seconds,
        )
        _print_gate_result(result)
        return 0
    if args.command == "council-abandon":
        session = ProviderBoundDeliberationEngine(model=DEFAULT_CODEX_MODEL).abandon_attempt(
            args.checkpoint,
            reason=args.reason,
            output_dir=args.output_dir / "live",
        )
        print(f"session={session.session_id} status={session.status.value} provider_calls=0")
        return 0
    raise ValueError(f"unsupported live command: {args.command}")


def main() -> int:
    return asyncio.run(_run(_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
