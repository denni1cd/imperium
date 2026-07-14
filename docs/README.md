# Design Documentation

These documents define the minimum viable deliberation protocol and the evidence required before Imperium earns further implementation.

## Governance and Status

- [`DECISIONS.md`](DECISIONS.md) — durable accepted decisions and authority boundaries
- [`PROJECT_STATUS.md`](PROJECT_STATUS.md) — concise stage status, built capabilities, risks, and next test checkpoint
- [`STRATEGIC_PROJECT_PLAN.md`](STRATEGIC_PROJECT_PLAN.md) — gated roadmap from design through validation to a first usable implementation

## Design Sequence

1. [`VALUE_VOCABULARY.md`](VALUE_VOCABULARY.md) — **approved:** nine strategic priorities, definitions, tensions, and validation rules.
2. [`COUNCIL_MEMBER_PROFILE.md`](COUNCIL_MEMBER_PROFILE.md) — **approved:** minimum profile contract, role boundaries, fidelity requirements, and change control.
3. [`INITIAL_COUNCIL.md`](INITIAL_COUNCIL.md) — **approved:** one non-advocating Seneschal and four fixed advocates.
4. [`DELIBERATION_LIFECYCLE.md`](DELIBERATION_LIFECYCLE.md) — **approved protocol 1.3:** twelve controlled transitions, advocate-authored challenge turns, conditional outputs, evidence routing and ordering, halt behavior, and stopping rules.
5. [`CONSEQUENTIAL_DEBATE.md`](CONSEQUENTIAL_DEBATE.md) — **approved protocol 1.3:** materiality, challenge quality, round ordering, change records, cardinality, minority preservation, and debate-effect measurement.
6. [`EXPERIMENT_PLAN.md`](EXPERIMENT_PLAN.md) — validation against direct advice, equivalent-budget self-critique, and independent perspectives; detailed cases and thresholds remain open.

## Implementation Contracts

- [`STAGE_4_IMPLEMENTATION_PLAN.md`](STAGE_4_IMPLEMENTATION_PLAN.md) — accepted and merged offline orchestration contract.
- [`STAGE_5_CODEX_PROVIDER_PLAN.md`](STAGE_5_CODEX_PROVIDER_PLAN.md) — sole current Stage 5 contract: bounded Codex CLI gates, Terra-low no-tools policy, structured-output compatibility, and live-run stop conditions.

## Protocol Amendments

- [`PROTOCOL_1_1_CHALLENGE_TURNS.md`](PROTOCOL_1_1_CHALLENGE_TURNS.md) — advocate-authored challenger and target-response subturns.
- [`PROTOCOL_1_2_CARDINALITY_AND_HALTS.md`](PROTOCOL_1_2_CARDINALITY_AND_HALTS.md) — conditional challenge outputs, evidence cardinality, halt semantics, and canonical challenge storage.
- [`PROTOCOL_1_3_EVIDENCE_ROUND_ORDERING.md`](PROTOCOL_1_3_EVIDENCE_ROUND_ORDERING.md) — evidence requests end the current challenge phase and cannot feed another round inside it.

## Approved Machine-Readable Configuration

- [`../config/values.yaml`](../config/values.yaml) — value vocabulary version 1.0
- [`../config/council.yaml`](../config/council.yaml) — member profiles and fixed roster version 1.0
- [`../config/protocol.yaml`](../config/protocol.yaml) — minimum deliberation protocol version 1.3
- [`../prompts/`](../prompts/) — stage-specific prompt contracts referenced by the protocol

The current engineering gate is one local verification of the locked Terra-low no-tools command, followed by provider injection under simulated tests. A complete live council remains blocked.
