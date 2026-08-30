# Strategerium v0 Protocol

## Purpose

This protocol defines the minimum repeatable lifecycle needed to test Strategerium's central hypothesis:

> Separating the definition of success, execution, and completion judgment should make complex AI-assisted work more complete and reliable than the same Work Process operating alone.

This is a behavioral protocol, not an implementation architecture.

The first version should be runnable through instructions and isolated agent instances before additional software machinery is introduced.

---

# Core Lifecycle

```text
USER REQUEST
    |
    v
STRATEGIC AGENT
    |
    +--> optional isolated Specialist Agents
    |        |
    |        +--> findings
    |
    v
EXECUTION CONTRACT
    |
    v
WORK PROCESS
    |
    v
READY FOR REVIEW
Artifacts + Evidence
    |
    v
RULES LAWYER
    |
    +--> COMPLETE
    |
    +--> REPAIR REQUIRED --> WORK PROCESS --> READY FOR REVIEW
    |
    +--> BLOCKED
    |
    +--> CONTRACT DEFECT --> STRATEGIC AGENT --> corrected contract
                                      |
                                      v
                               affected work/review
```

The default path is linear.

Loopbacks occur only for explicit reasons defined below.

---

# Phase 0 — Intake

## Input

The original user request and all context the user provided for that request.

## Rule

The original request must be preserved verbatim or as an immutable source artifact for the entire run.

Later agents may interpret it but may not replace it with a rewritten version and treat the rewrite as authoritative.

## Clarification

The Strategic Agent should ask the user for clarification only when ambiguity would materially change the required outcome or acceptance criteria.

If a reasonable interpretation can preserve the user's intent without blocking progress, the Strategic Agent should state the assumption in the Execution Contract rather than creating unnecessary friction.

---

# Phase 1 — Strategic Definition

## Actor

Strategic Agent

## Objective

Define what successful completion means before seeing the Work Process's proposed solution.

## Procedure

The Strategic Agent:

1. reads the original request and relevant context;
2. identifies the underlying objective and required deliverables;
3. identifies explicit constraints and meaningful assumptions;
4. identifies likely false-completion traps;
5. decides whether specialist expertise would materially improve the contract;
6. if useful, invokes only the necessary isolated specialists with focused questions;
7. synthesizes specialist findings;
8. defines acceptance criteria;
9. defines reasonable evidence required for each criterion;
10. records meaningful out-of-scope boundaries where useful;
11. publishes the Execution Contract.

## Specialist Rule

Specialists are optional.

The Strategic Agent owns the decision to invoke them and remains responsible for the resulting contract.

Specialist findings are advisory inputs, not independent requirements.

## Architecture Rule

The Strategic Agent does not normally design the implementation architecture.

It may consider architecture, design principles, technology constraints, security, maintainability, performance, interoperability, or similar concerns when they materially affect successful outcomes.

Those concerns should normally appear as acceptance criteria or constraints rather than prescribed implementation choices.

## Output

One immutable-version **Execution Contract** for the initial execution attempt.

---

# Execution Contract Format

The v0 contract uses the following structure.

```text
Execution Contract

Request Reference:
[original request identifier or preserved text]

Objective:
[the outcome the user is trying to achieve]

Deliverables:
- D1 ...
- D2 ...

Constraints:
- C1 ...
- C2 ...

Assumptions:
- A1 ...

Acceptance Criteria:
- AC-1: ...
  Evidence: ...
- AC-2: ...
  Evidence: ...

False-Completion Traps:
- F1 ...

Out of Scope:
- O1 ...

Specialist Use:
- none
or
- [specialist type]: [question asked] -> [material finding incorporated]
```

## Acceptance-Criterion Rules

Each acceptance criterion should be:

- traceable to the user's objective, deliverables, constraints, or a material success condition;
- independently understandable;
- observable or testable where reasonably possible;
- specific enough that the Rules Lawyer can distinguish pass from failure;
- no broader than necessary to protect the user's requested outcome.

Where completeness is enumerable, the criterion should preserve the enumeration.

The contract should not prescribe implementation details merely because the Strategic Agent or a specialist prefers them.

---

# Phase 2 — Execution

## Actor

Work Process

## Input

The Work Process receives:

- the original user request;
- relevant task context;
- the published Execution Contract.

It does not receive the Strategic Agent's private reasoning or specialist conversations unless a specialist result was incorporated into the contract or provided as necessary task evidence.

## Authority

The Work Process owns execution.

It may:

- plan;
- choose architecture;
- research;
- use tools;
- delegate;
- create or modify artifacts;
- test;
- revise its implementation approach;
- and otherwise solve the task as it judges appropriate within the contract.

## Completion Boundary

The Work Process may never emit `COMPLETE` as the authoritative terminal state.

When it believes the task is finished, it emits:

> **READY FOR REVIEW**

and submits a Review Package.

---

# Review Package Format

The Work Process submits:

```text
Review Package

Artifacts:
- [artifact or location]

Acceptance Evidence:
- AC-1: [evidence]
- AC-2: [evidence]

Known Limitations / Blockers:
- [none or explicit limitations]

Worker Claim:
READY FOR REVIEW
```

The worker may explain evidence, but explanation is not a substitute for inspectable proof when proof can reasonably be produced.

The Work Process should not rewrite the acceptance criteria in its submission.

---

# Phase 3 — Independent Verification

## Actor

Rules Lawyer

## Inputs

The Rules Lawyer receives:

- the original user request and relevant original context;
- the current Execution Contract;
- the Review Package;
- access to the resulting artifacts and evidence needed for inspection.

