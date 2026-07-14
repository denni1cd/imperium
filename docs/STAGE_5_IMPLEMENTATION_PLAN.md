# Stage 5 Implementation Plan

## Status

**Implementation started under a gated provider-smoke workflow.**

Stage 4 is merged and accepted. Stage 5 may replace replayed reasoning with live Codex output, but it may not change the manifesto, council 1.0, protocol 1.3, information boundaries, strategic artifacts, challenge rules, evidence ordering, or stopping behavior.

## Objective

Use the user's existing ChatGPT-authenticated Codex CLI access for the first live Imperium deliberation without introducing API billing, a second orchestration framework, or experiment infrastructure.

The central unproven assumption is:

> A fresh non-interactive Codex CLI process can receive one isolated Imperium context and prompt, return one schema-valid domain artifact, and expose enough execution metadata to preserve an inspectable call record.

Stage 5 begins by testing that assumption with one call. It does not begin with a full council run.

## Gate 1 — Single-Call Provider Smoke Test

Implement an isolated `CodexCliProvider` satisfying the existing `ModelProvider` protocol.

The smoke test uses:

- one fixed Accountant profile;
- one synthetic sovereign request;
- the approved independent-interpretation prompt;
- the real `Interpretation` Pydantic schema;
- one fresh empty temporary workspace;
- `codex exec` in non-interactive, ephemeral, read-only mode;
- no project repository as the Codex workspace;
- no inherited project rules or unrelated transcript;
- no automatic retry.

The provider writes the expected JSON Schema and final-response file into the temporary workspace, sends the complete prompt through stdin, validates the result against the requested Pydantic type, records latency and available usage metadata, and then removes the temporary workspace.

### Smoke success criteria

The gate passes only when a local authenticated run:

1. locates the Codex executable;
2. exits successfully without requesting interaction;
3. returns a final JSON object matching `Interpretation` exactly;
4. preserves the active member identity and request constraints;
5. runs in an empty read-only workspace;
6. records provider, model, response/session identifier when available, tokens when available, latency, and retry count;
7. writes a reviewable smoke report without exposing credentials or private Codex configuration.

### Smoke stop conditions

Stop before full deliberation if:

- Codex cannot run non-interactively under the user's ChatGPT authentication;
- structured output is unavailable or repeatedly invalid;
- the process requires repository access, writable workspace access, or inherited conversation state;
- the CLI cannot be bounded by timeout and explicit failure handling;
- a single call cannot be replayed from its saved accepted artifact;
- required metadata cannot be captured well enough to estimate the live run.

No hidden retry loop is permitted. A failed call remains a failed call and is preserved for inspection.

## Gate 2 — Provider-Neutral Engine Refactor

Only after Gate 1 passes locally:

- extract the Stage 4 orchestration from its hard-coded `ReplayProvider` construction;
- inject any `ModelProvider` through the same call boundary;
- keep replay fixtures as the default regression path;
- keep deterministic call keys, frozen prompts, complete profile projection, stage contexts, checkpoints, and exports unchanged;
- preserve accepted output artifacts so a completed live call can be replayed without another token-consuming invocation.

The refactor must not create a provider registry, plugin system, generalized workflow engine, or mixed-model router.

## Gate 3 — One Complete Live Vertical Slice

Run one complete live deliberation with:

- the fixed council: Accountant, Gazgul, Overmind, and Castellan;
- the non-advocating Seneschal;
- one frozen strategic request selected before result inspection;
- one explicit Codex model for every member and Seneschal call;
- protocol 1.3 unchanged;
- no web research or external tools;
- no automatic retries;
- one call at a time with a durable pending checkpoint before invocation;
- accepted outputs saved immediately and reusable through `ReplayProvider`.

The first live request should be bounded, non-medical, non-legal, non-financial, and answerable without current external facts. It should contain enough real tradeoffs to test persistent profile behavior and meaningful challenge.

### Live-slice success criteria

The live slice passes only when:

- all blind interpretations are isolated in practice;
- all structured artifacts validate;
- every direct challenge is authored by the assigned challenger and answered by the assigned target;
- the council produces material disagreement rather than four paraphrases;
- members revise or retain positions with explicit reasons;
- the Seneschal explains adjudication without voting or pre-framing;
- a serious minority objection remains visible;
- the actionable plan is complete;
- usage and duration are recorded per call and in aggregate;
- the full accepted live record can be replayed without additional Codex calls.

## Failure and Resume Semantics

A live Codex call is not assumed to be exactly-once or side-effect free.

For every call:

1. persist the pending call key and input digest;
2. invoke Codex in an empty read-only workspace;
3. validate the final artifact;
4. atomically persist the accepted artifact and call metadata;
5. never silently repeat a call after an ambiguous failure.

After timeout, process termination, or missing final output, the session becomes failed or paused for explicit operator review. Resume may accept a manually supplied artifact, explicitly rerun the failed call under a new attempt identifier, or abandon the session. It may not pretend the first invocation never happened.

## Token Discipline

Stage 5 does not impose an output-token cutoff that could truncate a valid structured artifact.

Instead it controls expense through:

- one-call smoke before orchestration work;
- exactly one live vertical slice before experiment infrastructure;
- one sequential call at a time;
- zero automatic retries;
- no duplicate calls after accepted output;
- frozen prompts and contexts;
- usage reporting after every call;
- explicit operator approval before a failed or ambiguous call is rerun.

## CI Boundary

GitHub Actions must never perform live Codex calls or require ChatGPT authentication.

CI covers:

- command construction;
- Windows `.cmd` launcher handling;
- temporary workspace isolation;
- schema generation and result parsing;
- timeout and nonzero-exit behavior;
- token and response-ID extraction from representative JSONL events;
- replay regression of saved live artifacts;
- the complete existing Stage 4 suite.

Live smoke and full deliberation remain explicit local commands.

## Deliverables

1. `CodexCliProvider` implementing `ModelProvider`.
2. Credential-safe local smoke command.
3. Unit tests using a simulated subprocess.
4. Reviewable smoke report format.
5. Provider injection into the Stage 4 orchestration after Gate 1.
6. One complete local live deliberation and replay package after Gate 2.
7. Updated project status and durable decision record.

## Explicit Exclusions

Stage 5 will not:

- modify the manifesto, council, values, or protocol;
- add API-key billing;
- use live Codex in CI;
- add dynamic council selection;
- add mixed models or model switching;
- implement A1, A2, B, or C experiment conditions;
- add web research, MCP services, autonomous execution, database infrastructure, or a UI;
- claim one successful live run proves Imperium outperforms a single adviser.

## Exit Decision

After the first live deliberation, choose one:

- continue with Codex into the controlled experiment harness;
- revise the provider or prompt boundary and repeat one bounded live slice;
- add a local or project-scoped alternative provider;
- stop live integration if structured isolation or resource use is unacceptable.
