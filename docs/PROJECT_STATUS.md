# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Main branch:** Stages 0–3 are merged through protocol 1.2.
- **Current patch:** protocol 1.3 clarifies evidence and same-phase debate-round ordering.
- **Stage 4:** draft implementation plan only; the offline engine is not implemented or authorized yet.
- **Next engineering milestone:** one complete, resumable synthetic fake/replay deliberation.
- **Best hands-on test:** after Stage 4 produces an inspectable end-to-end session.

`MANIFESTO.md` is the governing source of truth. `DECISIONS.md` records accepted decisions. `STRATEGIC_PROJECT_PLAN.md` remains the gated roadmap.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete | Manifesto, decisions, roadmap, domain contracts, lifecycle foundation, context isolation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete | Nine approved values, versioned configuration, differentiation and vector validation |
| 2 — Profiles and fixed council | Complete | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Protocol 1.3 patch under review | Twelve transitions, blind interpretation, direct challenge turns, evidence/cardinality/halt rules, bounded rounds, protocol trace |
| 4 — Offline deliberation engine | Planned, not implemented | One resumable synthetic/replay run from request to actionable plan |
| 5 — Codex provider and live slice | Not started | First live provider only after Stage 4 works |
| 6 — Experiment harness | Not started | A1, A2, B, and C with frozen controls |
| 7 — Pilot validation | Not started | Repeated blinded evaluation |
| 8 — Investment gate | Not started | Proceed, revise and retest, or stop |
| 9 — First usable local tool | Not started | CLI, durable sessions, exports, provider replacement, authorization checkpoints |

## Approved Strategic Foundation

### Values 1.0

- Ambition
- Urgency
- Economy
- Simplicity
- Resilience
- Optionality
- Leverage
- Adaptability
- Human Sustainability

### Council 1.0

- Seneschal — procedural coordinator and adjudicator
- Accountant (`steward`) — resource discipline
- Gazgul (`vanguard`) — ambition and urgency
- Overmind (`architect`) — leverage and reusable capability
- Castellan (`castellan`) — resilience and downside protection

The four advocates and Seneschal have versioned profiles, normalized vectors, doctrines, vigilance, sacrifices, evidence requirements, revision triggers, constraints, and counterweights. Human Sustainability remains a known roster-coverage risk.

## Approved Protocol Capabilities

Protocol 1.3 contains:

- twelve ordered lifecycle transitions;
- blind independent interpretation;
- normalized frame and proposal claim registers;
- bounded challenge plans;
- advocate-authored challenger and target-response subturns;
- exact empty/nonempty challenge cardinality;
- one evidence resolution per request, including zero;
- waiting and paused halt states;
- evidence resolution after the challenge phase that created the request;
- same-phase second rounds based only on revised claims, new material frames, or other already-permitted input;
- counterweight, materiality, anti-repetition, continuation, and round-limit validation;
- reasoned revision or retention;
- minority-objection preservation;
- Seneschal adjudication and actionable-plan contracts;
- canonical authored challenges in `ProtocolTrace`.

## What Can Run Today

The repository can:

- load and validate values, council, and protocol configuration;
- reject invalid transitions and forbidden artifact kinds;
- validate challenge plans, authored challenges, target responses, and round cardinality;
- validate evidence request-resolution cardinality and halt status;
- validate protocol trace continuity and canonical challenge ownership;
- run fake and replay providers;
- atomically export and reload foundation records;
- run the complete automated contract test suite.

It cannot yet orchestrate a complete council session automatically.

## Stage 4 Hands-On Checkpoint

The local checkpoint should provide one credential-free command that:

1. loads frozen values, profiles, protocol, prompts, and synthetic fixtures;
2. preserves a sample sovereign request;
3. runs all permitted transitions and direct advocate turns;
4. exercises challenge, evidence, waiting, pause, revision, adjudication, and plan paths;
5. exports the authoritative session, frozen manifest, transcript, lineage, and actionable plan;
6. resumes safely after a deliberate interruption.

Expected development commands remain:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
python -m pytest tests/integration/test_offline_vertical_slice.py -vv
```

The Stage 4 integration test and command do not exist yet.

## Remaining Before Stage 4 Implementation

- [ ] Merge the reviewed protocol 1.3 ordering patch
- [ ] Rebase and update PR #8 to protocol 1.3
- [ ] Complete a final manifesto/protocol review of the Stage 4 plan
- [ ] Receive explicit authorization before engine code begins

## Remaining Before Live Model Use

- [ ] Full offline orchestration
- [ ] Frozen session manifest and context/call lineage
- [ ] Deterministic checkpoint and resume
- [ ] Synthetic challenged, empty, conditional, waiting, and paused fixtures
- [ ] CI-generated inspectable session artifacts
- [ ] Review of the actual mocked session

## Current Validation Risks

- Numeric profiles have not been proven to create persistent reasoning differences.
- Human Sustainability may be underrepresented.
- Two debate rounds may be too permissive or restrictive.
- Prompt contracts have not been exercised with a live model.
- Seneschal synthesis may still bias outcomes.
- Full deliberation may not outperform strong single-adviser or independent-panel baselines.

These risks should be tested rather than answered with additional speculative architecture.
