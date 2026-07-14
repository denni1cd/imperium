# Stage 5 Codex Provider Plan

## Status

**Gate 1 implemented in draft PR #12; one successful local live call is still required before full provider injection.**

Stage 4 is accepted and merged. Protocol 1.3, council 1.0, and the manifesto remain unchanged.

## Central Unproven Assumption

A fresh ChatGPT-authenticated `codex exec` process can receive only the explicit Imperium stage prompt and context and return one artifact satisfying the existing Pydantic contract without inherited repository or conversation state.

The smallest falsifiable test is one blind Accountant `Interpretation`, not a complete 36-call council session.

## Gate 1 — One Isolated Interpretation

The local command:

```powershell
python -m imperium.live smoke --output-dir stage5-output\smoke
```

must perform exactly one Codex call and produce:

- a schema-valid `Interpretation`;
- `smoke-report.json` with provider, model, response ID when available, token counts when available, latency, retries, and the validated artifact;
- a local JSONL event log for inspection.

The test uses the approved Accountant profile and the Stage 4 independent-interpretation context builder.

## Codex Process Boundary

Each call must use:

- one fresh non-interactive `codex exec` process;
- an empty temporary working directory;
- a read-only sandbox;
- no approval prompts;
- an ephemeral session;
- ignored repository rules and user configuration while preserving Codex authentication;
- prompt input through stdin;
- a strict output schema;
- final output written to a temporary file;
- no automatic retries.

## Structured Output Compatibility

Pydantic JSON Schema is not passed directly to Codex.

OpenAI Structured Outputs supports only a subset of JSON Schema, requires every object field to be listed as required, and requires `additionalProperties: false`. Arbitrary-key dictionaries cannot satisfy that contract directly.

The provider therefore applies a reversible wire-schema adapter:

- unsupported Pydantic annotations such as `title`, `default`, `minLength`, and `propertyNames` are removed;
- every object property is required;
- every object rejects additional properties;
- dynamic dictionaries are represented on the wire as arrays of unique `{key, value}` objects;
- wire arrays are restored to dictionaries before the original Pydantic domain model validates the artifact;
- duplicate map keys or malformed entries fail closed.

This correction was triggered by the first local Gate 1 failure on Codex CLI 0.142.5, which rejected `propertyNames` in `Interpretation.value_influence`.

## Gate 1 Success Criteria

- Codex authentication works through the installed CLI.
- The command completes with exit code zero.
- The output validates as `Interpretation` after reversible wire decoding.
- `member_id` is `steward`.
- The artifact contains substantive core decision, desired outcome, inclination, value influence, and calibrated confidence.
- The event log and report expose enough provider metadata to estimate later usage.
- No file, command, network, or unrelated repository context is needed by the model turn.

## Stop Conditions

Stop after the first call and do not retry automatically when:

- authentication fails;
- the CLI flags are unsupported;
- the schema is rejected;
- the model fails to return a final output file;
- wire decoding or Pydantic validation fails;
- the process times out;
- the returned member identity or stage context is wrong.

Any failure is preserved as evidence and corrected before another token-consuming call.

## Gate 2 — Provider Injection

Unlocked only after Gate 1 succeeds and its report is reviewed.

- Inject `ModelProvider` into the merged Stage 4 orchestration rather than creating a second engine.
- Keep replay as the default regression provider.
- Preserve one fresh process and isolated context per model turn.
- Persist each accepted live artifact before the next call.
- Preserve failed and pending calls without silently retrying them.
- Save successful live artifacts as replay fixtures.

## Gate 3 — One Complete Live Session

Unlocked only after provider injection passes simulated tests.

- Use one fixed synthetic strategic request.
- Use the existing fixed council.
- Execute the complete protocol once.
- Stop for user review after the exported transcript and plan.
- Do not add experiment conditions, repetitions, dynamic selection, or model routing.

## Live Resume Boundary

Stage 4 proves deterministic replay resume, not exactly-once live execution.

For Stage 5:

- a validated artifact durably committed to the session is never regenerated;
- an uncommitted failed or interrupted Codex call remains failed or pending;
- the engine does not automatically repeat an ambiguous live call;
- explicit operator authorization is required to abandon or retry it;
- the retry is recorded as a separate attempt.

## Explicit Exclusions

Stage 5 does not:

- modify the manifesto, council, value matrices, or protocol;
- perform network research;
- use API-key billing;
- add local-model or multi-model routing;
- implement A1, A2, B, or C experiments;
- automate consequential actions;
- claim one successful live session proves strategic improvement.

## Current Validation

GitHub Actions uses simulated subprocesses only and never invokes Codex.

The current branch passes **102 tests**, including:

- all Stage 4 regression and integration paths;
- Codex command isolation and Windows launcher handling;
- output-schema adaptation and reversible dictionary decoding;
- the exact `propertyNames` regression;
- duplicate map-key rejection;
- provider failure and invalid-output handling;
- smoke-report generation without a live call.
