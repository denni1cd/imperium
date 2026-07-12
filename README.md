# Imperium

Imperium is a strategic deliberation system designed to produce better, actionable plans through meaningful disagreement among agents with persistent values and priorities.

## Governing Rule

[`MANIFESTO.md`](MANIFESTO.md) is the project's source of truth. Proposed features, workflows, and architecture must be evaluated against it.

[`docs/DECISIONS.md`](docs/DECISIONS.md) records accepted project decisions and how the manifesto is currently being applied. It does not override the manifesto.

## Current Stage

Imperium is in **design and validation**. Stages 1–4 are now encoded: the value vocabulary, member profiles and fixed council, exact deliberation protocol, and a complete resumable offline debate engine.

The next engineering target is **Stage 5: an isolated live vertical slice using ChatGPT-authenticated Codex**.

For the shortest current status and testing commands, see [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

## Repository Map

- [`MANIFESTO.md`](MANIFESTO.md) — governing project rules
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — durable accepted decisions
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — mobile-friendly stage status, built capabilities, risks, and test checkpoint
- [`docs/STRATEGIC_PROJECT_PLAN.md`](docs/STRATEGIC_PROJECT_PLAN.md) — gated roadmap to a first usable implementation
- [`docs/VALUE_VOCABULARY.md`](docs/VALUE_VOCABULARY.md) — approved strategic values and operating rules
- [`config/values.yaml`](config/values.yaml) — versioned value vocabulary
- [`docs/COUNCIL_MEMBER_PROFILE.md`](docs/COUNCIL_MEMBER_PROFILE.md) — approved member profile contract
- [`docs/INITIAL_COUNCIL.md`](docs/INITIAL_COUNCIL.md) — approved fixed first-experiment roster
- [`config/council.yaml`](config/council.yaml) — versioned member profiles and roster
- [`docs/DELIBERATION_LIFECYCLE.md`](docs/DELIBERATION_LIFECYCLE.md) — approved twelve-transition protocol
- [`docs/CONSEQUENTIAL_DEBATE.md`](docs/CONSEQUENTIAL_DEBATE.md) — approved materiality, challenge, revision, and measurement rules
- [`config/protocol.yaml`](config/protocol.yaml) — exact stage, evidence, challenge, and stopping contracts
- [`prompts/`](prompts/) — stage-specific and direct-debate prompt interfaces
- [`src/imperium/engine/offline.py`](src/imperium/engine/offline.py) — complete fake/replay deliberation engine
- [`tests/integration/test_offline_vertical_slice.py`](tests/integration/test_offline_vertical_slice.py) — resumable end-to-end debate acceptance test
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md) — validation against simpler approaches

## Supporting Code

The current Python foundation implements:

- validated deliberation artifacts and normalized value vectors;
- versioned loading of values, council, and protocol configuration;
- exact vocabulary and council-version compatibility;
- explicit separation between advocates and the non-advocating Seneschal;
- deterministic lifecycle transitions, including post-proposal evidence resolution;
- stage-specific information boundaries;
- normalized claims, challenge plans, continuation decisions, and protocol traces;
- direct challenger and target turns as separate provider calls;
- traceable debate consequences in later proposals and revisions;
- rejection of panel-only, Seneschal-proxied, unanswered, and consequence-free debate;
- fake and replay providers for zero-cost testing;
- atomic offline checkpoints, JSON export, reload, and resume;
- automated constitutional, profile, protocol, debate, and vertical integration tests.

It does not yet use a live model. The offline engine is deliberately provider-neutral so Stage 5 can add Codex without changing the council process.

### Local Development

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m pytest tests/integration/test_offline_vertical_slice.py -vv
```

Source code lives under `src/imperium/`; tests live under `tests/`.

## Implementation Gate

Live-model integration may begin only after the Stage 4 offline vertical slice remains green. Imperium is not a coding swarm, roleplaying system, or autonomous execution framework.
