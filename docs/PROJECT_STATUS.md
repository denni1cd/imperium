# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Stages 0–4:** complete and merged.
- **Stage 4 merge:** PR #8, squash commit `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- **Offline validation:** 95 repository tests and six Stage 4 integration paths passed before merge.
- **Local review:** the generated challenged replay session was accepted.
- **Stage 5:** started on branch `stage-5-codex-provider` with a one-call Codex CLI smoke gate.
- **Live council status:** not yet run.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted durable decisions. `docs/STAGE_5_IMPLEMENTATION_PLAN.md` defines the current live-provider gate.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values and normalized vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct debate, evidence ordering/cardinality, halt behavior, and bounded rounds |
| 4 — Offline deliberation engine | Complete and merged | Full replay orchestration, halt paths, checkpoints, resume, exports, CLI, and synthetic review artifacts |
| 5 — Codex provider and live slice | Provider smoke in progress | One isolated schema-valid live Interpretation before any full council run |
| 6 — Experiment harness | Not started | Conditions A1, A2, B, and C with frozen controls |
| 7 — Pilot validation | Not started | Repeated blinded evaluation |
| 8 — Investment gate | Not started | Proceed, revise and retest, or stop |
| 9 — First usable local tool | Not started | Durable local UX, provider replacement, exports, and authorization checkpoints |

## Approved Strategic Foundation

### Values 1.0

Ambition, Urgency, Economy, Simplicity, Resilience, Optionality, Leverage, Adaptability, and Human Sustainability.

### Council 1.0

- Seneschal — procedural coordinator and adjudicator
- Accountant (`steward`) — resource discipline
- Gazgul (`vanguard`) — ambition and urgency
- Overmind (`architect`) — leverage and reusable capability
- Castellan (`castellan`) — resilience and downside protection

### Protocol 1.3

The approved protocol contains twelve ordered transitions, blind interpretation, claim-specific direct debate, evidence resolution after the originating challenge phase, reasoned revision or retention, minority-objection preservation, non-voting adjudication, and actionable-plan generation.

## Stage 4 Accepted Result

The merged replay engine demonstrates:

- exact protocol execution;
- four isolated blind interpretations;
- four proposals;
- direct advocate-authored challenge and response turns;
- one revised-claim second proposal round;
- gathered, conditional, waiting, paused, and interrupted paths;
- four final advocate positions;
- hybrid adjudication;
- a preserved Castellan minority objection;
- actionable plan output;
- frozen inputs, context tracing, atomic checkpoints, tamper rejection, resume, and replay;
- credential-free local CLI and synthetic-only CI artifacts.

Stage 4 proves execution and inspectability. It does not prove genuine live cognitive diversity or an advantage over a single adviser.

## Stage 5 Gate 1

The central unproven assumption is that one fresh ChatGPT-authenticated Codex CLI process can receive an isolated Imperium prompt and context and return one schema-valid domain artifact.

The current branch implements:

- `CodexCliProvider` satisfying the existing provider protocol;
- one fresh `codex exec` process per call;
- empty temporary workspace;
- read-only sandbox;
- ephemeral session;
- ignored project rules and user configuration while preserving Codex authentication;
- JSON Schema-constrained final output;
- prompt delivery through stdin;
- Windows `.cmd` launcher handling;
- timeout, nonzero-exit, missing-output, and schema-failure handling;
- zero automatic retries;
- available model, response identifier, token, latency, and retry metadata;
- local JSONL event log and credential-safe smoke report;
- simulated CI tests that never invoke Codex.

## Local Smoke Command

Prerequisites:

```powershell
codex --version
codex
```

Use the second command once to sign in with ChatGPT if necessary, then exit Codex.

Run exactly one live Accountant interpretation:

```powershell
python -m imperium.live smoke `
  --output-dir stage5-output\smoke
```

Optional explicit model:

```powershell
python -m imperium.live smoke `
  --model <codex-model> `
  --output-dir stage5-output\smoke
```

Review:

- `stage5-output/smoke/smoke-report.json`
- `stage5-output/smoke/events/stage5-smoke_interpretation_steward.jsonl`

## Gate 1 Success Criteria

- Codex runs non-interactively under the existing ChatGPT sign-in.
- The process exits without an approval prompt.
- The final artifact validates as `Interpretation`.
- The output retains `member_id=steward`.
- The run uses no repository workspace or inherited council transcript.
- Available usage and duration are recorded.
- No retry occurs.

## Gate 1 Stop Conditions

Stop before a complete live deliberation if:

- authentication cannot be used non-interactively;
- structured output fails;
- the CLI requires write access or inherited repository context;
- timeout and failure state cannot be bounded;
- one accepted result cannot later be replayed;
- usage is too opaque to estimate a full run.

## Remaining Before the First Live Council

- [ ] Pass repository CI for the provider smoke implementation
- [ ] Run the one-call smoke locally
- [ ] Inspect the live Interpretation and metadata
- [ ] Confirm the result can be saved and replayed
- [ ] Refactor Stage 4 orchestration to accept an injected provider
- [ ] Freeze one bounded live strategic case and explicit model
- [ ] Run one complete live deliberation sequentially with no automatic retries
- [ ] Review transcript, profile fidelity, disagreement, usage, and minority objection

## Current Validation Risks

- Numeric profiles may not produce persistent live reasoning differences.
- The first live call may inherit unexpected Codex behavior despite an empty workspace.
- Codex JSONL may not expose complete token metadata on every installation or model.
- A live timeout or process failure is not safely equivalent to a replay interruption.
- Human Sustainability may remain underrepresented.
- The Seneschal may still bias synthesis.
- Full deliberation may not outperform simpler baselines.

These risks are now being tested in increasing order of cost rather than answered with additional architecture.
