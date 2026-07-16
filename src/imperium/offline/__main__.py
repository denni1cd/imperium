"""Credential-free command line entry point for Stage 4 synthetic sessions."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from imperium.domain.enums import EvidenceOutcome
from imperium.offline.provider_engine import OfflineDeliberationEngine
from imperium.offline.fixtures import build_challenged_scenario, scenario_by_name
from imperium.offline.persistence import load_session


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Imperium Stage 4 offline engine.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Run a new synthetic scenario.")
    run.add_argument(
        "--scenario",
        choices=("challenged", "empty", "conditional", "waiting", "paused"),
        default="challenged",
    )
    run.add_argument("--output-dir", type=Path, required=True)

    resume = subparsers.add_parser("resume", help="Resume a checkpointed session.")
    resume.add_argument("--checkpoint", type=Path, required=True)
    resume.add_argument("--output-dir", type=Path)
    resume.add_argument(
        "--evidence-outcome",
        choices=("gathered", "proceed_conditionally"),
        help="Explicit replacement for a waiting or paused evidence disposition.",
    )
    return parser


async def _run(args: argparse.Namespace) -> int:
    engine = OfflineDeliberationEngine()
    if args.command == "run":
        root = Path(__file__).resolve().parents[3]
        session = await engine.run(
            scenario_by_name(args.scenario),
            project_root=root,
            output_dir=args.output_dir,
        )
    else:
        replacements = ()
        if args.evidence_outcome:
            outcome = EvidenceOutcome(args.evidence_outcome)
            completed = build_challenged_scenario(evidence_outcome=outcome)
            checkpoint_session = load_session(args.checkpoint)
            known_ids = {
                request.evidence_request_id
                for request in checkpoint_session.record.evidence_requests
            }
            replacements = tuple(
                resolution
                for resolution in completed.proposal_evidence_resolutions
                if resolution.evidence_request_id in known_ids
            )
        session = await engine.resume(
            args.checkpoint,
            output_dir=args.output_dir,
            evidence_replacements=replacements,
        )

    print(
        f"session={session.session_id} stage={session.record.stage.value} "
        f"status={session.record.status.value} calls={len(session.turns)}"
    )
    return 0


def main() -> int:
    return asyncio.run(_run(_parser().parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
