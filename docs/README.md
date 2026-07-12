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
4. [`DELIBERATION_LIFECYCLE.md`](DELIBERATION_LIFECYCLE.md) — **approved:** twelve controlled transitions, information boundaries, evidence routing, and stopping rules.
5. [`CONSEQUENTIAL_DEBATE.md`](CONSEQUENTIAL_DEBATE.md) — **approved:** materiality, challenge quality, change records, and debate-effect measurement.
6. [`EXPERIMENT_PLAN.md`](EXPERIMENT_PLAN.md) — validation against direct advice, equivalent-budget self-critique, and independent perspectives; detailed cases and thresholds remain open.

## Approved Machine-Readable Configuration

- [`../config/values.yaml`](../config/values.yaml) — value vocabulary version 1.0
- [`../config/council.yaml`](../config/council.yaml) — member profiles and fixed roster version 1.0
- [`../config/protocol.yaml`](../config/protocol.yaml) — minimum deliberation protocol version 1.0
- [`../prompts/`](../prompts/) — stage-specific prompt contracts referenced by the protocol

The next implementation target is the Stage 4 offline vertical slice using fake and replay providers. No live provider is required until that workflow completes reliably.
