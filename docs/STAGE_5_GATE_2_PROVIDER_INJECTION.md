# Stage 5 Gate 2 — Provider Injection and Artifact Authority

## Status

**Implementation started on a separate branch after Gate 1 merged.**

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

## First Slice — Extract Replay Control

The first implementation step extracts every scripted provider result into one explicit replay record set:

- stable call keys are preserved;
- the challenged fixture produces 36 records;
- the empty fixture produces its exact abbreviated record set;
- evidence resolutions remain outside the provider script because they are protocol dispositions, not model turns;
- duplicate call keys fail closed;
- tests compare the extracted ordered keys with the current engine's completed call keys.

This slice does not change runtime behavior. It establishes the parity baseline required to remove per-call fixture construction safely.

## Required Refactor Sequence

### Slice 2A — Inject one session provider

- Construct one `ReplayProvider` from the extracted script at session start.
- Pass a `ModelProvider` into the existing Stage 4 orchestration boundary.
- Keep replay as the default provider for the offline CLI and all current regressions.
- Do not expose a live full-session CLI command.
- Preserve prompt hashes, context hashes, call keys, checkpoints, turns, and exports.

Success criterion: all Stage 4 records and artifacts remain deterministically identical after removing per-call `ReplayProvider` construction.

### Slice 2B — Make returned artifacts authoritative

- Replace fixture plan usage with the committed/generated `ChallengePlan`.
- Iterate assignments from that returned plan.
- Resolve target source artifacts from the session record.
- Use the returned `ChallengeArtifact` in the target context.
- Validate returned challenges and responses, not fixture equivalents.
- Use returned `ContinuationDecision` to stop or continue.
- Use committed claim registers for every later challenge decision.

Success criterion: a simulated provider may change a valid challenge assignment or return an empty plan, and all downstream routing follows that result without reading a competing fixture decision.

### Slice 2C — Bound dynamic rounds

- Keep the protocol maximum of two rounds per challenge phase.
- Require a valid continuation decision after each round.
- Permit a second round only for the protocol-approved material conditions.
- Fail if a provider requests a third round.
- Preserve anti-repetition and new-input requirements.

Success criterion: simulated continue, stop, empty, and invalid-third-round paths all fail or advance exactly as protocol 1.3 requires.

### Slice 2D — Resolve evidence without fixture authority

- Introduce a narrow evidence-disposition input boundary.
- Match resolutions to provider-generated evidence request IDs.
- Preserve gathered, user-clarification, conditional, and paused outcomes.
- Never invent evidence or silently map a new request to an unrelated fixture resolution.

Success criterion: provider-generated evidence requests halt or resume through explicit matching resolutions.

### Slice 2E — Add live call accounting and failure state

- Persist pending input digest and attempt identity before each call.
- Persist accepted artifact and provider metadata atomically.
- Preserve ambiguous failures without automatic retry.
- Record explicit abandoned and retried attempts separately.
- Add per-turn serialized-context ceilings.
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
