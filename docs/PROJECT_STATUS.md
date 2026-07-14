# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Stages 0–4:** complete and merged.
- **Stage 4 merge:** PR #8, squash commit `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- **Stage 5:** draft PR #12 has completed Gate 1, the isolated live Codex provider test.
- **Live model policy:** all Stage 5 tests are locked to `gpt-5.6-terra` with `low` reasoning effort.
- **Live tool policy:** shell execution and web search are disabled.
- **Current gate:** implement Gate 2 provider injection and token/context controls before any complete live council run.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records durable accepted decisions. `docs/STAGE_5_CODEX_PROVIDER_PLAN.md` defines the current live-provider gates.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values and normalized vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct debate, evidence ordering/cardinality, halt behavior, and bounded rounds |
| 4 — Offline deliberation engine | Complete and merged | Full replay orchestration, halt paths, checkpoints, resume, exports, CLI, and synthetic review artifacts |
| 5 — Codex provider and live slice | Gate 1 complete; Gate 2 next | Terra-low no-tools provider proven locally; engine injection and usage controls remain |
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

Twelve ordered transitions, blind interpretation, advocate-authored challenge and response turns, evidence resolution after the originating challenge phase, reasoned revision or retention, minority-objection preservation, non-voting adjudication, and actionable-plan generation.

## Stage 4 Accepted Result

The merged replay engine proves process execution and inspectability: exact lifecycle execution, isolated interpretations, direct debate, evidence ordering, halt paths, atomic checkpoints, deterministic replay resume, minority-objection preservation, adjudication, and actionable-plan export.

It does not prove genuine live cognitive diversity or an advantage over a single adviser.

## Stage 5 Gate 1 Accepted Result

The locked local smoke completed successfully on Codex CLI 0.144.4.

- provider: `codex-cli`;
- model: `gpt-5.6-terra`;
- reasoning effort: `low`;
- member: `steward`;
- input tokens: `10,939`;
- cached input tokens: `0`;
- output tokens: `470`;
- reasoning output tokens: `11`;
- latency: `11,597 ms`;
- retries: `0`;
- confidence: `0.94`.

The report and raw wire output match after reversible decoding. The event log contains no shell, file, command, web-search, or other tool event.

The interpretation is profile-faithful: economy, simplicity, optionality, human sustainability, recurring burden, and bounded commitment materially affect the recommendation.

## Stage 5 Provider Boundary

The branch implements:

- one fresh `codex exec` process per call;
- explicit `gpt-5.6-terra` selection;
- explicit `model_reasoning_effort=low`;
- rejection of all other models and efforts before launch;
- explicit `features.shell_tool=false`;
- explicit `web_search=disabled`;
- empty temporary workspace and read-only sandbox;
- ephemeral session with ignored project rules and user configuration;
- strict structured output and reversible Pydantic schema adaptation;
- Windows `.cmd` launcher handling and bare enum overrides;
- timeout, nonzero-exit, missing-output, and schema-failure handling;
- zero automatic retries;
- provider, model, reasoning, thread, token, latency, and retry metadata;
- local JSONL event log and smoke report;
- simulated CI tests with no live model calls.

Every artifact type planned for a live council has a schema-subset regression test.

## Remaining Before the First Live Council

- [x] Pass provider smoke CI
- [x] Diagnose and cover structured-output failures
- [x] Complete one valid live Accountant interpretation
- [x] Lock tests to Terra low
- [x] Disable shell and web tools
- [x] Verify the locked command locally on Windows
- [x] Validate every planned live artifact schema
- [ ] Inject `ModelProvider` into Stage 4 orchestration
- [ ] Preserve replay as the default provider
- [ ] Add per-turn context ceilings and cumulative token budgets
- [ ] Track cached input tokens
- [ ] Add explicit live pending, failed, abandoned, and retry-attempt state
- [ ] Save accepted live artifacts as replay fixtures
- [ ] Pass Gate 2 simulated tests
- [ ] Review estimated complete-session usage
- [ ] Explicitly authorize one sequential complete live deliberation

## Current Validation Risks

- Numeric profiles may not produce persistent live reasoning differences across a full session.
- Live context growth may make a complete session impractically expensive.
- A live timeout or process failure is not safely equivalent to replay interruption.
- Codex usage metadata may vary by turn.
- Human Sustainability may remain underrepresented.
- The Seneschal may bias synthesis.
- Full deliberation may not outperform simpler baselines.

These risks are being tested in increasing order of cost rather than answered with additional architecture.