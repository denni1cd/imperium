# Stage 5 Gate 2 — Provider Injection and Artifact Authority

## Status

**Provider-authority behavior is proven under simulated providers. Gate 2 is paused at an architecture review gate before merge or live call accounting.**

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

The latest head passes:

- **139 Python tests**;
- all six Stage 4 integration paths;
- the unchanged Stage 4 artifact workflow;
- provider-authority adversarial tests;
- provider-generated evidence halt and resume tests;
- the Terra-low provider safety and schema suite.

CI uses simulated providers only and never invokes Codex or consumes tokens.

## Architecture Review Blockers

The behavioral hypothesis is proven, but the current implementation must not merge unchanged.

### Blocker 1 — Duplicated orchestration surface

`ProviderBoundDeliberationEngine` is approximately 1,000 lines and copies or overrides substantial portions of `_call`, challenge orchestration, evidence resolution, and context assembly from the Stage 4 engine.

Although it inherits the lifecycle loop, this creates two large orchestration surfaces that can drift. That conflicts with the manifesto's preference for the simplest inspectable design and approaches the Gate 2 stop condition against duplicating the Stage 4 lifecycle.

**Required resolution:** move provider invocation, artifact authority, challenge routing, and evidence disposition into shared seams in the existing engine. Replay and live providers must use one orchestration implementation rather than parallel copies.

### Blocker 2 — Route-control artifacts are checkpointed before full protocol validation

The current provider-bound challenge loop calls `_call()` for a `ChallengePlan` and `ContinuationDecision`, which commits the artifact and writes its completed-call checkpoint. The caller then runs `validate_challenge_plan()` or `validate_continuation_decision()` afterward.

A schema-valid but protocol-invalid plan or continuation can therefore be durably recorded as a completed provider turn before the session fails. Resume would recover the invalid accepted artifact instead of permitting an explicit corrected attempt.

**Required resolution:** all context-dependent protocol validation for route-control artifacts must succeed before the artifact is committed as accepted or added to `completed_call_keys`.

### Blocker 3 — Second-round new input is too permissive

The current helper treats any changed claim object as new input. A cosmetic rewrite or non-material metadata change could therefore satisfy the anti-repetition gate.

Protocol 1.3 requires a materially revised claim, a genuinely new material claim/frame, or another explicitly permitted input—not merely inequality between serialized objects.

**Required resolution:** derive second-round eligibility from an accepted `ChallengeResponse.revised_claim`, a genuinely new claim ID, or another explicit protocol-approved input. Add adversarial tests proving cosmetic changes do not unlock a repeated challenge.

## Next Implementation Gate — Shared Engine Consolidation

The next change should be smaller than the current subclass, not additive:

1. Introduce one provider invocation seam in the existing engine.
2. Introduce one artifact-authority policy used by both replay and provider sessions.
3. Make route-control validation pre-commit.
4. Move provider-authoritative challenge routing into the shared challenge phase.
5. Preserve Stage 4 strict replay validation and exact accepted outputs.
6. Add the stricter second-round input test.
7. Delete or reduce the provider-bound subclass to configuration only.

Only after that consolidation is reviewed should Gate 2E begin.

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

## Stop Condition Applied

The Gate 2 stop condition is now active. Implementation pauses here because the behavior was achieved with enough duplicated orchestration and validation-order risk to require design review before further expansion.