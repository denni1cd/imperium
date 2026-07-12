# Imperium

Imperium is a strategic deliberation system designed to produce better, actionable plans through meaningful disagreement among agents with persistent values and priorities.

## Governing Rule

[`MANIFESTO.md`](MANIFESTO.md) is the project's source of truth. Proposed features, workflows, and architecture must be evaluated against it.

[`docs/DECISIONS.md`](docs/DECISIONS.md) records accepted project decisions and how the manifesto is currently being applied. It does not override the manifesto.

## Current Stage

Imperium is in **design and validation**. Stages 1–3 are now explicit and encoded: the value vocabulary, member profiles and fixed council, and the exact deliberation protocol.

The next engineering target is **Stage 4: a complete offline fake/replay deliberation from sovereign request to actionable plan**.

For the shortest current status and recommended testing checkpoint, see [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md).

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
- [`config/protocol.yaml`](config/protocol.yaml) — exact machine-readable stage, evidence, challenge, and stopping contracts
- [`prompts/`](prompts/) — stage-specific prompt interfaces
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md) — validation against simpler approaches

## Supporting Code

The current Python foundation implements accepted, provider-neutral constraints:

- validated deliberation artifacts and normalized value vectors;
- versioned loading of values, council, and protocol configuration;
- exact vocabulary and council-version compatibility;
- explicit separation between advocates and the non-advocating Seneschal;
- deterministic lifecycle transitions, including post-proposal evidence resolution;
- stage-specific information-boundary contracts;
- normalized claim, challenge-plan, continuation-decision, and protocol-trace models;
- deterministic challenge materiality, counterweight, repetition, and stopping checks;
- fake and replay providers for zero-cost testing;
- inspectable JSON session exports;
- automated constitutional, vocabulary, profile, roster, lifecycle, and protocol tests.

It does not yet connect every stage into one complete offline deliberation. Stage 4 will provide that vertical slice before Codex or API integration.

### Local Development

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

Source code lives under `src/imperium/`; tests live under `tests/`.

## Implementation Gate

Live-model integration should begin only after the Stage 4 offline engine completes and resumes a full deliberation using fake or replay providers. Imperium is not a coding swarm, roleplaying system, or autonomous execution framework.
