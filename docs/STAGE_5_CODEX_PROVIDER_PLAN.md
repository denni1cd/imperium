# Stage 5 Codex Provider Plan

## Status

**Gate 1 passed locally on 2026-07-14; Gate 2 provider injection is unlocked but not yet complete.**

Stage 4 is accepted and merged. Protocol 1.3, council 1.0, and the manifesto remain unchanged.

## Central Unproven Assumption

A fresh ChatGPT-authenticated `codex exec` process can receive only the explicit Imperium stage prompt and context and return one artifact satisfying the existing Pydantic contract without inherited repository or conversation state.

The smallest falsifiable test was one blind Accountant `Interpretation`, not a complete 36-call council session.

## Gate 1 — One Isolated Interpretation

The local command:

```powershell
python -m imperium.live smoke --output-dir stage5-output\smoke
```

performed exactly one Codex call and produced:

- a schema-valid `Interpretation`;
- `smoke-report.json` with provider, model label, response/thread ID, token counts, latency, retries, and validated output;
- a local JSONL event log.

The test used the approved Accountant profile and the Stage 4 independent-interpretation context builder.

### Accepted live evidence

- provider: `codex-cli`;
- model label emitted by the original default-config run: `codex-config-default`;
- member: `steward`;
- response/thread ID: `019f6198-7529-7c13-8917-67c5c9fba7bd`;
- input tokens: `13,006`;
- cached input tokens observed in JSONL: `2,432`;
- output tokens: `524`;
- latency: `40,875 ms`;
- retries: `0`;
- confidence: `0.86`.

The raw wire output encoded `value_influence` as unique key/value entries. The provider restored that representation to the approved dictionary field before Pydantic validation. The validated report matches the raw structured output after this reversible transformation.

The interpretation is substantively consistent with the Accountant profile: it prioritizes economy, simplicity, optionality, bounded commitment, hidden recurring burden, and a hard decision checkpoint. It does not treat one successful call as proof of the council hypothesis.

### Gate 1 limitations

- The original `codex-config-default` label did not identify the underlying configured model.
- The recorded `response_id` is currently the Codex thread ID because no more specific response identifier was emitted.
- One interpretation consumed 13,006 input tokens. A naive 36-call extrapolation would exceed 468,000 input tokens before accounting for larger later-stage contexts. The complete live session must remain blocked until Gate 2 measures and controls per-turn context.

## Live Model Safety Lock

All subsequent Stage 5 live tests are locked to:

- model: `gpt-5.6-terra`;
- reasoning effort: `low`, the Codex CLI equivalent of Light.

The user-facing live command exposes no model or reasoning override. The provider fails before resolving or launching the Codex executable when any other model or effort is requested.

This means Stage 5 will not run:

- GPT-5.6 Sol;
- GPT-5.6 Luna;
- another model family;
- minimal, medium, high, or xhigh reasoning effort.

A quality-based increase requires an explicit reviewed code change and user approval. No runtime flag may silently escalate capability or usage.

## Codex Process Boundary

Each call uses:

- one fresh non-interactive `codex exec` process;
- an empty temporary working directory;
- a read-only sandbox;
- no approval prompts;
- an ephemeral session;
- ignored repository rules and user configuration while preserving Codex authentication;
- explicit `gpt-5.6-terra` and `model_reasoning_effort="low"` overrides;
- shell tool disabled through `features.shell_tool=false`;
- web search disabled through `web_search="disabled"`;
- prompt input through stdin;
- a strict output schema;
- final output written to a temporary file;
- no automatic retries.

Tool prohibition is enforced by command configuration rather than relying only on prompt instructions.

## Structured Output Compatibility

Pydantic JSON Schema is not passed directly to Codex.

OpenAI Structured Outputs supports only a subset of JSON Schema, requires every object field to be listed as required, and requires `additionalProperties: false`. Arbitrary-key dictionaries cannot satisfy that contract directly.

The provider applies a reversible wire-schema adapter:

- unsupported Pydantic annotations such as `title`, `default`, `minLength`, `propertyNames`, and generated `pattern` expressions are removed;
- every object property is required;
- every object rejects additional properties;
- dynamic dictionaries are represented on the wire as arrays of unique `{key, value}` objects;
- wire arrays are restored to dictionaries before the original Pydantic domain model validates the artifact;
- duplicate map keys or malformed entries fail closed;
- final Pydantic validation remains authoritative for constraints removed from the wire schema.

The first two local attempts were preserved as evidence: Codex CLI 0.142.5 rejected `propertyNames`, then rejected Pydantic's Decimal regex lookaround. Both failures are covered by regression tests.

## Gate 1 Success Criteria

- [x] Codex authentication works through the installed CLI.
- [x] The command completes with exit code zero.
- [x] The output validates as `Interpretation` after reversible wire decoding.
- [x] `member_id` is `steward`.
- [x] The artifact contains substantive core decision, desired outcome, inclination, value influence, and calibrated confidence.
- [x] The event log and report expose enough provider metadata to estimate later usage.
- [x] No file, command, web-search, or unrelated repository context was needed by the model turn.

## Gate 2 — Provider Injection

Gate 2 is unlocked.

- Inject `ModelProvider` into the merged Stage 4 orchestration rather than creating a second engine.
- Keep replay as the default regression provider.
- Preserve one fresh process and isolated context per model turn.
- Preserve the Terra-low and no-tools safety lock for every live turn.
- Persist each accepted live artifact before the next call.
- Preserve failed and pending calls without silently retrying them.
- Save successful live artifacts as replay fixtures.
- Add per-turn token and context-size gates before authorizing a complete live session.
- Prove provider injection with simulated subprocesses only in CI.

## Gate 3 — One Complete Live Session

Unlocked only after provider injection and token/context controls pass simulated tests and are reviewed.

- Use one fixed synthetic strategic request.
- Use the existing fixed council.
- Execute the complete protocol once using Terra low only.
- Keep shell and web tools disabled for every call.
- Stop for user review after the exported transcript and plan.
- Do not add experiment conditions, repetitions, dynamic selection, model routing, or model escalation.

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
- allow shell-command execution;
- use API-key billing;
- add local-model or multi-model routing;
- use a non-Terra model or reasoning effort other than low during current tests;
- implement A1, A2, B, or C experiments;
- automate consequential actions;
- claim one successful live session proves strategic improvement.

## Current Validation

GitHub Actions uses simulated subprocesses only and never invokes Codex.

Coverage includes:

- all Stage 4 regression and integration paths;
- Codex command isolation and Windows launcher handling;
- explicit Terra model and low-reasoning command construction;
- explicit shell-tool and web-search disabling;
- rejection of non-Terra models and non-low reasoning effort before launch;
- output-schema adaptation and reversible dictionary decoding;
- the exact `propertyNames` and Decimal-regex regressions;
- duplicate map-key rejection;
- provider failure and invalid-output handling;
- smoke-report generation without a live call.
