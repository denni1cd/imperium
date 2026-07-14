# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Main branch:** Stages 0–3 are merged through protocol 1.3.
- **Stage 4 branch:** the complete offline fake/replay engine is implemented in draft PR #8.
- **Validation:** 95 repository tests pass; all six Stage 4 integration paths pass.
- **Generated review artifact:** one complete synthetic council session has been produced and inspected.
- **Merge status:** Stage 4 is not merged and live-provider work is not authorized.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted durable decisions. `docs/STAGE_4_IMPLEMENTATION_PLAN.md` remains the implementation and acceptance contract.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, context isolation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values, versioned configuration, differentiation and vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct challenge turns, evidence ordering/cardinality, halt behavior, bounded rounds, and protocol trace |
| 4 — Offline deliberation engine | Implemented in draft PR #8 | Complete credential-free fake/replay session, halt paths, persistence, resume, exports, CLI, and CI artifacts |
| 5 — Codex provider and live slice | Not started | First isolated live provider only after explicit Stage 4 acceptance |
| 6 — Experiment harness | Not started | Conditions A1, A2, B, and C with frozen controls |
| 7 — Pilot validation | Not started | Repeated blinded evaluation |
| 8 — Investment gate | Not started | Proceed, revise and retest, or stop |
| 9 — First usable local tool | Not started | Durable local UX, provider replacement, exports, and authorization checkpoints |

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

The four advocates and Seneschal retain versioned profiles, normalized vectors, doctrines, vigilance, accepted sacrifices, evidence requirements, revision triggers, operating constraints, and declared counterweights. Human Sustainability remains a known roster-coverage risk for later experiments.

## Stage 4 Implementation

The draft implementation now provides:

- all twelve ordered protocol 1.3 transitions;
- exact preservation of the sovereign request;
- four blind independent interpretations;
- four independent proposals;
- one direct frame challenge;
- a four-member counterweighted proposal round;
- a second proposal round based on a materially revised claim;
- evidence resolution after the challenge phase that created the request;
- gathered, conditional, waiting-for-user, and paused evidence behavior;
- four revisions or reasoned retentions;
- Seneschal hybrid adjudication;
- a preserved Castellan minority objection;
- one complete actionable plan;
- frozen value, council, protocol, prompt, profile, and scenario-structure digests;
- complete own-profile serialization in every advocate context;
- stable call keys and separate provider-call traces;
- atomic pending and completed checkpoints;
- deterministic interruption and resume for the fake/replay provider;
- malformed-checkpoint, frozen-content, scenario-structure, and accepted-artifact tamper rejection;
- session, record, protocol trace, manifest, lineage, transcript, and plan exports;
- a credential-free CLI;
- synthetic-only GitHub Actions artifact publication.

## Validated Paths

The Stage 4 integration suite proves:

1. **Challenged complete session** — reaches `plan_complete` with four interpretations, four proposals, six direct challenge exchanges, four revisions, hybrid adjudication, minority objection, and actionable plan.
2. **No-material-challenge session** — completes with valid empty plans and no fabricated challenge, response, evidence request, or resolution artifacts.
3. **Conditional session** — proceeds only with explicit conditions and remaining uncertainty.
4. **Waiting session** — stops at `waiting_for_user`, accepts explicit replacement evidence, records disposition history, and resumes.
5. **Paused session** — stops at `paused` and performs no revision, adjudication, or plan work.
6. **Interrupted session** — reloads a committed checkpoint without duplicate accepted calls and matches the uninterrupted strategic result.

## Generated Review Session

The current synthetic challenged session contains:

- protocol version `1.3`;
- final stage `plan_complete`;
- final status `complete`;
- 36 separately traced replay-provider turns;
- complete profile digests for every advocate turn;
- no unknown disclosed artifact kinds;
- three challenge plans;
- six authored challenges and six target responses;
- one gathered evidence resolution after proposal debate;
- four final advocate positions;
- one preserved minority objection;
- one three-step actionable plan.

The preserved objection is that deterministic replay does not prove live-provider interruption safety. This must remain visible at the Stage 5 gate.

## Local Hands-On Test

Install and run the complete suite:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
pytest
```

Generate the primary synthetic review session:

```bash
python -m imperium.offline run \
  --scenario challenged \
  --output-dir stage4-output/challenged
```

Inspect:

- `stage4-output/challenged/transcript.md`
- `stage4-output/challenged/plan.json`
- `stage4-output/challenged/lineage.json`
- `stage4-output/challenged/manifest.json`
- `stage4-output/challenged/session.json`

Additional scenarios are `empty`, `conditional`, `waiting`, and `paused`.

## Remaining Before Stage 4 Merge

- [x] Complete offline orchestration
- [x] Freeze configuration, prompts, profiles, and fixture structure
- [x] Enforce context and own-profile boundaries
- [x] Execute direct multi-turn advocate debate
- [x] Exercise revised-claim second round
- [x] Exercise gathered, conditional, waiting, and paused evidence paths
- [x] Implement atomic checkpoint and deterministic fake/replay resume
- [x] Reject tampered accepted replay artifacts
- [x] Publish synthetic review artifacts in CI
- [x] Inspect the generated challenged session
- [ ] Complete final PR review for implementation quality and scope
- [ ] Receive explicit user authorization to merge PR #8

## Remaining Before Live Model Use

- [ ] Accept and merge Stage 4
- [ ] Define the isolated Stage 5 provider boundary
- [ ] Decide how a live provider handles non-idempotent or side-effecting calls
- [ ] Add one bounded live case without experiment infrastructure
- [ ] Review the actual live transcript before any broader integration

## Current Validation Risks

- Scripted artifacts demonstrate execution, not genuine cognitive diversity.
- Numeric profiles have not yet been proven to produce persistent live reasoning differences.
- Human Sustainability may be underrepresented by the fixed roster.
- The two-round rule may prove too permissive or restrictive with live reasoning.
- The Seneschal may still bias synthesis despite formal non-advocacy.
- Full deliberation may not outperform direct advice, equivalent-budget self-critique, or independent advisers.
- Fake/replay resume safety does not establish live-provider exactly-once behavior.

These risks are now ready for later live and controlled validation. They are not reasons to add more Stage 4 architecture.
