# Stage 5 Gate 2E — Attempt Accounting and Usage Budgets

## Status

**In implementation under simulated providers only. This gate does not authorize a complete live council.**

Gate 2 was squash-merged as `d816cc64cc88e28b7472e89bada680217704237f`. Gate 2E adds the safety state required before a full live deliberation can be considered.

## Central hypothesis

> Every provider launch can be represented by one durable attempt record before invocation, transitioned exactly once after invocation, and constrained by a persisted usage budget without altering the accepted deliberation lifecycle.

## Slice 2E.1 scope

This first slice adds:

- a stable attempt identity and attempt number per call key;
- a pending checkpoint containing prompt and input digests before provider launch;
- explicit `pending`, `accepted`, `failed`, and `ambiguous` terminal behavior;
- modeled `abandoned` and `retried` dispositions without yet authorizing either transition;
- exact provider/model/response and reported usage metadata;
- cached-input token tracking;
- a persisted session usage budget;
- an exact attempt-count gate before provider launch;
- a conservative estimated-input gate before provider launch;
- a reserved-output gate before provider launch;
- actual cumulative input, cached-input, and output checks after a provider returns;
- accepted-output digests validated against authoritative checkpoint artifacts;
- zero automatic retries.

## Attempt authority rules

1. A provider must not launch until its pending attempt has been atomically checkpointed.
2. A pending attempt contains the exact call key, stage, member identity, model, prompt digest, input digest, and conservative input estimate.
3. An accepted attempt requires a validated and committed output artifact.
4. A schema-valid but protocol-invalid output becomes a failed attempt and is not accepted into the deliberation record.
5. A timeout or another explicitly uncertain provider outcome becomes ambiguous.
6. A second attempt for the same call key requires a future explicit abandon-or-retry authorization workflow. This slice does not provide that workflow.
7. Failed and ambiguous attempts count against usage budgets because they may have consumed provider resources.
8. Accepted output content must continue matching its persisted digest when a checkpoint is loaded.

## Budget semantics

The budget is persisted in the session and cannot be silently loosened during resume.

Before a call, the engine checks:

- maximum launched attempts;
- cumulative reported input plus a conservative estimate for the next serialized prompt/context;
- cumulative output plus a configured per-attempt reserve.

After a provider returns, the engine checks actual reported:

- input tokens;
- cached input tokens;
- output tokens.

A post-return breach records the attempt and usage but does not accept the output artifact. This cannot recover already-consumed tokens; it ensures the record remains honest and prevents further calls.

## Explicit exclusions

Slice 2E.1 does not:

- authorize retrying an ambiguous or failed attempt;
- implement operator abandon/retry commands;
- capture accepted live outputs as replay fixtures;
- replay a captured complete live session;
- expose a live full-session CLI;
- change the Terra-low, no-shell, no-web safety lock;
- authorize a complete live council.

## Acceptance tests

The slice must prove:

- all 36 replay turns create accepted attempt records;
- pending state is readable before provider invocation;
- deterministic failures and ambiguous failures persist distinct states;
- call and estimated-input budgets stop before provider launch;
- reported token overruns are recorded without artifact acceptance;
- cached input tokens are persisted;
- accepted artifact tampering is rejected on checkpoint load;
- existing Stage 4 and Gate 2 behavior remains green;
- no automatic retry occurs.

## Next sub-gate

After this slice passes review, Gate 2E.2 may add an explicit operator workflow for abandoning an ambiguous attempt or authorizing one replacement attempt. That workflow must preserve both attempt records and must never retry automatically.
