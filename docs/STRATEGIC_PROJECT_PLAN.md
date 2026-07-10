# Strategic Project Plan

## Purpose

This plan defines the sequence from the current design-and-validation stage to a first usable Imperium implementation.

The roadmap is intentionally gated. Work should advance only when the preceding phase has produced enough evidence and clarity to justify the next investment. The purpose is not to maximize code delivered; it is to reach a testable system that produces measurably better actionable plans.

## Target Outcome

The first usable implementation must be able to:

- accept and preserve a user's strategic request, goals, facts, and constraints;
- convene a fixed, user-approved council;
- obtain blind independent interpretations from selected members;
- compare frames and assign targeted challenges;
- resolve decision-critical evidence needs;
- produce independent strategies, debate them, and record justified revisions;
- support Seneschal adjudication without allowing pre-framing;
- generate a complete actionable plan;
- preserve an inspectable deliberation record;
- run the defined validation conditions using frozen configurations;
- report quality, actionability, debate effects, profile fidelity, and resource use.

A web interface, autonomous execution, dynamic council selection, and production-scale deployment are not required for this milestone.

## Operating Principles

- `MANIFESTO.md` remains the governing source of truth.
- Accepted design decisions must be recorded before they are encoded as permanent behavior.
- Supporting code may enforce accepted constraints but must not silently settle open design questions.
- Fake and replay providers should be used wherever a live model is unnecessary.
- The smallest complete vertical slice is preferred over broad partial implementation.
- Every phase must produce a reviewable artifact and an explicit exit decision.
- Failure to validate the council premise is a legitimate project result.

## Roadmap

### Phase 0 — Governance and Provider-Neutral Foundation

**Status:** In progress through draft PR #1.

**Objective:** Establish the constitutional documents and supporting code needed to develop the protocol without live-model expense.

**Deliverables:**

- governing manifesto and durable decision log;
- design documents for values, profiles, lifecycle, debate, council, and experiments;
- validated domain contracts;
- explicit lifecycle state machine;
- stage-specific information boundaries;
- fake and replay model providers;
- inspectable JSON records;
- automated tests and CI.

**Exit criteria:**

- the foundation passes automated tests;
- no unresolved strategic choice has been accidentally hard-coded;
- the implementation remains provider-neutral;
- the repository clearly separates accepted decisions from open questions.

**Decision:** Merge, revise, or reject the foundation.

---

### Phase 1 — Approve the Shared Strategic Value Vocabulary

**Objective:** Define the common dimensions that create persistent strategic differences among council members.

**Deliverables:**

- approved value names and precise definitions;
- high-weight and low-weight behavioral examples;
- known tensions between values;
- separation of weighted preferences from universal constraints;
- validation rules for normalized vectors;
- sample vectors used only to test the vocabulary.

**Exit criteria:**

- changing a value weight predictably changes attention, tradeoffs, sacrifice, evidence demands, or recommendations;
- values are distinct enough to avoid redundancy;
- the vocabulary is compact enough that every weight remains meaningful;
- the set works across several different strategic problem types.

**Implementation unlocked:** Configuration schemas and loaders for approved values.

---

### Phase 2 — Finalize Member Profiles and the Fixed Initial Council

**Objective:** Turn the approved values into a small set of persistent, distinguishable strategic perspectives.

**Deliverables:**

- approved minimum member profile contract;
- fixed, user-approved initial roster;
- normalized value vectors for each member;
- doctrines, jurisdictions, vigilance areas, accepted sacrifices, and revision triggers;
- a distinct procedural profile for the Seneschal;
- profile-fidelity test cases.

**Exit criteria:**

- profiles can be distinguished without names or theatrical tone;
- each member notices or evaluates at least one material dimension differently;
- members remain responsive to evidence rather than behaving as rigid caricatures;
- redundant members are removed or revised;
- the roster is small enough for controlled initial experiments.

**Implementation unlocked:** Versioned member configuration, profile snapshots, and profile validation.

---

### Phase 3 — Freeze the Minimum Deliberation Protocol

**Objective:** Convert the lifecycle design into exact stage contracts and operational rules.

**Deliverables:**

- exact input and output contract for every stage;
- frame and claim normalization method;
- challenge-selection and assignment rules;
- evidence-resolution behavior;
- operational stopping rules;
- actionable-plan output contract;
- stage-specific prompt contracts;
- required deliberation-record fields;
- rules for abbreviated handling of simple decisions.

**Exit criteria:**

- every stage has explicit prerequisites, inputs, outputs, and allowed information;
- evidence requests always terminate in an allowed outcome;
- challenges target decision-relevant claims rather than general disagreement;
- stopping rules prevent both premature closure and repetitive debate;
- the full protocol can be simulated deterministically with fake responses.

**Implementation unlocked:** Full offline orchestration and stage runners.

---

### Phase 4 — Complete the Offline Deliberation Engine

**Objective:** Implement the entire protocol without requiring Codex or API calls.

**Deliverables:**

- configuration loaders for values, members, and prompts;
- stage runners connected through the lifecycle engine;
- context construction and information-boundary enforcement;
- frame and claim registries;
- challenge assignment;
- evidence-resolution routing;
- stopping-rule evaluation;
- revision and minority-objection tracking;
- adjudication and actionable-plan validation;
- complete fake-provider vertical tests;
- replay fixtures for realistic model outputs.

**Exit criteria:**

