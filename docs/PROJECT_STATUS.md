# Project Status

## Current Position

Imperium remains in **design and validation**, but the constitutional and protocol design is now largely explicit.

- **Main branch:** Stages 0–2 complete and merged.
- **Current work:** Stage 3 exact deliberation protocol on `agent/stage-3-deliberation-protocol`.
- **Next engineering stage:** Stage 4 offline deliberation engine.
- **Best next hands-on test:** after Stage 4 completes one end-to-end fake/replay deliberation.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted decisions. `STRATEGIC_PROJECT_PLAN.md` remains the gated roadmap.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, roadmap, Pydantic artifacts, lifecycle foundation, context isolation, fake/replay providers, persistence, CI |
| 1 — Shared strategic value vocabulary | Complete and merged | Nine approved values, versioned YAML, differentiation rules, exact vector validation |
| 2 — Member profiles and fixed initial council | Complete and merged | Four advocates, one non-advocating Seneschal, versioned profiles, doctrines, counterweights, known coverage risks |
| 3 — Exact deliberation protocol | Implemented on current branch; awaiting CI and merge | Twelve transitions, claim normalization, challenge assignment, evidence routing, stopping rules, prompt contracts, protocol trace |
| 4 — Complete offline deliberation engine | Next | Wire all stages into one resumable fake/replay run from request to actionable plan |
| 5 — Codex provider and live vertical slice | Not started | Use ChatGPT-authenticated Codex only after the offline engine works |
| 6 — Controlled experiment harness | Not started | Conditions A1, A2, B, and C with frozen configurations and metrics |
| 7 — Pilot validation | Not started | Repeated blinded evaluation on representative strategic cases |
| 8 — Investment decision gate | Not started | Proceed, revise and retest, or stop based on evidence |
| 9 — First usable local tool | Not started | CLI, durable sessions, exports, provider replacement, authorization checkpoints |

## What Is Built

### Governance and design

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

### Python foundation

- Python 3.12 package
- Strict Pydantic domain models
- Normalized value-vector enforcement
- Versioned YAML loaders for values and council
- Deterministic lifecycle state machine
- Explicit information-boundary context builder
- Provider-neutral model interface
- Fake and replay providers
- Atomic JSON session export and reload
- Cross-record validation
- GitHub Actions test workflow

### Stage 3 additions

- Versioned `config/protocol.yaml`
- Exact contract for every lifecycle transition
- Explicit post-proposal evidence-resolution stage
- Typed normalized claim registers
- Typed challenge plans and assignments
- Typed continuation and stopping decisions
- Deterministic materiality, counterweight, repetition, and round-limit checks
- Evidence-routing thresholds
- Two-round debate safety rule that preserves unresolved issues instead of truncating them
- Abbreviated path defined but disabled for initial experiments
- Stage-specific prompt contracts under `prompts/`
- Typed `ProtocolTrace` for Stage 4 session integration

## What Can Run Today

The repository can currently:

- load and validate the value vocabulary;
- load and validate the fixed council;
- load and validate the complete Stage 3 protocol;
- reject invalid stage transitions;
- reject leaked or forbidden stage artifacts;
- validate challenge targeting, materiality, counterweights, repetition, and stopping decisions;
- simulate provider responses through fake and replay providers;
- export and reload validated session records;
- run the full automated contract test suite.

It **cannot yet run a complete council deliberation automatically**. The individual pieces exist, but Stage 4 must connect them into one orchestrated vertical slice.

## Recommended Hands-On Testing Point

The best point for the user to get to a computer and run Imperium is **the end of Stage 4**, not immediately after Stage 3.

That checkpoint should provide one command or integration test that:

1. loads values, council, protocol, and fake/replay responses;
2. accepts a sample sovereign request;
3. advances through all twelve transitions;
4. enforces every information boundary and output contract;
5. resolves both evidence stages;
6. produces revisions, adjudication, and an actionable plan;
7. exports the complete record and protocol trace;
8. can be resumed or inspected after a deliberate interruption.

At that point, hands-on testing will evaluate the actual workflow rather than only schemas.

Expected local validation commands will be:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m pytest tests/integration/test_offline_vertical_slice.py -vv
```

The integration-test path is a Stage 4 target and does not exist yet.

## Protocol Readiness

### Approved

- [x] Governing manifesto and actionable-plan objective
- [x] Authority hierarchy and action boundary
- [x] Evidence-resolution routes
- [x] Shared value vocabulary
- [x] Member profile contract
- [x] Fixed initial council and matrices
- [x] Blind independent interpretation
- [x] Exact stage inputs, outputs, and artifact visibility
- [x] Claim and frame normalization method
- [x] Challenge-assignment policy
- [x] Operational continuation and stopping rules
- [x] Stage-specific prompt contracts
- [x] Required protocol trace
- [x] Abbreviated-path rules, disabled for initial experiments

### Remaining before live model use

- [ ] Connect contracts into full offline orchestration
- [ ] Attach `ProtocolTrace` to the authoritative session record
- [ ] Add deterministic stage runners
- [ ] Add interruption and resume behavior
- [ ] Complete fake-provider vertical integration test
- [ ] Add realistic replay fixture set

### Remaining before pilot validation

- [ ] Codex provider and isolated live vertical slice
- [ ] Frozen experiment cases and prompts
- [ ] A1, A2, B, and C experiment runners
- [ ] Blinded evaluation rubric and process
- [ ] Repetition count and minimum improvement threshold
- [ ] Profile-fidelity and human-sustainability coverage tests

## Current Risks

- Numeric profile differences have not yet been proven to create persistent reasoning differences.
- The fixed roster may underrepresent Human Sustainability.
- The two-round debate rule may be too permissive or too restrictive; experiments must test it.
- Prompt contracts are approved but have not yet been exercised with a live model.
- The Seneschal may still bias synthesis despite formal non-advocacy; blinded testing must detect this.
- The full council may not outperform a strong single adviser or independent panel.

These are validation risks, not reasons to add more architecture before the current protocol is tested.
