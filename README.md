# Imperium

Imperium is a strategic deliberation system designed to produce better, actionable plans through meaningful disagreement among agents with persistent values and priorities.

## Governing Rule

[`MANIFESTO.md`](MANIFESTO.md) is the project's source of truth. Proposed features, workflows, and architecture must be evaluated against it.

[`docs/DECISIONS.md`](docs/DECISIONS.md) records accepted project decisions and how the manifesto is currently being applied. It does not override the manifesto.

## Current Stage

Imperium remains in **design and validation**.

Stages 0–4 are complete and merged. Stage 5 draft PR #12 implements the first bounded live-provider gate: one isolated ChatGPT-authenticated Codex interpretation before any complete live council run.

The first local call reached Codex but exposed a Pydantic/OpenAI schema mismatch. The branch now includes a reversible Structured Outputs adapter and passes 102 tests; the corrected one-call smoke must be rerun locally before provider injection.

For the current status and next gate, see [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

## Repository Map

- [`MANIFESTO.md`](MANIFESTO.md) — governing project rules
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — durable accepted decisions
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — current implementation and validation status
- [`docs/STRATEGIC_PROJECT_PLAN.md`](docs/STRATEGIC_PROJECT_PLAN.md) — gated roadmap
- [`docs/STAGE_4_IMPLEMENTATION_PLAN.md`](docs/STAGE_4_IMPLEMENTATION_PLAN.md) — accepted Stage 4 contract
- [`docs/STAGE_5_CODEX_PROVIDER_PLAN.md`](docs/STAGE_5_CODEX_PROVIDER_PLAN.md) — current live-provider gates
- [`config/values.yaml`](config/values.yaml) — approved vocabulary 1.0
- [`config/council.yaml`](config/council.yaml) — approved council 1.0
- [`config/protocol.yaml`](config/protocol.yaml) — approved protocol 1.3
- [`prompts/`](prompts/) — stage-specific prompt contracts
- [`src/imperium/offline/`](src/imperium/offline/) — merged Stage 4 orchestration
- [`src/imperium/providers/codex_cli.py`](src/imperium/providers/codex_cli.py) — bounded Stage 5 Codex process adapter
- [`src/imperium/providers/openai_schema.py`](src/imperium/providers/openai_schema.py) — reversible Structured Outputs schema adapter
- [`src/imperium/live/`](src/imperium/live/) — one-call live smoke command
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md) — later controlled validation

## Stage 4 Capabilities

The merged implementation provides:

- all twelve protocol 1.3 lifecycle transitions;
- four blind advocate interpretations and four independent proposals;
- separate advocate-authored challenge and response turns;
- a materially revised same-phase second-round claim;
- evidence resolution after the originating challenge phase;
- gathered, conditional, waiting-for-user, and paused outcomes;
- reasoned revisions or retentions;
- Seneschal hybrid adjudication with a preserved objection;
- actionable plan output;
- frozen configuration, profile, protocol, prompt, and scenario digests;
- atomic checkpoints and deterministic replay resume;
- inspectable session, trace, transcript, lineage, manifest, and plan exports;
- synthetic-only GitHub Actions artifacts.

## Stage 5 Gate 1

The live provider uses:

- one fresh `codex exec` process;
- an empty temporary workspace;
- read-only sandboxing;
- no approval prompts;
- an ephemeral session;
- ignored repository rules and user configuration;
- prompt input over stdin;
- strict structured output;
- no automatic retry.

Pydantic schemas are adapted to OpenAI Structured Outputs by requiring every object field, closing every object, removing unsupported annotations, and encoding arbitrary dictionaries as reversible key/value entry arrays.

## Local Development

```powershell
python -m pip install -e ".[dev]"
pytest
```

Run the Stage 4 synthetic session:

```powershell
python -m imperium.offline run --scenario challenged --output-dir stage4-output\challenged
```

Run exactly one Stage 5 live call:

```powershell
python -m imperium.live smoke --output-dir stage5-output\smoke
```

Inspect:

- `stage5-output/smoke/smoke-report.json`
- `stage5-output/smoke/events/stage5-smoke_interpretation_steward.jsonl`

Do not automatically rerun a failed live call. Preserve the exact error and correct the provider boundary first.

## Implementation Gate

A successful one-call smoke does not authorize a full live council by itself. Review the returned Accountant interpretation and metadata first. Provider injection into the Stage 4 engine is the next separately validated change.

Imperium is not a coding swarm, roleplaying system, or autonomous execution framework.
