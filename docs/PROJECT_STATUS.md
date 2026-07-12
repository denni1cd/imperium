# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Main branch:** Stages 0–4 complete and merged.
- **Validation:** 71 Python tests passing, including the resumable end-to-end vertical slice.
- **Current work:** preparing Stage 5, the ChatGPT-authenticated Codex provider.
- **Next milestone:** one isolated live deliberation using the unchanged Stage 4 engine.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted decisions. `STRATEGIC_PROJECT_PLAN.md` remains the gated roadmap.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, roadmap, Pydantic artifacts, lifecycle foundation, context isolation, fake/replay providers, persistence, CI |
| 1 — Shared strategic value vocabulary | Complete and merged | Nine approved values, versioned YAML, differentiation rules, exact vector validation |
| 2 — Member profiles and fixed initial council | Complete and merged | Four advocates, one non-advocating Seneschal, versioned profiles, doctrines, counterweights, known coverage risks |
| 3 — Exact deliberation protocol | Complete and merged | Twelve transitions, claim normalization, challenge assignment, evidence routing, stopping rules, prompt contracts, protocol trace |
| 4 — Offline multi-turn debate engine | Complete and merged | Full fake/replay run, direct confrontation, debate consequences, checkpoints, export, reload, and resume |
| 5 — Codex provider and live vertical slice | Next | Use ChatGPT-authenticated Codex without changing the deliberation engine |
| 6 — Controlled experiment harness | Not started | Conditions A1, A2, B, and C with frozen configurations and metrics |
| 7 — Pilot validation | Not started | Repeated blinded evaluation on representative strategic cases |
| 8 — Investment decision gate | Not started | Proceed, revise and retest, or stop based on evidence |
| 9 — First usable local tool | Not started | CLI, durable sessions, exports, provider replacement, authorization checkpoints |

## What Is Built

### Governance and strategy

- Governing manifesto and authority hierarchy
- Durable decision log
- Gated strategic roadmap
- Explicit recommendation, authorization, and execution boundary
- Evidence-resolution outcomes
- Actionable-plan minimum contract
- Consequential-debate definition and measurements

### Strategic profiles

- Approved vocabulary version `1.0`:
  - Ambition
  - Urgency
  - Economy
  - Simplicity
  - Resilience
  - Optionality
  - Leverage
  - Adaptability
  - Human Sustainability
- Approved council version `1.0`:
  - Seneschal — procedural adjudicator; not an advocate
  - Steward — resource discipline
  - Vanguard — ambition and urgency
  - Architect — leverage and reusable capability
  - Castellan — resilience and downside protection
- Complete vectors, doctrine, vigilance, sacrifices, evidence requirements, revision triggers, operating constraints, and counterweights
- Thematic names isolated as removable presentation metadata
- Human Sustainability preserved as a known roster coverage risk

### Protocol and Python foundation

- Python 3.12 package and strict Pydantic contracts
- Versioned value, council, and protocol configuration
- Deterministic twelve-transition lifecycle
- Explicit information boundaries
- Normalized claim registers
- Material challenge assignment and bounded continuation rules
- Separate frame and proposal evidence stages
- Provider-neutral model interface
- Fake and replay providers
- Atomic JSON persistence
- GitHub Actions validation

### Stage 4 offline engine

- Complete `OfflineDeliberationEngine`
- One atomic checkpoint for every lifecycle transition
- Stop, export, reload, and deterministic resume
- Direct `DebateExchange` records
- Explicit `DebateImpact` links from confrontation to later proposal or revision
- Separate provider calls for challenge selection, challenger articulation, target response, and continuation assessment
- Static offline evidence resolver
- Complete protocol trace in the offline session envelope
- Resumable end-to-end replay test producing adjudication and an actionable plan

## Actual Debate Guarantee

Imperium now distinguishes a real debate from a panel of independent answers.

A full debate requires:

1. the Seneschal selects a material challenge assignment;
2. the assigned challenger articulates the challenge directly;
3. the targeted advocate answers that exact challenge directly;
4. the target later records what changed, strengthened, or became clearer;
5. every assignment has a matching exchange;
6. every exchange has a later strategic consequence;
7. direct confrontation occurs in both frame and proposal phases;
8. at least two distinct advocates are confronted before adjudication.

The following fail verification:

- independent submissions followed by a shared summary;
- a Seneschal speaking for the challenger;
- a challenge with no target response;
- an exchange that has no effect on a later proposal or revision;
- a challenge plan that is never executed;
- only one nominal debate phase before adjudication.

The Stage 4 vertical fixture contains four direct confrontations and four traceable consequences.

## What Can Run Today

The repository can:

- load and validate values, council, and protocol;
- accept a sovereign request;
- run all twelve transitions using replayed or fake structured outputs;
- generate blind independent interpretations;
- execute direct frame confrontation;
- produce independent strategy proposals that account for frame debate;
- execute direct proposal confrontation;
- produce revisions that account for proposal debate;
- block adjudication when actual-debate verification fails;
- produce adjudication and an actionable plan;
- export after each stage;
- reload and resume from an interruption;
- verify the complete record and debate trace.

It does **not yet use a live model**. Stage 5 will add an isolated Codex provider without changing the deliberation engine.

## Hands-On Testing

Stage 4 is the first meaningful local testing checkpoint.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m pytest tests/integration/test_offline_vertical_slice.py -vv
```

The integration test should show that the run:

- pauses after strategy development;
- persists to JSON;
- reloads successfully;
- completes proposal debate and revisions;
- verifies four direct exchanges and four consequences;
- produces the final actionable plan.

## Remaining Before Pilot Validation

- [ ] ChatGPT-authenticated Codex provider
- [ ] Isolated live vertical slice
- [ ] Frozen experiment cases and prompts
- [ ] A1, A2, B, and C experiment runners
- [ ] Blinded evaluation rubric and process
- [ ] Repetition count and minimum improvement threshold
- [ ] Profile-fidelity and Human Sustainability coverage tests

## Current Risks

- The offline engine proves orchestration and auditability, not model reasoning quality.
- Numeric profile differences have not yet been proven to create persistent reasoning differences in live calls.
- The fixed roster may underrepresent Human Sustainability.
- The two-round debate rule may be too permissive or too restrictive.
- The Seneschal may still bias synthesis despite formal non-advocacy.
- The full council may not outperform a strong single adviser or independent panel.

These remain validation risks. They are not reasons to add more architecture before the live vertical slice and controlled experiment are run.
