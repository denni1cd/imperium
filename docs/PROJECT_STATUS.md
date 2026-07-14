# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Stages 0–4:** complete and merged.
- **Stage 4 merge:** PR #8, squash commit `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- **Stage 5:** draft PR #12 implements Gate 1, one isolated live Codex interpretation.
- **Validation:** 102 tests pass on the Stage 5 branch; GitHub Actions uses no live model calls.
- **Current gate:** rerun exactly one local smoke call after the structured-output schema correction.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted durable decisions. `docs/STAGE_5_CODEX_PROVIDER_PLAN.md` defines the current live-provider gate.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values and normalized vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct debate, evidence ordering/cardinality, halt behavior, and bounded rounds |
| 4 — Offline deliberation engine | Complete and merged | Full replay orchestration, halt paths, checkpoints, resume, exports, CLI, and synthetic review artifacts |
| 5 — Codex provider and live slice | Gate 1 under review in PR #12 | Isolated Codex provider and one-call live smoke command |
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
- OpenAI-compatible structured output;
- prompt delivery through stdin;
- Windows `.cmd` launcher handling;
- timeout, nonzero-exit, missing-output, and schema-failure handling;
- zero automatic retries;
- available model, response identifier, token, latency, and retry metadata;
- local JSONL event log and smoke report;
- simulated CI tests that never invoke Codex.

## First Live Failure and Correction

The first local call reached Codex successfully but Codex CLI 0.142.5 rejected Pydantic's generated `propertyNames` keyword inside `Interpretation.value_influence`.

The branch now uses a reversible Structured Outputs adapter:

- unsupported Pydantic annotations such as `title`, `default`, `minLength`, and `propertyNames` are removed;
- every object field is required;
- every object sets `additionalProperties: false`;
- arbitrary dictionaries are represented as arrays of unique key/value entries on the wire;
- wire entries are restored to dictionaries before the original Pydantic model validates them;
- malformed entries and duplicate keys fail closed.

The exact failure is covered by regression tests. No live call was made by CI.

## Local Smoke Command

Pull the corrected branch:

```powershell
git pull
python -m pip install -e ".[dev]"
pytest
```

Then run exactly one live Accountant interpretation:

```powershell
python -m imperium.live smoke --output-dir stage5-output\smoke
```

Review:

- `stage5-output/smoke/smoke-report.json`
- `stage5-output/smoke/events/stage5-smoke_interpretation_steward.jsonl`

## Gate 1 Success Criteria

- Codex runs non-interactively under the existing ChatGPT sign-in.
- The process exits without an approval prompt.
- The wire output restores and validates as `Interpretation`.
- The output retains `member_id=steward`.
- The run uses no repository workspace or inherited council transcript.
- Available usage and duration are recorded.
- No retry occurs.

## Gate 1 Stop Conditions

Stop before a complete live deliberation if:

- authentication cannot be used non-interactively;
- the corrected schema is rejected;
- wire decoding or domain validation fails;
- the CLI requires write access or inherited repository context;
- timeout and failure state cannot be bounded;
- one accepted result cannot later be replayed;
- usage is too opaque to estimate a full run.

## Remaining Before the First Live Council

- [x] Pass repository CI for the provider smoke implementation
- [x] Preserve and diagnose the first structured-output failure
- [x] Add reversible schema adaptation and exact regression coverage
- [ ] Pull the correction locally
- [ ] Run the one-call smoke locally
- [ ] Inspect the live Interpretation and metadata
- [ ] Confirm the result can be saved and replayed
- [ ] Inject the provider into Stage 4 orchestration
- [ ] Freeze one bounded live strategic case and explicit model
- [ ] Run one complete live deliberation sequentially with no automatic retries
- [ ] Review transcript, profile fidelity, disagreement, usage, and minority objection

## Current Validation Risks

- Numeric profiles may not produce persistent live reasoning differences.
- The first live call may reveal another unsupported schema construct.
- Codex JSONL may not expose complete token metadata on every installation or model.
- A live timeout or process failure is not safely equivalent to a replay interruption.
- Human Sustainability may remain underrepresented.
- The Seneschal may still bias synthesis.
- Full deliberation may not outperform simpler baselines.

These risks are being tested in increasing order of cost rather than answered with additional architecture.
