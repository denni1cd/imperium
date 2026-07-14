# Imperium

Imperium is a strategic deliberation system designed to produce better, actionable plans through meaningful disagreement among agents with persistent values and priorities.

## Governing Rule

[`MANIFESTO.md`](MANIFESTO.md) is the project's source of truth. Proposed features, workflows, and architecture must be evaluated against it.

[`docs/DECISIONS.md`](docs/DECISIONS.md) records accepted project decisions and how the manifesto is currently being applied. It does not override the manifesto.

## Current Stage

Imperium remains in **design and validation**.

Stages 1–4 are complete and merged: the value vocabulary, persistent council profiles, fixed council, exact deliberation protocol, and complete credential-free replay engine.

Stage 5 has begun with the smallest live gate: one isolated ChatGPT-authenticated Codex CLI call producing one schema-valid `Interpretation`. A complete live council run is not attempted until that smoke test succeeds locally.

For the current status and next gate, see [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

## Repository Map

- [`MANIFESTO.md`](MANIFESTO.md) — governing project rules
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — durable accepted decisions
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — current implementation and validation status
- [`docs/STRATEGIC_PROJECT_PLAN.md`](docs/STRATEGIC_PROJECT_PLAN.md) — gated roadmap
- [`docs/STAGE_4_IMPLEMENTATION_PLAN.md`](docs/STAGE_4_IMPLEMENTATION_PLAN.md) — completed offline-engine acceptance contract
- [`docs/STAGE_5_IMPLEMENTATION_PLAN.md`](docs/STAGE_5_IMPLEMENTATION_PLAN.md) — bounded Codex provider and live-slice gates
- [`config/values.yaml`](config/values.yaml) — approved value vocabulary 1.0
- [`config/council.yaml`](config/council.yaml) — approved council 1.0
- [`config/protocol.yaml`](config/protocol.yaml) — approved protocol 1.3
- [`prompts/`](prompts/) — stage-specific prompt contracts
- [`src/imperium/offline/`](src/imperium/offline/) — merged Stage 4 orchestration, persistence, rendering, and CLI
- [`src/imperium/providers/codex_cli.py`](src/imperium/providers/codex_cli.py) — Stage 5 isolated Codex CLI adapter
- [`src/imperium/live/`](src/imperium/live/) — local-only live smoke workflow
- [`tests/integration/test_offline_vertical_slice.py`](tests/integration/test_offline_vertical_slice.py) — complete and halted Stage 4 acceptance paths
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md) — later validation against simpler approaches

## Stage 4 Capabilities

The merged offline engine provides:

- all twelve protocol 1.3 lifecycle transitions;
- four blind interpretations and four independent proposals;
- direct advocate-authored challenge and response turns;
- revised-claim second-round debate;
- evidence resolution after the originating challenge phase;
- gathered, conditional, waiting, and paused outcomes;
- four revisions or retentions;
- Seneschal hybrid adjudication with a preserved minority objection;
- actionable plan generation;
- frozen configuration, profile, protocol, prompt, and scenario digests;
- atomic checkpoints and deterministic replay resume;
- inspectable session, trace, transcript, lineage, manifest, and plan exports;
- synthetic-only GitHub Actions artifacts.

Stage 4 proves process execution. It does not prove live profile fidelity or superiority over a strong single adviser.

## Local Development

```bash
python -m pip install -e ".[dev]"
pytest
```

Run the primary replay council session:

```bash
python -m imperium.offline run \
  --scenario challenged \
  --output-dir stage4-output/challenged
```

Available replay scenarios are `challenged`, `empty`, `conditional`, `waiting`, and `paused`.

## Stage 5 Codex Smoke

Prerequisites:

1. Install the Codex CLI.
2. Run `codex` once and sign in with ChatGPT.
3. Confirm `codex --version` works in the same terminal.

Spend tokens on exactly one isolated Accountant interpretation:

```bash
python -m imperium.live smoke \
  --output-dir stage5-output/smoke
```

Optionally freeze an explicit model for the call:

```bash
python -m imperium.live smoke \
  --model <codex-model> \
  --output-dir stage5-output/smoke
```

The command uses an empty temporary workspace, read-only sandbox, ephemeral Codex session, schema-constrained final output, no inherited project rules, and no automatic retry. It writes `smoke-report.json` plus local JSONL events for review.

A complete live council deliberation remains blocked until this single-call gate succeeds and is inspected.

## Project Boundary

Imperium is not a coding swarm, roleplaying system, or autonomous execution framework. Live-model integration remains subordinate to strategic deliberation, explicit information boundaries, inspectable artifacts, and user authorization.
