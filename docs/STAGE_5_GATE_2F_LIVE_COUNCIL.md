# Stage 5 Gate 2F — Complete Live Council

## Status

**Implemented under replay and simulated providers. No complete live council has been run.**

Gate 2F is the authorization boundary for the first full condition-C deliberation. It is not another one-member smoke test and it does not ask the council to implement software. Four fixed advocates answer one frozen strategic question, debate material claims, revise their strategies, and the non-advocating Seneschal adjudicates one actionable council result.

## Central hypothesis

> The complete fixed council can preserve the sovereign request, produce four blind value-driven interpretations, conduct consequential member-to-member debate, revise strategies in response, and produce a reasoned actionable result that is more than a summary of initial answers.

This single run can falsify process and qualitative expectations. It cannot prove that Imperium outperforms the A1, A2, and B baselines; that requires the repeated blinded experiment defined in `docs/EXPERIMENT_PLAN.md`.

## Frozen strategic case

The council must decide whether a 20-person data engineering group should:

- build an internal AI coding and orchestration platform;
- adopt commercial tools;
- run a bounded hybrid pilot; or
- defer investment.

The decision targets at least a 20% reduction in median delivery lead time within six months while protecting confidential code and data, staying below $120,000 first-year incremental spend, keeping ongoing burden below 1.5 FTE, requiring human review, and prohibiting autonomous production deployment.

The supplied facts intentionally create legitimate tension among economy, urgency, leverage, resilience, adoption burden, and incomplete evidence. External research, shell access, repository inspection, and web access remain prohibited. Unknowns must become explicit assumptions, conditions, or evidence dispositions rather than invented facts.

The exact structured request lives in `src/imperium/live/gate_case.py` and is frozen before live results.

## Required deliberation

The accepted fixed roster remains:

1. Steward / Accountant — economy and opportunity cost;
2. Vanguard / Gazgul — urgency and credible commitment;
3. Architect / Overmind — leverage and reusable capability;
4. Castellan — resilience and reversibility;
5. Seneschal — coordination, adjudication, and plan synthesis only.

Protocol 1.3 runs without an abbreviated path:

1. four blind independent interpretations;
2. Seneschal frame comparison and claim normalization;
3. member-authored frame challenges and exact target responses;
4. explicit evidence disposition if requested;
5. four independent strategy proposals;
6. member-authored proposal challenges and exact target responses;
7. explicit evidence disposition if requested;
8. four reasoned revisions or justified retentions;
9. Seneschal adjudication with rejected alternatives and minority objections;
10. one actionable council plan.

## Gate criteria

Completion alone is a failure when the result contains no consequential debate.

Automated checks require:

- one interpretation, proposal, and revision from every fixed advocate;
- blind interpretation contexts containing only the request, supplied facts, and active profile;
- at least one member-authored challenge and matching target response;
- at least one refinement, concession, withdrawal, or decision-relevant evidence request;
- at least one post-debate revision signal through change, concession, evidence, or a changed proposal;
- Seneschal decisive reasons and rejected alternatives;
- an actionable plan with an immediate next action, ordered steps, and stop or reconsideration conditions;
- accepted-output capture and semantically exact full-session replay with no Codex provider.

Human review remains mandatory. It must determine whether the disagreement was genuinely distinct, whether the changes were material rather than cosmetic, whether the final strategy is stronger than simple aggregation, and whether the plan faithfully preserves intent, constraints, risks, objections, and revision triggers.

## Usage and attempt controls

The expected schema-exemplar path contains 36 sequential model calls. Protocol 1.3 permits up to 59 calls if both challenge phases use two rounds with the maximum four assignments. The replay-only estimate records expected serialized input and output reserve before authorization; live budgets remain the hard boundary.

`max_attempts_per_call` is a persisted configuration value exposed by the command. It defaults to 2 but is not fixed at 2. `max_attempts`, input, cached-input, output, and per-attempt output reserve are independently configurable. No provider may retry automatically; every replacement still requires explicit operator disposition and reason.

## Commands

Provider-free estimate:

```bash
python -m imperium.live council-estimate --output-dir artifacts/gate-2f-estimate
```

Full live council, only after reviewing the estimate and explicitly authorizing it:

```bash
python -m imperium.live council \
  --output-dir artifacts/gate-2f \
  --authorize RUN_FULL_COUNCIL \
  --max-attempts-per-call 3
```

The full command remains locked to `gpt-5.6-terra`, low reasoning, no shell, and no web. It captures accepted artifacts and immediately exercises a ReplayProvider-only rerun.

Provider-free replay of an accepted capture:

```bash
python -m imperium.live council-replay \
  --capture artifacts/gate-2f/accepted-replay.json \
  --output-dir artifacts/gate-2f-replay
```

If the council requests evidence, supply a JSON array of exact `EvidenceResolution` objects and resume explicitly:

```bash
python -m imperium.live council-resume-evidence \
  --checkpoint artifacts/gate-2f/live/session.json \
  --evidence artifacts/gate-2f/evidence-resolutions.json \
  --output-dir artifacts/gate-2f \
  --authorize RUN_FULL_COUNCIL
```

If one provider attempt fails or is ambiguous, either authorize one replacement with `council-retry --reason ... --authorize RUN_FULL_COUNCIL` or stop without a provider call using `council-abandon --reason ...`. The persisted `max_attempts_per_call` value controls how many sequential attempts can ever be authorized.

## Halt and failure behavior

- A missing evidence disposition fails closed and preserves the checkpoint; the engine never invents evidence.
- A failed or ambiguous provider attempt is not repeated automatically.
- Explicit retry or abandonment remains subject to the persisted attempt and token budgets.
- A structurally complete run without challenge consequences or revision signals fails the automated gate.
- An automated pass is still labeled as requiring human strategic review.

## Current validation

CI and local tests use ReplayProvider and simulated usage only. They prove frozen-case construction, explicit authorization, configurable per-call attempts, provider-free estimation, cached-token-preserving capture, tamper detection, complete replay equivalence, and rejection of a completion-only no-debate session. They do not invoke Codex.
