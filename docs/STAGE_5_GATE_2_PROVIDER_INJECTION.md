# Stage 5 Gate 2 — Provider Injection and Artifact Authority

## Status

**Replay extraction and session-level provider injection are complete and green. Provider-authoritative routing is next.**

Gate 1 was squash-merged as `bd16c0a4dcbc4f7174743029611b950d233abfa7` after a successful locked Terra-low local smoke. Gate 2 does not authorize a complete live council.

## Central Finding

The Stage 4 engine is provider-neutral at the schema and call interface, but it is not yet provider-authoritative throughout orchestration.

`OfflineDeliberationEngine._call()` invokes a replay provider and commits the returned artifact. However, several later decisions still read the corresponding `OfflineScenario` fixture object rather than the committed provider output. The important examples are:

- challenge-plan validation and assignment iteration;
- challenger and target identities;
- the challenge artifact exposed to the target response;
- challenge and response cardinality validation;
- continuation validation and whether another round executes;
- evidence-request discovery through scripted round contents.

A simple provider substitution would therefore be unsafe. It could display live-generated artifacts while silently routing the debate according to scripted fixture decisions.

## Gate 2 Governing Rule

> Once a provider artifact validates and is committed, that artifact is the sole authority for every downstream context, validation, routing decision, and lifecycle transition.

Fixtures may populate `ReplayProvider` records. They may not independently control orchestration after provider execution begins.

This is required by the manifesto's inspectability, consequential-debate, controlled-information-sharing, and genuine-cognitive-diversity rules.

## Slice 1 — Extract Replay Control — Complete

Every scripted provider result is now represented in one explicit replay record set:

- stable call keys are preserved;
- the challenged fixture produces 36 records;
- the empty fixture produces its exact abbreviated record set;
- evidence resolutions remain outside the provider script because they are protocol dispositions, not model turns;
- duplicate call keys fail closed;
- tests compare the extracted ordered keys with the current engine's completed call keys.

This established the parity baseline required to remove per-call fixture construction safely.

## Slice 2A — Inject One Session Provider — Complete

`ProviderBoundDeliberationEngine` now:

- constructs one complete `ReplayProvider` at session start when no provider is supplied;
- accepts one injected `ModelProvider` for simulated Gate 2 tests;
- routes every model turn through that same provider instance;
- preserves replay as the default behavior;
- exposes no live full-session CLI command;
- enforces a serialized-context byte ceiling before provider invocation;
- preserves prompt hashes, context hashes, call keys, checkpoints, turns, and exports.

Acceptance evidence:

- the default provider-bound challenged run makes exactly 36 calls through one `ReplayProvider`;
- an injected simulated provider handles all 36 calls through one instance;
- the provider-bound run matches the original engine across the complete deterministic record, protocol trace, lifecycle history, completed call keys, evidence history, lineage, and turn traces;
- the context ceiling fails before a provider is invoked;
- the full Python suite and Stage 4 artifact workflow remain green.

This slice proves the provider seam only. It does not make live debate safe because fixture-driven routing still exists.

## Required Refactor Sequence

### Slice 2B — Make Returned Artifacts Authoritative — Next

- Replace fixture plan usage with the committed/generated `ChallengePlan`.
- Iterate assignments from that returned plan.
- Resolve target source artifacts from the session record.
- Use the returned `ChallengeArtifact` in the target context.
- Validate returned challenges and responses, not fixture equivalents.
- Use returned `ContinuationDecision` to stop or continue.
- Use committed claim registers for every later challenge decision.

Success criterion: a simulated provider may change a valid challenge assignment or return an empty plan, and all downstream routing follows that result without reading a competing fixture decision.

### Slice 2C — Bound Dynamic Rounds

- Keep the protocol maximum of two rounds per challenge phase.
- Require a valid continuation decision after each round.
- Permit a second round only for the protocol-approved material conditions.
- Fail if a provider requests a third round.
- Preserve anti-repetition and new-input requirements.

Success criterion: simulated continue, stop, empty, and invalid-third-round paths all fail or advance exactly as protocol 1.3 requires.

### Slice 2D — Resolve Evidence Without Fixture Authority

- Introduce a narrow evidence-disposition input boundary.
- Match resolutions to provider-generated evidence request IDs.
- Preserve gathered, user-clarification, conditional, and paused outcomes.
- Never invent evidence or silently map a new request to an unrelated fixture resolution.

Success criterion: provider-generated evidence requests halt or resume through explicit matching resolutions.

### Slice 2E — Add Live Call Accounting and Failure State

- Persist pending input digest and attempt identity before each call.
- Persist accepted artifact and provider metadata atomically.
- Preserve ambiguous failures without automatic retry.
- Record explicit abandoned and retried attempts separately.
- Add cumulative input, cached-input, and output usage budgets.
- Stop before launching a call that would exceed the configured context or call-count limit.

Success criterion: simulated timeout, invalid output, budget exhaustion, accepted resume, and explicit retry are inspectable and cannot duplicate an accepted turn.

## Terra Light Safety Boundary

Every Stage 5 live call remains locked to:

- `gpt-5.6-terra`;
- reasoning effort `low`;
- shell tool disabled;
- web search disabled;
- empty temporary workspace;
- read-only sandbox;
- no automatic retries.

Gate 2 must not add runtime model selection or escalation.

## Gate 3 Unlock Conditions

One complete live council remains blocked until all of the following are true:

1. Replay parity remains green after provider injection.
2. Returned artifacts exclusively control downstream routing.
3. Dynamic debate rounds obey protocol limits.
4. Provider-generated evidence requests have explicit disposition behavior.
5. Pending, failed, accepted, and retried live attempts are inspectable.
6. Context and cumulative usage budgets are enforced before calls.
7. The complete simulated provider-injected session can be replayed without provider calls.
8. The estimated complete Terra-low session cost is reviewed by the user.
9. The user explicitly authorizes the one complete live run.

## Explicit Exclusions

Gate 2 does not:

- modify the manifesto, council, value matrices, or protocol;
- create a second deliberation lifecycle;
- add dynamic member selection;
- add mixed-model routing;
- run live Codex in CI;
- perform a complete live council;
- add network research or autonomous action;
- claim that provider injection proves strategic improvement.

## Stop Condition

Stop Gate 2 and return for design review if provider-authoritative routing cannot be achieved without duplicating the Stage 4 lifecycle or weakening protocol validation.
