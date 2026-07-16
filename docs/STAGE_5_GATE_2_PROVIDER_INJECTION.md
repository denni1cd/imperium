# Stage 5 Gate 2 — Provider Injection and Artifact Authority

## Status

**Provider-authority behavior and shared-engine consolidation are proven under simulated providers. PR #13 remains draft pending final review and does not authorize live council execution.**

Gate 1 was squash-merged as `bd16c0a4dcbc4f7174743029611b950d233abfa7` after a successful locked Terra-low local smoke. PR #13 remains draft and unmerged. Gate 2 does not authorize a complete live council.

## Governing Rule

> Once a provider artifact validates and is committed, that artifact is the sole authority for every downstream context, validation, routing decision, and lifecycle transition.

Fixtures may populate `ReplayProvider` records and provide schema exemplars. They may not independently control orchestration after provider execution begins.

This rule is required by the manifesto's inspectability, consequential-debate, controlled-information-sharing, and genuine-cognitive-diversity requirements.

## Completed Behavioral Slices

### Slice 1 — Replay Extraction

Every scripted provider result is represented in one explicit replay record set:

- stable call keys are preserved;
- the challenged fixture produces 36 records;
- the empty fixture produces its exact abbreviated record set;
- evidence resolutions remain outside the provider script because they are protocol dispositions rather than model turns;
- duplicate keys and missing exchanges fail closed;
- extracted call order matches the accepted Stage 4 engine.

### Slice 2A — One Session Provider

The provider-bound implementation:

- constructs one `ReplayProvider` at session start when no provider is supplied;
- accepts one injected `ModelProvider` for simulated tests;
- routes every model turn through the same provider instance;
- preserves replay as the default;
- exposes no live full-session CLI command;
- enforces a serialized-context byte ceiling before provider invocation.

### Slice 2B — Provider-Authoritative Debate Routing

Simulated provider artifacts now control:

- the accepted `ChallengePlan`;
- assignment IDs and challenger/target routing;
- the challenge artifact exposed to the target;
- challenge and response validation;
- the continuation decision;
- whether a second round occurs;
- the artifacts visible to the Seneschal.

Adversarial tests prove that:

- a returned empty plan suppresses fixture exchanges;
- changed provider challenge text reaches the target context;
- accepted responses reach the Seneschal continuation context;
- a returned stop decision prevents the fixture's second round.

### Slice 2C — Bounded Dynamic Rounds

- Protocol 1.3's maximum of two rounds is enforced.
- A provider request for a third round is rejected.
- Every round requires an accepted continuation decision.
- Replay behavior and the Stage 4 artifact workflow remain green.

### Slice 2D — Provider-Generated Evidence

- Evidence resolutions match accepted provider-generated request IDs exactly.
- An unrelated fixture disposition cannot be silently substituted.
- Missing dispositions fail closed.
- Gathered dispositions continue the session.
- User-clarification dispositions halt the session.
- A halted provider-generated request resumes through an explicit replacement using the accepted request ID, without modifying the replay scenario.

## Validation Evidence

The consolidated head passes:

- **143 Python tests**;
- all six Stage 4 integration paths;
- the unchanged Stage 4 artifact workflow;
- provider-authority adversarial tests;
- provider-generated evidence halt and resume tests;
- the Terra-low provider safety and schema suite.

CI uses simulated providers only and never invokes Codex or consumes tokens.

## Architecture Review Resolution

The behavioral hypothesis now runs through one shared orchestration implementation.

### Blocker 1 — Resolved: shared orchestration

`SharedDeliberationEngine` owns the provider call seam, accepted-artifact recovery, challenge phase, evidence resolution, resume behavior, and inherited lifecycle. `OfflineDeliberationEngine` selects strict scenario authority; `ProviderBoundDeliberationEngine` selects provider authority. Both adapters are thin and execute the same control flow.

### Blocker 2 — Resolved: validation before commitment

`_call()` accepts a context-specific validation callback and executes it after schema and identity checks but before applying output. Adversarial plan and continuation tests verify that rejected output is absent from the authoritative record, turn trace, completed-call keys, and accepted checkpoint.

### Blocker 3 — Resolved: material new input

Second-round eligibility is derived from genuinely new claim IDs or target claim IDs associated with accepted responses carrying `revised_claim`. Changed wording, evidence ordering, regenerated registers, and other object inequality do not independently qualify.

## Next Implementation Gate — Gate 2E

Shared-engine consolidation is implemented and locally validated. Gate 2E remains separate and may begin only after review of this draft; it does not authorize a live council.

## Gate 2E — Not Started

Remaining live-safety work includes:

- persistent attempt identity and pending input digest;
- explicit accepted, failed, ambiguous, abandoned, and retried attempt state;
- no automatic retry of an ambiguous live call;
- cumulative input, cached-input, output-token, and call-count budgets;
- accepted live output capture as replay fixtures;
- replay of a complete captured session without provider calls;
- a complete Terra-low usage estimate.

## Terra Light Safety Boundary

Every future Stage 5 live call remains locked to:

- `gpt-5.6-terra`;
- reasoning effort `low`;
- shell disabled;
- web search disabled;
- empty temporary workspace;
- read-only sandbox;
- no automatic retries.

No runtime model selection or escalation is permitted.

## Gate 3 Unlock Conditions

One complete live council remains blocked until:

1. shared provider-neutral orchestration replaces the duplicated subclass logic;
2. route-control artifacts validate before commitment;
3. second-round new input obeys protocol 1.3 materially;
4. provider-generated evidence has explicit disposition behavior;
5. pending, failed, accepted, abandoned, and retried attempts are inspectable;
6. context, call-count, and cumulative usage budgets are enforced before calls;
7. a captured complete simulated session replays without provider calls;
8. the estimated Terra-low usage is reviewed by the user;
9. the user explicitly authorizes one complete live run.

## Explicit Exclusions

Gate 2 does not:

- modify the manifesto, council, value matrices, or protocol;
- add dynamic member selection or mixed-model routing;
- run live Codex in CI;
- perform a complete live council;
- add network research or autonomous action;
- claim that provider injection proves strategic improvement.

## Review Boundary Applied

The shared-engine, validation-order, and material-new-input blockers are resolved under simulated providers. Implementation pauses here for merge review; Gate 2E failure accounting, cumulative usage budgets, captured-session replay, and every complete live council remain blocked.