- a complete deliberation can run from request to actionable plan using fake or replayed outputs;
- invalid transitions and information leaks are rejected;
- interrupted sessions can be inspected and resumed safely;
- the resulting record explains what changed, why it changed, and how the final plan was produced;
- normal development and regression testing require no live-model usage.

**Implementation unlocked:** Live provider integration.

---

### Phase 5 — Add the Codex Provider and Run a Live Vertical Slice

**Objective:** Use existing ChatGPT-authenticated Codex access for the first live deliberations without committing to API expense.

**Deliverables:**

- isolated `CodexCliProvider` implementation;
- ephemeral, non-interactive calls with structured output validation;
- read-only or empty temporary working directories;
- no inherited council transcript or unrelated repository context;
- model-call, token, duration, retry, and failure records;
- one complete live deliberation using the fixed council;
- saved outputs suitable for replay tests.

**Exit criteria:**

- every live stage satisfies its structured contract;
- blind interpretation remains isolated in practice;
- one request completes from intake to actionable plan;
- failures are preserved and resumable rather than silently retried into a different decision state;
- the live record can be replayed without another model call;
- usage is visible enough to estimate the cost of larger experiments.

**Decision:** Continue with Codex, revise the provider, add a local provider, or introduce a project-scoped API provider.

---

### Phase 6 — Implement the Controlled Experiment Harness

**Objective:** Make the central hypothesis testable rather than relying on impressive anecdotes.

**Deliverables:**

- condition A1: direct single adviser;
- condition A2: equivalent-budget single adviser with structured self-critique;
- condition B: independent value-profiled advisers without debate;
- condition C: full Imperium deliberation;
- frozen case, prompt, profile, model, tool, and output configurations;
- repeat-run support;
- blinded output packages;
- quality, actionability, profile-fidelity, debate-effect, and efficiency metrics;
- complete experiment artifact preservation.

**Exit criteria:**

- all conditions can run from the same case definition;
- B and C use the same council profiles;
- A2 receives a reasonably comparable reasoning opportunity;
- evaluators cannot identify the generating condition from presentation artifacts;
- experiment configuration is frozen before result inspection.

**Implementation unlocked:** Pilot validation.

---

### Phase 7 — Run the Pilot Validation

**Objective:** Determine whether the minimum protocol is promising enough to justify further implementation.

**Deliverables:**

- a small, precommitted set of representative strategic cases;
- repeated runs under all experimental conditions;
- blinded human scoring and ranking;
- profile-fidelity results;
- token and call measurements;
- failure analysis;
- documented protocol revisions or preserved objections.

**Exit criteria:**

- results are repeatable enough to distinguish signal from isolated strong outputs;
- condition C is compared honestly against A1, A2, and B;
- changes caused by debate are evaluated for benefit, not merely counted;
- serious failure cases are understood;
- the evidence supports one of three explicit decisions: proceed, revise and retest, or stop.

---

### Phase 8 — Implementation Decision Gate

**Objective:** Decide whether Imperium has earned further engineering investment.

**Proceed when:**

- full deliberation shows a repeatable and material advantage in actionable strategic output;
- the advantage is not explained only by greater inference budget;
- member profiles are persistent and genuinely distinct;
- consequential debate produces justified improvements often enough to warrant its cost;
- no constitutional flaw requires redesign of the core protocol.

**Revise and retest when:**

- diversity helps but debate does not;
- insight improves while actionability declines;
- profiles are inconsistent or redundant;
- stopping, challenge assignment, or adjudication creates avoidable waste;
- results are promising but too variable.

**Stop or fundamentally reconsider when:**

- the single-adviser baselines match or outperform Imperium;
- debate reliably adds ceremony rather than decision value;
- persistent profiles cannot be made distinguishable without roleplay;
- the system cannot justify its additional cost and complexity.

---

### Phase 9 — Deliver the First Usable Implementation

**Objective:** Package the validated protocol into a reliable local tool for real strategic use.

**Required scope:**

- command-line workflow for starting, inspecting, resuming, and exporting sessions;
- versioned configuration for values, members, prompts, and provider settings;
- Codex provider and at least one replaceable alternative when justified;
- durable local persistence;
- human checkpoints for missing information and consequential authorization;
- actionable-plan and full-record exports;
- usage reporting and stage-boundary budget controls;
- regression tests using fake and replay providers;
- operator documentation and worked examples.

**Exit criteria:**

- a user can run a deliberation without editing source code;
- the system exposes rather than hides uncertainty, assumptions, minority objections, and resource use;
- failures do not corrupt the session record;
- provider replacement does not require changes to the deliberation engine;
- the tool remains subordinate to strategic judgment rather than autonomous execution.

## Deferred Work

The following should remain outside the critical path unless evidence demonstrates they are necessary:

- web or mobile interface;
- microservices or distributed queues;
- vector databases;
- dynamic autonomous council selection;
- unrestricted shared-agent chat;
- MCP services;
- production cloud deployment;
- autonomous action execution;
- large council registries;
- mixed-model optimization.

## Immediate Next Actions

1. Review and squash-merge the provider-neutral foundation when satisfied.
2. Complete and approve the shared strategic value vocabulary.
3. Finalize the member profile contract and fixed initial council.
4. Freeze the minimum lifecycle contracts, challenge rules, and stopping rules.
5. Extend the current Python foundation into a complete fake-provider vertical slice.
6. Add Codex only after the offline protocol can complete without it.

## Progress Rule

A phase is complete only when its exit criteria are met and the accepted decision is recorded. Starting later work early is acceptable only when it does not prejudge unresolved design decisions or create architecture that depends on an unvalidated assumption.