It does not receive the Work Process's private reasoning or prior conversational assurances that work is complete.

## Procedure

The Rules Lawyer performs two reviews in order.

### A. Contract Compliance

For every acceptance criterion, assign exactly one disposition:

- `PASS`
- `FAIL`
- `BLOCKED`
- `NOT PROVEN`

Each disposition must cite or describe the evidence supporting it.

### B. Intent Fidelity

After criterion review, ask:

> If every acceptance criterion passed exactly as written, would the user's original request materially be fulfilled?

If yes, proceed to the terminal judgment.

If no because the contract omitted or misstated a material requirement, return `CONTRACT DEFECT`.

The Rules Lawyer must not silently add new criteria and then fail the Work Process against them.

---

# Rules Lawyer Output Format

```text
Verification Report

Criterion Results:
- AC-1: PASS | FAIL | BLOCKED | NOT PROVEN
  Evidence: ...
  Deficiency: [only if applicable]
- AC-2: ...

Intent Fidelity:
PASS | CONTRACT DEFECT
Reason: ...

Terminal Judgment:
COMPLETE | REPAIR REQUIRED | BLOCKED | CONTRACT DEFECT

Required Action:
[none, targeted repair, blocker resolution, or contract correction]
```

---

# Terminal States

## COMPLETE

Allowed only when:

- every required acceptance criterion is `PASS`;
- required evidence is sufficient;
- intent fidelity passes;
- no unresolved blocker prevents the requested outcome.

The Rules Lawyer is the only Strategerium role authorized to issue this state.

## REPAIR REQUIRED

Used when one or more criteria are `FAIL` or `NOT PROVEN` and the contract itself remains valid.

The Rules Lawyer returns only the deficiencies relevant to those criteria and the evidence needed for reevaluation.

The task returns to the Work Process.

## BLOCKED

Used when completion depends on a specific external condition that cannot currently be resolved by the Work Process.

The blocker must be explicit.

A blocker is not a successful completion state.

## CONTRACT DEFECT

Used when the Execution Contract materially fails to represent the original user request.

The Rules Lawyer identifies the defect but does not rewrite the contract.

The task returns to the Strategic Agent for correction.

---

# Repair Loop

A repair loop is intentionally narrow.

The Work Process receives:

- the current Execution Contract;
- the failed or unproven criterion identifiers;
- the Rules Lawyer's deficiency descriptions;
- the evidence required for reevaluation.

The worker repairs the deficiencies and submits a new Review Package.

The Rules Lawyer reevaluates at minimum every affected criterion and must also ensure that the repair did not invalidate previously passing criteria when the change could reasonably have affected them.

The contract does not change during ordinary repair.

---

# Contract-Defect Loop

A contract defect is handled differently from execution failure.

The Strategic Agent receives:

- the original request;
- the current contract;
- the Rules Lawyer's identified contract defect.

The Strategic Agent then:

1. determines whether the defect is valid;
2. corrects only the affected portion of the contract;
3. increments the contract version;
4. identifies which existing work or prior review results may be invalidated by the correction.

The Work Process then performs only the additional or changed work required by the corrected contract unless the correction materially changes the entire task.

The Rules Lawyer evaluates against the corrected contract.

The system should preserve a record of the original contract and the reason for amendment so specification failures remain measurable.

---

# User Changes During a Run

The user may change the objective, scope, constraints, or desired output at any time.

A material user change supersedes the affected portion of the current Execution Contract.

The Strategic Agent updates the contract before further authoritative completion review.

This is not classified as a contract defect.

It is a user-directed scope change.

---

# Information Boundaries

The minimum information-sharing rules are:

### Strategic Agent sees

- original request;
- original context;
- relevant source material;
- specialist findings it requested.

### Specialist sees

- relevant original request/context;
- its focused assignment;
- source material necessary for that assignment.

### Work Process sees

- original request/context;
- Execution Contract;
- repair reports when applicable.

### Rules Lawyer sees

- original request/context;
- current Execution Contract;
- Review Package;
- artifacts/evidence necessary for verification.

Private reasoning is not a handoff artifact.

Shared conversation is not the default coordination model.

---

# What v0 Does Not Define

The protocol intentionally does not yet define:

- a required orchestration platform;
- a permanent set of specialist agents;
- model selection rules;
- token budgets;
- automatic parallelism;
- a state-machine implementation;
- persistent databases;
- autonomous external action;
- voting or debate;
- mandatory architecture review;
- or a fixed number of repair attempts.

Those decisions should be introduced only when testing demonstrates that they are necessary.

---

# Minimum Experimental Record

Each Strategerium test run should preserve enough information for later comparison without recording unnecessary internal reasoning.

Record:

```text
Run ID:
Task:
Worker system/model:
Baseline or Strategerium:
Strategic Agent system/model:
Specialists invoked:
Execution Contract version(s):
Worker READY FOR REVIEW submissions:
Rules Lawyer system/model:
Verification result(s):
Repair-loop count:
Contract-defect count:
Final terminal state:
Human evaluation:
Notable missed requirement or false-completion event:
```

The baseline run should use the same original user request and the same Work Process without the Strategerium wrapper wherever practical.

The purpose of the experiment is not to prove Strategerium works. It is to determine whether it does.

---

# v0 Success Question

After a meaningful sample of representative tasks, the first decision is simple:

> Does Strategerium materially reduce incomplete, weak, or falsely completed work enough to justify its added cost and complexity?

If not, the protocol should be revised or abandoned rather than expanded ceremonially.
