# Imperium

Imperium is a strategic deliberation system designed to produce better, actionable plans through meaningful disagreement among agents with persistent values and priorities.

## Governing Rule

[`MANIFESTO.md`](MANIFESTO.md) is the project's source of truth. Proposed features, workflows, and architecture must be evaluated against it.

[`docs/DECISIONS.md`](docs/DECISIONS.md) records accepted project decisions and how the manifesto is currently being applied. It does not override the manifesto.

## Current Stage

Imperium remains in **design and validation**.

Stages 1–3 are approved and encoded: the value vocabulary, persistent council profiles, fixed council, and exact deliberation protocol. Stage 4 is implemented on the current draft branch as a complete credential-free fake/replay deliberation from sovereign request to actionable plan.

The Stage 4 implementation proves protocol execution, information boundaries, evidence ordering, halt behavior, persistence, and deterministic resume. It does not prove that live models create genuine cognitive diversity or outperform a capable single adviser.

For the shortest current status and remaining gate, see [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

## Repository Map

- [`MANIFESTO.md`](MANIFESTO.md) — governing project rules
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — durable accepted decisions
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — current implementation and validation status
- [`docs/STRATEGIC_PROJECT_PLAN.md`](docs/STRATEGIC_PROJECT_PLAN.md) — gated roadmap to a first usable implementation
- [`docs/STAGE_4_IMPLEMENTATION_PLAN.md`](docs/STAGE_4_IMPLEMENTATION_PLAN.md) — reviewed Stage 4 scope and acceptance contract
- [`config/values.yaml`](config/values.yaml) — approved value vocabulary 1.0
- [`config/council.yaml`](config/council.yaml) — approved council 1.0
- [`config/protocol.yaml`](config/protocol.yaml) — approved protocol 1.3
- [`prompts/`](prompts/) — stage-specific prompt contracts
- [`src/imperium/offline/`](src/imperium/offline/) — Stage 4 orchestration, fixtures, persistence, rendering, and CLI
- [`tests/integration/test_offline_vertical_slice.py`](tests/integration/test_offline_vertical_slice.py) — complete and halted Stage 4 acceptance paths
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md) — later validation against simpler approaches

## Stage 4 Capabilities

The current draft implementation provides:

- all twelve protocol 1.3 lifecycle transitions;
- four blind advocate interpretations and four independent proposals;
- separate advocate-authored challenge and response turns;
- a materially revised same-phase second-round claim;
- evidence resolution after the challenge phase that created the request;
- gathered, conditional, waiting-for-user, and paused evidence outcomes;
- reasoned revisions or retentions from all four advocates;
- Seneschal hybrid adjudication with a preserved minority objection;
- an actionable plan with steps, checkpoints, risks, and reconsideration conditions;
- exact frozen configuration, profile, protocol, prompt, and scenario-structure digests;
- atomic checkpoints and deterministic fake/replay resume;
- inspectable session, protocol trace, transcript, lineage, manifest, and plan exports;
- synthetic-only GitHub Actions artifacts.

The implementation intentionally excludes live providers, network research, autonomous execution, dynamic council selection, and experiment conditions A1/A2/B/C.

## Local Development

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

Run the primary Stage 4 synthetic council session:

```bash
python -m imperium.offline run \
  --scenario challenged \
  --output-dir stage4-output/challenged
```

Available scenarios are `challenged`, `empty`, `conditional`, `waiting`, and `paused`.

Resume a waiting or paused checkpoint with an explicit synthetic evidence disposition:

```bash
python -m imperium.offline resume \
  --checkpoint stage4-output/waiting/session.json \
  --evidence-outcome gathered
```

Source code lives under `src/imperium/`; tests live under `tests/`.

## Implementation Gate

Stage 4 is implemented but remains in a draft, unmerged pull request pending review of the generated artifacts. Live-model integration must not begin until Stage 4 is explicitly accepted and merged. Imperium is not a coding swarm, roleplaying system, or autonomous execution framework.
