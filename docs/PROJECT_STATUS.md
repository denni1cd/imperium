# Project Status

## Current Position

Imperium remains in **design and validation**, with the constitutional, council, and protocol contracts now explicit through protocol version `1.2`.

- **Main branch:** Stages 0–3 complete and merged through protocol 1.1.
- **Current patch:** protocol 1.2 resolves conditional output, evidence cardinality, halt, and canonical-record blockers before Stage 4.
- **Current Stage 4 work:** draft implementation plan only; no offline engine code is authorized yet.
- **Next engineering milestone:** one complete, resumable fake/replay deliberation.
- **Best next hands-on test:** after Stage 4 produces the end-to-end vertical slice and its inspectable artifacts.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted decisions. `STRATEGIC_PROJECT_PLAN.md` remains the gated roadmap.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, roadmap, Pydantic artifacts, lifecycle foundation, context isolation, fake/replay providers, persistence, CI |
| 1 — Shared strategic value vocabulary | Complete and merged | Nine approved values, versioned YAML, differentiation rules, exact vector validation |
| 2 — Member profiles and fixed initial council | Complete and merged | Four advocates, one non-advocating Seneschal, versioned profiles, doctrines, counterweights, known coverage risks |
| 3 — Exact deliberation protocol | Protocol 1.2 patch under review | Twelve transitions, blind interpretation, advocate-authored challenges, conditional outputs, evidence routing/cardinality, halt behavior, stopping rules, protocol trace |
| 4 — Complete offline deliberation engine | Planned, not implemented | Wire every approved stage and subturn into one resumable fake/replay run from request to actionable plan |
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
  - Accountant — resource discipline (`steward` internal office)
  - Gazgul — ambition and urgency (`vanguard` internal office)
  - Overmind — leverage and reusable capability (`architect` internal office)
  - Castellan — resilience and downside protection
- Complete vectors, doctrine, vigilance, sacrifices, evidence requirements, revision triggers, operating constraints, and counterweights
- Council names isolated as removable presentation metadata
- Internal stable IDs remain `seneschal`, `steward`, `vanguard`, `architect`, and `castellan`
- Human Sustainability preserved as a known roster coverage risk

### Python foundation

- Python 3.12 package
- Strict Pydantic domain models
- Normalized value-vector enforcement
- Versioned YAML loaders for values, council, and protocol
- Deterministic lifecycle state machine
- Explicit information-boundary context builder
- Provider-neutral model interface
- Fake and replay providers
- Atomic JSON record export and reload
- Cross-record validation
- GitHub Actions test workflow

### Stage 3 protocol capabilities

- Versioned `config/protocol.yaml`
- Exact contract for every lifecycle transition
- Typed normalized claim registers
- Typed challenge plans and assignments
- Advocate-authored challenger and target-response subturns
- Typed continuation and stopping decisions
- Deterministic materiality, counterweight, repetition, and round-limit checks
- Conditional challenge outputs: zero exchanges for empty plans, one exchange per assignment otherwise
- Exact evidence cardinality: one resolution per request, including zero
- User-wait and deliberation-pause status rules
- Explicit post-proposal evidence-resolution stage
- Evidence-routing thresholds
- Two-round debate safety rule preserving unresolved issues
- Abbreviated path defined but disabled for initial experiments
- Stage-specific prompt contracts under `prompts/`
- Typed `ProtocolTrace` as the canonical challenge and protocol record fragment

## What Can Run Today

The repository can currently:

- load and validate the value vocabulary;
- load and validate the fixed council;
- load and validate the protocol configuration;
- reject invalid stage transitions;
- reject leaked or forbidden artifact kinds;
- validate challenge targeting, materiality, counterweights, repetition, and stopping decisions;
- validate authored challenger and target ownership;
- validate empty and nonempty challenge-round cardinality;
- validate evidence request-resolution cardinality and halt status;
- simulate provider responses through fake and replay providers;
- export and reload validated foundation records;
- run the automated contract test suite.

It **cannot yet run a complete council deliberation automatically**. Stage 4 must connect the approved pieces into one orchestrated vertical slice.

## Recommended Hands-On Testing Point

The best point for local use is the end of Stage 4, when one command should:

1. load frozen values, council, protocol, prompts, and fake/replay responses;
2. accept a synthetic sample sovereign request;
3. advance through all twelve transitions when no halt outcome blocks progress;
4. execute separate challenger and target calls;
5. enforce information boundaries and output cardinality;
6. exercise evidence continuation, waiting, and pause paths;
7. produce revisions, adjudication, and an actionable plan;
8. export the authoritative session, protocol trace, readable transcript, lineage, and plan;
9. resume safely after a deliberate interruption.

Expected local validation commands remain:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m pytest tests/integration/test_offline_vertical_slice.py -vv
```

The Stage 4 integration test does not exist yet.

## Remaining Before Stage 4 Implementation

- [ ] Merge the reviewed protocol 1.2 patch
- [ ] Rebase and update the Stage 4 plan to protocol 1.2
- [ ] Freeze prompt/configuration content requirements in the Stage 4 session envelope
- [ ] Require positive minority-objection and hybrid-or-no-hybrid acceptance paths
- [ ] Require synthetic-only CI artifacts and exact profile projection boundaries
- [ ] Approve the final Stage 4 scope before coding

## Remaining Before Live Model Use

- [ ] Connect contracts into full offline orchestration
- [ ] Attach `ProtocolTrace` to the authoritative offline session envelope
- [ ] Add deterministic stage and challenge-subturn runners
- [ ] Add interruption and resume behavior
- [ ] Complete fake-provider vertical integration tests
- [ ] Add realistic replay fixture sets
- [ ] Review generated offline session artifacts

## Remaining Before Pilot Validation

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
- Prompt contracts have not yet been exercised with a live model.
- The Seneschal may still bias synthesis despite formal non-advocacy; blinded testing must detect this.
- The full council may not outperform a strong single adviser or independent panel.

These are validation risks, not reasons to add more architecture before the current protocol is tested.
