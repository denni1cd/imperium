# Project Status

## Current Position

Imperium remains in **design and validation**.

- **Stages 0–4:** complete and merged.
- **Stage 4 merge:** PR #8, squash commit `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- **Stage 5 Gate 1:** complete and merged through PR #12, squash commit `bd16c0a4dcbc4f7174743029611b950d233abfa7`.
- **Stage 5 Gate 2:** complete and merged through PR #13, squash commit `d816cc64cc88e28b7472e89bada680217704237f`.
- **Stage 5 Gate 2E.1:** complete and merged through PR #14, squash commit `a074d27b648d63ffbb602fbec57aa7961cbe9576`.
- **Stage 5 Gate 2E.2:** implemented in draft PR #15 under simulated providers; review is pending.
- **Live model policy:** all Stage 5 tests remain locked to `gpt-5.6-terra` with `low` reasoning effort.
- **Live tool policy:** shell execution and web search remain disabled.
- **Current gate:** review Gate 2E.2 operator abandon/single-replacement authorization before captured replay or any complete live council.

`MANIFESTO.md` remains the governing source of truth. `DECISIONS.md` records durable accepted decisions. `docs/STAGE_5_CODEX_PROVIDER_PLAN.md` defines the accepted Gate 1 boundary. `docs/STAGE_5_GATE_2_PROVIDER_INJECTION.md` defines accepted Gate 2. `docs/STAGE_5_GATE_2E_ATTEMPT_ACCOUNTING.md` defines the current Gate 2E safety contract.

## Stage Summary

| Stage | Status | Result |
|---|---|---|
| 0 — Governance and provider-neutral foundation | Complete and merged | Manifesto, decisions, domain contracts, lifecycle foundation, providers, persistence, CI |
| 1 — Shared strategic vocabulary | Complete and merged | Nine approved values and normalized vector validation |
| 2 — Profiles and fixed council | Complete and merged | Seneschal plus Accountant, Gazgul, Overmind, and Castellan with persistent profiles and counterweights |
| 3 — Exact deliberation protocol | Complete and merged | Protocol 1.3 with blind interpretation, direct debate, evidence ordering/cardinality, halt behavior, and bounded rounds |
| 4 — Offline deliberation engine | Complete and merged | Full replay orchestration, halt paths, checkpoints, resume, exports, CLI, and synthetic review artifacts |
| 5 — Codex provider and live slice | Gates 1, 2, and 2E.1 merged; Gate 2E.2 in draft | Terra-low provider proven; durable budgeted attempts and explicit one-replacement authorization pass simulated tests; captured replay remains |
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

## Stage 5 Gate 2 Accepted Result

Merged PR #13 proves under simulated providers that:

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

The merged Gate 2 implementation passed **146 Python tests** and the Stage 4 artifact workflow. CI and local validation made no live model calls.

The architecture review established:

1. `SharedDeliberationEngine` owns provider invocation, challenge routing, evidence resolution, resume, and the inherited single lifecycle. `OfflineDeliberationEngine` and `ProviderBoundDeliberationEngine` are thin authority adapters.
2. Route-control validation occurs inside the call acceptance boundary. Invalid plans and continuation decisions are not applied, traced, added to completed calls, or checkpointed as accepted.
3. Second-round eligibility accepts genuinely new claim IDs or an exact normalized canonical claim produced by an accepted prior-round `REFINE` response. Non-refine, wrong-phase, wrong-round, cosmetic, and unincorporated revisions do not qualify.

## Stage 5 Gate 2E.1 Result

Merged PR #14 proves under replay and simulated providers that:

- every provider launch has a pending attempt checkpoint before invocation;
- accepted, failed, and ambiguous outcomes remain distinct and inspectable;
- prompt, input, output, stage, member, provider, and model identity are bound across attempts, turns, and accepted artifacts;
- accepted artifact or attempt-metadata tampering fails checkpoint validation;
- cumulative attempt, input, cached-input, and output budgets fail closed;
- missing provider usage is charged conservatively rather than treated as zero;
- previously accepted attempts survive a later preflight failure;
- a second attempt requires explicit retry lineage;
- providers reporting an automatic retry are rejected.

The merged Gate 2E.1 head passed **162 Python tests** and the Stage 4 artifact workflow. CI made no Codex or live council calls.

## Stage 5 Gate 2E.2 Result

Draft PR #15 proves under replay and simulated providers that:

- an operator can abandon one unresolved first attempt without launching a provider;
- one replacement requires an explicit non-empty reason;
- original and replacement attempts retain bidirectional durable lineage;
- ordinary resume cannot create a replacement;
- a second replacement remains prohibited;
- original and replacement usage remain cumulative;
- crash-pending attempts retain conservative output-reserve charges;
- model identity cannot change during replacement.

The clean draft head passes **170 Python tests** and the Stage 4 artifact workflow. CI made no Codex or live council calls.

## Remaining Before the First Live Council

Gate 2E still requires:

- accepted live artifacts saved as replay fixtures;
- complete captured-session replay without provider calls;
- reviewed full-session Terra-low usage estimate;
- explicit user authorization for one sequential complete live deliberation.

## Current Validation Risks

- Numeric profiles may not produce persistent live reasoning differences across a full session.
- Live context growth may make a complete session impractically expensive.
- Codex may omit or vary usage metadata; budgets therefore use conservative fallback charges.
- A timeout may consume tokens without returning exact usage.
- Human Sustainability may remain underrepresented.
- The Seneschal may bias synthesis.
- Full deliberation may not outperform simpler baselines.

These risks are being tested in increasing order of cost rather than answered with additional architecture.
