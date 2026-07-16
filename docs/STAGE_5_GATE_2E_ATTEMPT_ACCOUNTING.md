# Stage 5 Gate 2E — Attempt Accounting and Usage Budgets

## Status

**Slice 2E.1 is merged. Slice 2E.2 is implemented in draft PR #15 under simulated providers and does not authorize a complete live council.**

Gate 2 was squash-merged as `d816cc64cc88e28b7472e89bada680217704237f`. Gate 2E.1 was squash-merged as `a074d27b648d63ffbb602fbec57aa7961cbe9576`. Gate 2E adds the safety state required before a full live deliberation can be considered.

## Central hypothesis

> Every provider launch can be represented by one durable attempt record before invocation, transitioned exactly once after invocation, and constrained by a persisted usage budget without altering the accepted deliberation lifecycle.

The hypothesis passed the current simulated gate.

## Slice 2E.1 completed result

The implementation adds:

- a stable attempt identity and contiguous attempt number per call key;
- a pending checkpoint containing prompt and input digests before provider launch;
- explicit `pending`, `accepted`, `failed`, and `ambiguous` terminal behavior;
- modeled `abandoned` and `retried` dispositions without yet authorizing either transition;
- exact provider, model, response, stage, member, and reported-usage metadata;
- cached-input token extraction and persistence;
- a persisted session usage budget that cannot be silently loosened on resume;
- an exact attempt-count gate before provider launch;
- a conservative cumulative estimated-input gate before provider launch;
- a reserved-output gate before provider launch;
- actual cumulative input, cached-input, and output checks after a provider returns;
- conservative charging when provider usage metadata is missing;
- accepted-output digests validated against authoritative checkpoint artifacts;
- attempt prompt/input digests and execution identity bound to the accepted turn trace;
- preservation of previously accepted attempts when a later preflight check fails;
- zero automatic retries.

## Attempt authority rules

1. A provider must not launch until its pending attempt has been atomically checkpointed.
2. A pending attempt contains the exact call key, stage, member identity, model, prompt digest, input digest, and conservative input estimate.
3. An accepted attempt requires a protocol-valid and committed output artifact.
4. A schema-valid but protocol-invalid output becomes a failed attempt and is not accepted into the deliberation record.
5. A timeout or another explicitly uncertain provider outcome becomes ambiguous.
6. A second attempt for the same call key requires explicit retry lineage from an earlier attempt marked `retried`.
7. Slice 2E.2 exposes two explicit operator operations: abandon without replacement, or authorize one replacement with a required reason.
8. A replacement is authorized only when the original is atomically marked `retried` and attempt 2 is checkpointed as `pending` with bidirectional lineage.
9. Failed and ambiguous attempts count against usage budgets because they may have consumed provider resources.
10. Accepted output content must continue matching its persisted digest when a checkpoint is loaded.
11. Accepted prompt, input, stage, member, provider, and model identity must continue matching the accepted turn trace.

## Budget semantics

The budget is persisted in the session and cannot be silently loosened during resume.

Before a call, the engine checks:

- maximum launched attempts;
- conservatively charged cumulative input plus the estimate for the next serialized prompt and context;
- conservatively charged cumulative output plus the configured reserve for the next attempt.

After a provider returns, the engine checks:

- reported input tokens or, when larger, the persisted conservative input estimate;
- reported cached-input tokens;
- reported output tokens or, when larger, the configured output reserve.

Missing usage metadata therefore cannot be treated as zero for hard-budget purposes. Reported usage remains preserved separately for later measurement and provider diagnostics.

A post-return breach records the failed attempt and its available usage/output identity but does not accept the output artifact. This cannot recover already-consumed tokens; it keeps the record honest and prevents further calls.

## Validation evidence

The merged Gate 2E.1 head passed **162 Python tests**. The current Gate 2E.2 draft head passes:

- **170 Python tests**;
- the Stage 4 offline artifact workflow;
- all Gate 2 provider-authority regressions;
- pending, accepted, failed, and ambiguous attempt tests;
- exact attempt-count, cumulative input, cached-input, and output-budget tests;
- missing-usage conservative-charge tests;
- accepted-artifact, prompt-digest, input-digest, and retry-lineage tamper tests;
- later-preflight preservation of earlier accepted attempts.

CI uses replay and simulated providers only. It does not invoke Codex or consume model tokens.

## Slice 2E.2 operator workflow

The operator may act only when exactly one unresolved first attempt is `pending`, `failed`, or `ambiguous`.

- `abandon_attempt` requires a non-empty reason, marks the attempt `abandoned`, clears pending identity, and launches no provider.
- `retry_attempt` requires a non-empty reason and the original model identity.
- Authorization is consumed when the original becomes `retried` and attempt 2 becomes `pending` in the same checkpoint.
- Attempt 2 identifies `retry_of_attempt_id`; attempt 1 identifies `superseded_by_attempt_id`.
- Ordinary resume remains inert for failed sessions and cannot create a replacement.
- A failed or ambiguous attempt 2 has no legal path to attempt 3.
- Every attempt remains charged to the same persisted cumulative budget.
- A crash-pending attempt consumes its conservative output reserve before attempt 2 can launch.

## Explicit exclusions

Slice 2E.2 does not:

- authorize automatic retry or more than one replacement;
- capture accepted live outputs as replay fixtures;
- replay a captured complete live session;
- expose a live full-session CLI;
- change the Terra-low, no-shell, no-web safety lock;
- authorize a complete live council.

## Next sub-gate

After PR #15 review, the next separate slice may capture accepted live outputs as replay fixtures and prove captured-session replay without provider calls. A reviewed full-session usage estimate and explicit user authorization remain required before any complete live council.
