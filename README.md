# Imperium

Imperium is a strategic deliberation system designed to produce better, actionable plans through meaningful disagreement among agents with persistent values and priorities.

## Governing Rule

[`MANIFESTO.md`](MANIFESTO.md) is the project's source of truth. Proposed features, workflows, and architecture must be evaluated against it.

[`docs/DECISIONS.md`](docs/DECISIONS.md) records accepted project decisions and how the manifesto is currently being applied. It does not override the manifesto.

## Current Stage

Imperium is in **design and validation**. Stages 1 and 2 are approved and encoded: the shared strategic value vocabulary, member profile contract, and fixed initial council. The immediate design focus is Stage 3—the exact deliberation protocol.

The project must establish:

1. an approved shared strategic value vocabulary;
2. a persistent council member profile format and fixed initial roster;
3. the exact deliberation lifecycle;
4. a definition and measurement of consequential debate;
5. operational challenge and stopping rules;
6. an experiment comparing direct advice, equivalent-budget self-critique, independent advisers, and the full Imperium process.

## Repository Map

- [`MANIFESTO.md`](MANIFESTO.md) — governing project rules
- [`docs/DECISIONS.md`](docs/DECISIONS.md) — durable accepted decisions
- [`docs/PROJECT_STATUS.md`](docs/PROJECT_STATUS.md) — current stage, readiness, and open work
- [`docs/STRATEGIC_PROJECT_PLAN.md`](docs/STRATEGIC_PROJECT_PLAN.md) — gated roadmap to a first usable implementation
- [`docs/VALUE_VOCABULARY.md`](docs/VALUE_VOCABULARY.md) — approved strategic values and operating rules
- [`config/values.yaml`](config/values.yaml) — versioned machine-readable value vocabulary
- [`docs/COUNCIL_MEMBER_PROFILE.md`](docs/COUNCIL_MEMBER_PROFILE.md) — approved member profile contract
- [`docs/INITIAL_COUNCIL.md`](docs/INITIAL_COUNCIL.md) — approved fixed first-experiment roster
- [`config/council.yaml`](config/council.yaml) — versioned machine-readable member profiles and roster
- [`docs/DELIBERATION_LIFECYCLE.md`](docs/DELIBERATION_LIFECYCLE.md) — controlled council process
- [`docs/CONSEQUENTIAL_DEBATE.md`](docs/CONSEQUENTIAL_DEBATE.md) — standards and measurements for meaningful debate
- [`docs/EXPERIMENT_PLAN.md`](docs/EXPERIMENT_PLAN.md) — validation against simpler approaches

## Supporting Code

The current Python foundation implements accepted, provider-neutral constraints:

- validated deliberation artifacts and normalized value vectors;
- versioned loading and validation of the approved strategic value vocabulary;
- versioned loading and validation of the fixed council and profile contract;
- exact vocabulary compatibility for every member vector;
- explicit separation between advocates and the non-advocating Seneschal;
- differentiation claims, counterweights, and known coverage risks;
- an explicit lifecycle state machine;
- stage-specific information boundaries;
- fake and replay providers for zero-cost testing;
- inspectable JSON session exports;
- tests for constitutional, vocabulary, profile, and roster invariants.

It does not yet finalize stage prompts, claim and frame normalization, challenge assignment, stopping rules, or a live model provider.

### Local Development

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

Source code lives under `src/imperium/`; tests live under `tests/`.

## Implementation Gate

Full offline orchestration should begin only after the Stage 3 lifecycle contracts are explicit enough to simulate deterministically. Imperium is not being designed as a coding swarm, roleplaying system, or autonomous execution framework.
