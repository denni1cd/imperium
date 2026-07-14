# Stage 5 Codex Provider Plan

## Status

**Gate 1 passed locally on 2026-07-14. Gate 2 provider injection is unlocked but not yet implemented.**

Stage 4 is accepted and merged. Protocol 1.3, council 1.0, and the manifesto remain unchanged.

## Central Assumption Tested

A fresh ChatGPT-authenticated `codex exec` process can receive only the explicit Imperium stage prompt and context and return one artifact satisfying the existing Pydantic contract without inherited repository or conversation state.

The smallest falsifiable test was one blind Accountant `Interpretation`, not a complete council session.

## Gate 1 — Accepted Result

The local command:

```powershell
python -m imperium.live smoke --output-dir stage5-output\smoke
```

completed successfully on Codex CLI 0.144.4 with the final safety boundary enabled.

Accepted evidence:

- provider: `codex-cli`;
- model: `gpt-5.6-terra`;
- reasoning effort: `low`;
- member: `steward`;
- response/thread ID: `019f6223-5233-7003-af3b-eb78c19404ef`;
- input tokens: `10,939`;
- cached input tokens: `0`;
- output tokens: `470`;
- reasoning output tokens: `11`;
- latency: `11,597 ms`;
- retries: `0`;
- confidence: `0.94`.

The raw JSONL contains only thread start, turn start, one completed agent message, and turn completion. No file, shell, command, web-search, or other tool event occurred.

The raw wire output and persisted report match after the intended reversible transformations: map-entry arrays are restored to dictionaries and final Pydantic validation remains authoritative.

The interpretation is substantively consistent with the Accountant profile. Economy, simplicity, optionality, human sustainability, recurring burden, reversibility, and a bounded decision rule materially shaped the result.

## Live Model Safety Lock

All Stage 5 live tests are locked to:

- model: `gpt-5.6-terra`;
- reasoning effort: `low`, the CLI equivalent of Light;
- shell tool: disabled;
- web search: disabled.

The user-facing command exposes no model or reasoning override. The provider rejects every other model or effort before launching Codex.

A quality-based increase requires explicit user approval and a reviewed code change. No runtime flag may silently escalate capability, reasoning effort, or tool access.

## Codex Process Boundary

Each call uses:

- one fresh non-interactive `codex exec` process;
- an empty temporary working directory;
- a read-only sandbox;
- no approval prompts;
- an ephemeral session;
- ignored repository rules and user configuration while preserving authentication;
- explicit `gpt-5.6-terra` and `model_reasoning_effort=low` overrides;
- `features.shell_tool=false`;
- `web_search=disabled`;
- prompt input through stdin;
- strict structured output;
- final output written to a temporary file;
- no automatic retries.

Tool prohibition is enforced by command configuration rather than relying only on prompt instructions.

Codex enum overrides use bare `key=value` arguments. Quoted values are avoided because Windows `cmd.exe` can preserve quote characters and cause the CLI to reject otherwise valid enum values.

## Structured Output Compatibility

Pydantic JSON Schema is not passed directly to Codex.

The provider applies a reversible wire-schema adapter:

- unsupported Pydantic annotations and generated regex patterns are removed;
- every object property is required;
- every object rejects additional properties;
- dynamic dictionaries are represented as arrays of unique `{key, value}` entries;
- wire arrays are restored before original Pydantic validation;
- malformed entries and duplicate map keys fail closed;
- final domain validation remains authoritative.

Regression coverage includes every artifact type planned for a live council and the observed boundaries:

1. unsupported `propertyNames`;
2. unsupported Decimal regex lookaround;
3. Windows preservation of quoted enum values;
4. Codex CLI versions too old to resolve `gpt-5.6-terra`.

## Gate 1 Success Criteria

- [x] ChatGPT authentication works through the installed CLI.
- [x] The locked Terra-low no-tools command completes successfully.
- [x] The output validates as `Interpretation` after reversible wire decoding.
- [x] `member_id` remains `steward`.
- [x] The artifact contains substantive, value-influenced reasoning.
- [x] Usage, latency, retry count, model, reasoning effort, and thread identifier are recorded.
- [x] No repository context, file access, shell use, or web search is required.
- [x] No automatic retry occurs.

## Gate 2 — Provider Injection

Gate 2 is unlocked. Gate 3 remains blocked.

Required work:

- inject `ModelProvider` into the merged Stage 4 orchestration rather than creating a second engine;
- keep replay as the default regression provider;
- preserve one fresh process and isolated context per live turn;
- preserve the Terra-low no-tools safety lock;
- persist each accepted live artifact before the next call;
- preserve failed and pending calls without silently retrying them;
- record explicit retry attempts separately;
- save successful live artifacts as replay fixtures;
- add per-turn context ceilings and cumulative token budgets, including cached-token accounting;
- estimate complete-session usage before authorizing a full live run;
- prove all wiring with simulated providers in CI.

## Gate 3 — One Complete Live Session

Gate 3 unlocks only after Gate 2 is implemented, green, and reviewed.

The first complete live session will:

- use one fixed synthetic strategic request;
- use the existing fixed council;
- execute protocol 1.3 once;
- use Terra low only;
- disable shell and web tools;
- run sequentially with no automatic retries;
- stop for user review after transcript and plan export;
- avoid experiment repetitions, dynamic selection, model routing, and model escalation.

## Live Resume Boundary

Stage 4 proves deterministic replay resume, not exactly-once live execution.

For Stage 5:

- a validated artifact durably committed to the session is never regenerated;
- an uncommitted failed or interrupted call remains failed or pending;
- the engine never silently repeats an ambiguous live call;
- explicit operator authorization is required to abandon or retry it;
- every retry is recorded as a separate attempt.

## Explicit Exclusions

Stage 5 does not:

- modify the manifesto, council, values, or protocol;
- perform network research;
- use API-key billing;
- add local-model or multi-model routing;
- use Sol, Luna, medium, high, or xhigh for tests;
- implement the comparative experiment harness;
- automate consequential actions;
- claim one successful live call proves strategic improvement.

## Current Validation

GitHub Actions uses simulated subprocesses only and never invokes Codex.

The branch passes 124 tests covering Stage 4 regressions, Windows launching, Terra-low command construction, no-tools configuration, model and effort rejection, schema adaptation, every prospective live output schema, provider failure handling, and smoke-report persistence.