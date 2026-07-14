# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Stages 0–4:** complete and merged.
- **Stage 4 merge:** PR #8, squash commit `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- **Stage 5:** draft PR #12 contains the successful Gate 1 Codex provider and one-call live smoke.
- **Live model policy:** all Stage 5 tests are locked to `gpt-5.6-terra` with `low` reasoning effort.
- **Live tool policy:** shell execution and web search are disabled for every current Stage 5 call.
- **Current gate:** complete the PR #12 review and locally verify the locked Terra-low command before merge or Gate 2 live use.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records accepted durable decisions. `docs/STAGE_5_CODEX_PROVIDER_PLAN.md` defines the current live-provider gates.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values and normalized vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct debate, evidence ordering/cardinality, halt behavior, and bounded rounds |
| 4 — Offline deliberation engine | Complete and merged | Full replay orchestration, halt paths, checkpoints, resume, exports, CLI, and synthetic review artifacts |
| 5 — Codex provider and live slice | Gate 1 passed; Gate 2 not implemented | Isolated Codex provider, live smoke evidence, Terra-low no-tools safety lock |
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

## Stage 5 Gate 1 Result

The central assumption was proven for one isolated call: a fresh ChatGPT-authenticated Codex CLI process received only an explicit Imperium prompt and Accountant context and returned a schema-valid domain artifact.

Accepted result:

- correct `steward` identity;
- profile-faithful economy, simplicity, optionality, burden, and bounded-commitment reasoning;
- 13,006 input tokens;
- 524 output tokens;
- 40,875 ms latency;
- zero retries;
- no observed file, shell, web-search, or unrelated-context events.

The usage level blocks a naive 36-call run until Gate 2 adds provider injection and context/token ceilings.

## Stage 5 Provider Boundary

The current branch implements:

- `CodexCliProvider` satisfying the existing provider protocol;
- one fresh `codex exec` process per call;
- explicit `gpt-5.6-terra` model selection;
- explicit `model_reasoning_effort="low"` override;
- rejection of every other model and reasoning effort before process launch;
- explicit `features.shell_tool=false`;
- explicit `web_search="disabled"`;
- empty temporary workspace;
- read-only sandbox;
- ephemeral session;
- ignored project rules and user configuration while preserving Codex authentication;
- OpenAI-compatible structured output;
- prompt delivery through stdin;
- Windows `.cmd` launcher handling;
- timeout, nonzero-exit, missing-output, and schema-failure handling;
- zero automatic retries;
- provider, thread/response identifier, token, latency, and retry metadata;
- local JSONL event log and smoke report including configured reasoning effort;
- simulated CI tests that never invoke Codex.

## Structured Outputs Corrections

The first local attempts reached Codex but exposed unsupported Pydantic schema constructs: `propertyNames` and Decimal regex lookaround.

The reversible adapter:

- removes unsupported annotations and generated patterns;
- requires every object field;
- sets `additionalProperties: false`;
- represents arbitrary dictionaries as unique key/value entry arrays;
- restores entries before original Pydantic validation;
- rejects malformed entries, duplicate keys, and domain-invalid output.

Every artifact type planned for a live council now has a schema-subset regression test.

## Terra Light and No-Tools Safety Policy

All current Stage 5 tests use:

- model: `gpt-5.6-terra`;
- CLI reasoning effort: `low`;
- shell tool: disabled;
- web search: disabled.

The live CLI exposes no override. Any model, effort, or tool escalation requires explicit user approval and a reviewed code change.

## Local Smoke Command

```powershell
python -m imperium.live smoke --output-dir stage5-output\smoke
```

The command explicitly launches Terra with low reasoning and does not inherit a higher local model default. One local run is still required to confirm the installed Codex CLI accepts the newly locked command options.

## Remaining Before the First Live Council

- [x] Pass repository CI for the provider smoke implementation
- [x] Preserve and diagnose structured-output failures
- [x] Add reversible schema adaptation and regression coverage
- [x] Complete and review one valid live Accountant interpretation
- [x] Lock all live tests to Terra low
- [x] Disable shell execution and web search
- [x] Validate every planned live artifact schema through the adapter
- [ ] Run one local smoke with the locked Terra-low no-tools command
- [ ] Inject `ModelProvider` into Stage 4 orchestration
- [ ] Preserve replay as the default provider
- [ ] Add per-turn context and token ceilings, including cached-token accounting
- [ ] Add explicit live failed/pending/retry state
- [ ] Save accepted live artifacts as replay fixtures
- [ ] Pass Gate 2 simulated tests
- [ ] Review estimated full-session usage
- [ ] Authorize one sequential complete live deliberation

## Current Validation Risks

- Numeric profiles may not produce persistent live reasoning differences.
- The installed Codex CLI has not yet executed the explicit Terra-low no-tools command.
- Codex JSONL may not expose complete token metadata on every turn.
- A live timeout or process failure is not safely equivalent to replay interruption.
- Live context growth may make a complete session impractically expensive.
- Human Sustainability may remain underrepresented.
- The Seneschal may still bias synthesis.
- Full deliberation may not outperform simpler baselines.

These risks are being tested in increasing order of cost rather than answered with additional architecture.
