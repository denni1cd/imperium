# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Stages 0–4:** complete and merged.
- **Stage 4 merge:** PR #8, squash commit `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- **Stage 5 Gate 1:** complete and merged through PR #12, squash commit `bd16c0a4dcbc4f7174743029611b950d233abfa7`.
- **Stage 5 Gate 2:** draft PR #13 resolves the shared-engine architecture gate under simulated providers; final review remains before merge.
- **Live model policy:** all Stage 5 tests remain locked to `gpt-5.6-terra` with `low` reasoning effort.
- **Live tool policy:** shell execution and web search remain disabled.
- **Current gate:** review the consolidated Gate 2 implementation before Gate 2E live-failure accounting or any complete live council.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records durable accepted decisions. `docs/STAGE_5_CODEX_PROVIDER_PLAN.md` defines the accepted Gate 1 boundary. `docs/STAGE_5_GATE_2_PROVIDER_INJECTION.md` defines the current Gate 2 review state.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values and normalized vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct debate, evidence ordering/cardinality, halt behavior, and bounded rounds |
| 4 — Offline deliberation engine | Complete and merged | Full replay orchestration, halt paths, checkpoints, resume, exports, CLI, and synthetic review artifacts |
| 5 — Codex provider and live slice | Gate 1 merged; Gate 2 consolidated in draft | Terra-low provider proven; one shared replay/provider lifecycle passes simulated authority and precommit validation; live-safety accounting remains |
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

The locked local smoke completed on Codex CLI 0.144.4 using `gpt-5.6-terra` with `low` reasoning.

- input tokens: `10,939`;
- cached input tokens: `0`;
- output tokens: `470`;
- reasoning output tokens: `11`;
- latency: `11,597 ms`;
- retries: `0`;
- confidence: `0.94`.

The result was profile-faithful, schema-valid, isolated, and contained no shell, file, command, web-search, or other tool event.

## Stage 5 Gate 2 Behavioral Result

Draft PR #13 demonstrates under simulated providers that:

- one provider instance can serve the complete 36-turn session;
- replay remains the default;
- provider-returned challenge plans control whether exchanges occur;
- provider assignments control challenger and target routing;
- provider-authored challenge text reaches the target context;
- accepted responses reach the Seneschal continuation context;
- provider continuation decisions control whether another round occurs;
- the two-round protocol limit rejects a third round;
- provider-generated evidence requests require exact matching dispositions;
- clarification-required evidence halts and resumes by the accepted provider request ID;
- Stage 4 strict replay and artifact workflows remain unchanged.

The consolidated implementation passes **143 Python tests** and the Stage 4 artifact workflow. CI and local validation made no live model calls.

## Gate 2 Architecture Review Resolution

The three architecture blockers are resolved in the draft branch:

1. `SharedDeliberationEngine` owns provider invocation, challenge routing, evidence resolution, resume, and the inherited single lifecycle. `OfflineDeliberationEngine` and `ProviderBoundDeliberationEngine` are thin authority adapters.
2. Route-control validation is passed into the call acceptance boundary. Invalid plans and continuation decisions are not applied, traced, added to completed calls, or checkpointed as accepted.
3. Second-round eligibility recognizes genuinely new claim IDs and claims reached through accepted consequential revisions. Cosmetic object inequality is ignored.

## Required Consolidation Before Gate 2E

- [x] Extract complete replay scripts
- [x] Inject one session provider under simulation
- [x] Prove provider-returned routing authority
- [x] Enforce bounded rounds
- [x] Match and resume provider-generated evidence IDs
- [x] Preserve Stage 4 strict replay behavior
- [x] Move replay and provider execution onto one shared orchestration path
- [x] Validate route-control artifacts before commitment
- [x] Enforce material second-round input rather than cosmetic inequality
- [x] Reduce the provider-bound subclass to an authority adapter
- [x] Re-run adversarial provider-authority and Stage 4 parity tests

## Remaining Before the First Live Council

After consolidation, Gate 2E still requires:

- persistent pending input digests and attempt identities;
- explicit accepted, failed, ambiguous, abandoned, and retried attempt state;
- cumulative input, cached-input, output-token, and call-count budgets;
- accepted live artifacts saved as replay fixtures;
- complete captured-session replay without provider calls;
- reviewed full-session Terra-low usage estimate;
- explicit user authorization for one sequential complete live deliberation.

## Current Validation Risks

- Numeric profiles may not produce persistent live reasoning differences across a full session.
- Live context growth may make a complete session impractically expensive.
- A live timeout or process failure is not safely equivalent to replay interruption.
- Codex usage metadata may vary by turn.
- Human Sustainability may remain underrepresented.
- The Seneschal may bias synthesis.
- Full deliberation may not outperform simpler baselines.

These risks are being tested in increasing order of cost rather than answered with additional architecture.
