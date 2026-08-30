# Strategerium v0 Protocol

## Purpose

This protocol defines the minimum repeatable lifecycle needed to test Strategerium's central hypothesis:

> Separating the definition of success, execution, and completion judgment should make complex AI-assisted work more complete and reliable than the same Work Process operating alone.

This is a behavioral protocol, not an implementation architecture.

The first version should be runnable through instructions and isolated agent instances before additional software machinery is introduced.

---

# Core Principle: Acceptance Criteria Define Authorized Scope

The Execution Contract exists to turn the user's request into a complete, explicit, and bounded definition of success.

The governing scope rule is:

> **If an outcome, deliverable, feature, behavior, or quality requirement is not represented in the acceptance criteria, it is not part of the authorized work.**

The goal is the **minimum product that satisfies every stated user goal**.

This does not mean the Strategic Agent should interpret vague requests narrowly. The opposite is required: when a request is vague, incomplete, or expressed at a high level, the Strategic Agent must infer and define the acceptance criteria reasonably necessary for the user to regard the result as successful.

That expansion of scope belongs **only to the Strategic Agent**, before execution.

The Work Process may choose whatever internal implementation steps are necessary to satisfy the approved acceptance criteria, but it may not independently add new user-facing scope, deliverables, features, quality targets, or strategic requirements.

If the Work Process discovers that additional scope appears necessary to satisfy the user's actual objective, it must surface that issue as a potential contract defect rather than silently expanding the task.

The acceptance criteria therefore serve two functions at once:

1. they are the complete definition of what must be achieved;
2. they are the boundary beyond which the Work Process does not expand the task.

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
DRAFT EXECUTION CONTRACT
    |
    v
RULES LAWYER — CONTRACT REVIEW
    |
    +--> CONTRACT APPROVED
    |          |
    |          v
    |      WORK PROCESS
    |          |
    |          v
    |      READY FOR REVIEW
    |      Artifacts + Evidence
    |          |
    |          v
    |      RULES LAWYER — COMPLETION REVIEW
    |          |
    |          +--> COMPLETE
    |          |
    |          +--> REPAIR REQUIRED --> WORK PROCESS --> READY FOR REVIEW
    |          |
    |          +--> BLOCKED
    |          |
    |          +--> CONTRACT DEFECT --> STRATEGIC AGENT
    |
    +--> CONTRACT REVISION REQUIRED --> STRATEGIC AGENT
```

No work begins until the Rules Lawyer approves the Execution Contract.

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

The Strategic Agent should ask the user for clarification only when ambiguity would materially change the required outcome or acceptance criteria and a reasonable inference would risk producing the wrong result.

If the user's likely desired outcome can be inferred with reasonable confidence, the Strategic Agent should make the interpretation explicit in the contract instead of forcing unnecessary clarification.

---

# Phase 1 — Strategic Definition

## Actor

Strategic Agent

## Objective

Translate the user's request into the smallest complete set of acceptance criteria that, if all satisfied, should make the user reasonably consider the request fulfilled.

The Strategic Agent is not merely a transcription layer for requirements the user explicitly enumerated.

For vague or high-level requests, it must identify the implied conditions necessary for genuine user satisfaction while avoiding speculative extras.

## Procedure

The Strategic Agent:

1. reads the original request and relevant context;
2. identifies the user's underlying objective;
3. identifies every required deliverable and material success condition;
4. preserves explicit constraints and meaningful assumptions;
5. identifies likely false-completion traps;
6. decides whether specialist expertise would materially improve the contract;
7. if useful, invokes only the necessary isolated specialists with focused questions;
8. synthesizes specialist findings;
9. expands vague goals into concrete acceptance criteria where necessary for user satisfaction;
10. verifies that every deliverable, constraint, and material success condition is represented by one or more acceptance criteria;
11. defines reasonable evidence required for every criterion;
12. removes optional embellishment or speculative scope not necessary to satisfy the user's goals;
13. records meaningful out-of-scope boundaries where useful;
14. publishes a Draft Execution Contract for independent contract review.

## Specialist Rule

Specialists are optional.

The Strategic Agent owns the decision to invoke them and remains responsible for the resulting contract.

Specialist findings are advisory inputs, not independent requirements.

## Architecture Rule

The Strategic Agent does not normally design the implementation architecture.

It may consider architecture, design principles, technology constraints, security, maintainability, performance, interoperability, or similar concerns when they materially affect whether the user's objective can be satisfied.

Those concerns should normally appear as outcome-oriented acceptance criteria or constraints rather than prescribed implementation choices.

## Scope Authority

Only the Strategic Agent may expand the task beyond what the user stated explicitly, and only when the expansion is reasonably necessary to satisfy the user's actual objective.

It must not add work merely because the work would be useful, elegant, conventional, or considered best practice.

The test is:

> **Would omitting this condition create a material risk that all existing criteria could pass while the user would still reasonably consider the requested task incomplete or unsatisfactory?**

If yes, the Strategic Agent should normally add or refine an acceptance criterion.

If no, the condition should normally remain outside scope.

## Output

One versioned **Draft Execution Contract** for Rules Lawyer review.

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
  Covers: D1, C1, [objective/success condition]
  Evidence: ...
- AC-2: ...
  Covers: ...
  Evidence: ...

False-Completion Traps:
- F1 ...

Out of Scope:
- O1 ...

Specialist Use:
- none
or
- [specialist type]: [question asked] -> [material finding incorporated]

Contract Status:
DRAFT | APPROVED
```

---

# Acceptance-Criterion Rules

Acceptance criteria are the authoritative scope and success definition for execution.

Every criterion should be:

- traceable to the user's objective, a required deliverable, an explicit constraint, or a material implied success condition;
- independently understandable;
- observable or testable where reasonably possible;
- specific enough that the Rules Lawyer can distinguish pass from failure;
- no broader than necessary to protect the user's requested outcome;
- paired with reasonable evidence sufficient for independent verification.

Every required deliverable and material constraint must be covered by at least one acceptance criterion.

A condition that appears only in explanatory prose, a risk section, an assumption, a deliverables list, or worker reasoning is **not sufficient**. If it must be satisfied for completion, it belongs in the acceptance criteria.

Where completeness is enumerable, the criterion must preserve the enumeration.

Acceptance criteria should define outcomes rather than prescribe implementation unless the implementation itself is a user requirement or unavoidable constraint.

The target is neither the smallest possible checklist nor the most comprehensive imaginable product. It is the **smallest complete contract that captures everything necessary to satisfy the user's stated and reasonably implied goals**.

---

# Phase 2 — Pre-Execution Contract Review

## Actor

Rules Lawyer

## Objective

Determine whether the Draft Execution Contract is complete, faithful, minimal, and sufficiently verifiable **before any execution begins**.

This review exists because a worker can perfectly satisfy a bad contract.

## Inputs

The Rules Lawyer receives:

- the immutable original user request;
- relevant original context and constraints;
- the Draft Execution Contract.

It does not receive a proposed worker solution or worker reasoning.

## Review Questions

The Rules Lawyer evaluates:

1. **Goal fidelity** — Do the criteria collectively capture the user's actual objective?
2. **Coverage** — Is every required deliverable, explicit constraint, and material implied success condition represented in acceptance criteria?
3. **Sufficiency** — If every criterion passed, would the user reasonably regard the request as successfully fulfilled?
4. **Minimality** — Does the contract avoid optional features, preferences, or work not necessary to achieve the user's goals?
5. **Verifiability** — Can an independent evaluator reasonably determine whether each criterion passed?
6. **Scope integrity** — Are mandatory requirements actually expressed as acceptance criteria rather than hidden elsewhere in the contract?
7. **Implementation neutrality** — Does the contract avoid unnecessary architectural or implementation prescriptions?

## Contract Review Output

The Rules Lawyer returns:

```text
Contract Review

Goal Fidelity:
PASS | REVISION REQUIRED

Coverage:
PASS | REVISION REQUIRED

Minimality:
PASS | REVISION REQUIRED

Verifiability:
PASS | REVISION REQUIRED

Scope Integrity:
PASS | REVISION REQUIRED

Implementation Neutrality:
PASS | REVISION REQUIRED

Contract Judgment:
CONTRACT APPROVED | CONTRACT REVISION REQUIRED

Required Revisions:
- [specific smallest useful corrections]
```

### CONTRACT APPROVED

Allowed only when the Rules Lawyer determines that the acceptance criteria form a sufficiently complete, minimal, faithful, and verifiable definition of success.

The contract status changes to `APPROVED` and execution may begin.

### CONTRACT REVISION REQUIRED

Used when the contract is materially incomplete, over-scoped, ambiguous, non-verifiable, or otherwise insufficient.

The Rules Lawyer identifies the problem but does not rewrite the contract.

The Strategic Agent revises the affected portions and resubmits the contract for review.

No execution begins until approval.

---

# Phase 3 — Execution

## Actor

Work Process

## Input

The Work Process receives:

- the original user request;
- relevant task context;
- the **approved** Execution Contract.

It does not receive the Strategic Agent's private reasoning or specialist conversations unless a specialist result was incorporated into the approved contract or provided as necessary task evidence.

## Authority

The Work Process owns implementation, but not scope.

It may:

- plan;
- choose architecture;
- research implementation details;
- use tools;
- delegate;
- create or modify artifacts;
- test;
- revise its implementation approach;
- and otherwise solve the task as it judges appropriate within the approved contract.

## Scope Boundary

The Work Process must implement the **minimum sufficient product that satisfies all approved acceptance criteria**.

It must not independently add:

- new user-facing features;
- additional deliverables;
- broader quality targets;
- new strategic requirements;
- optional enhancements;
- or other scope not represented in the approved acceptance criteria.

Internal implementation work that is reasonably necessary to satisfy the criteria is allowed and does not itself need a separate acceptance criterion.

If the Work Process discovers that the approved criteria appear insufficient to achieve the user's actual objective, it must report a **POTENTIAL CONTRACT DEFECT** and stop treating the missing condition as authorized scope.

The issue returns to the Strategic Agent and Rules Lawyer for contract correction before that additional scope becomes authoritative.

## Completion Boundary

The Work Process may never emit `COMPLETE` as the authoritative terminal state.

When it believes all approved acceptance criteria are satisfied, it emits:

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

Potential Contract Defect:
- [none or explicit issue]

Worker Claim:
READY FOR REVIEW
```

The worker may explain evidence, but explanation is not a substitute for inspectable proof when proof can reasonably be produced.

The Work Process must not rewrite, reinterpret, or add acceptance criteria in its submission.

---

# Phase 4 — Completion Review

## Actor

Rules Lawyer

## Inputs

The Rules Lawyer receives:

- the original user request and relevant original context;
- the approved Execution Contract;
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

The Rules Lawyer evaluates the criteria exactly as approved. It must not expand scope during completion review.

### B. Intent Fidelity

Even though the contract was reviewed before execution, compare it again with the original user request to detect missed contract defects revealed by the actual result.

Ask:

> If every approved acceptance criterion passed exactly as written, would the user's original request materially be fulfilled?

If yes, proceed to the terminal judgment.

If no because the approved contract omitted or misstated a material requirement, return `CONTRACT DEFECT`.

The Rules Lawyer must not silently add new criteria and then fail the Work Process against them.

---

# Completion Review Output

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

- every approved acceptance criterion is `PASS`;
- required evidence is sufficient;
- intent fidelity passes;
- no unresolved blocker prevents the requested outcome.

The Rules Lawyer is the only Strategerium role authorized to issue this state.

## REPAIR REQUIRED

Used when one or more approved criteria are `FAIL` or `NOT PROVEN` and the contract itself remains valid.

The Rules Lawyer returns only the deficiencies relevant to those criteria and the evidence needed for reevaluation.

The task returns to the Work Process.

## BLOCKED

Used when completion depends on a specific external condition that cannot currently be resolved by the Work Process.

The blocker must be explicit.

A blocker is not a successful completion state.

## CONTRACT DEFECT

Used when the approved Execution Contract materially fails to represent the original user request.

The Rules Lawyer identifies the defect but does not rewrite the contract.

The task returns to the Strategic Agent for correction and then to the Rules Lawyer for contract approval before affected execution resumes.

---

# Repair Loop

A repair loop is intentionally narrow.

The Work Process receives:

- the current approved Execution Contract;
- the failed or unproven criterion identifiers;
- the Rules Lawyer's deficiency descriptions;
- the evidence required for reevaluation.

The worker repairs only what is necessary to satisfy the affected approved criteria and submits a new Review Package.

The Rules Lawyer reevaluates at minimum every affected criterion and must also ensure that the repair did not invalidate previously passing criteria when the change could reasonably have affected them.

The contract does not change during ordinary repair.

---

# Contract-Defect Loop

A contract defect is handled differently from execution failure.

The Strategic Agent receives:

- the original request;
- the current contract;
- the Rules Lawyer's identified contract defect or the Work Process's potential contract defect report.

The Strategic Agent then:

1. determines whether the defect is valid;
2. corrects only the affected portion of the contract;
3. increments the contract version;
4. identifies which existing work or prior review results may be invalidated by the correction;
5. submits the revised contract to the Rules Lawyer for pre-execution contract review.

The new or changed scope is not authorized until the Rules Lawyer approves the revised contract.

After approval, the Work Process performs only the additional or changed work required by the corrected criteria unless the correction materially changes the entire task.

The system preserves the previous contract version and reason for amendment so strategy/specification failures remain measurable.

---

# User Changes During a Run

The user may change the objective, scope, constraints, or desired output at any time.

A material user change supersedes the affected portion of the current Execution Contract.

The Strategic Agent updates the acceptance criteria and submits the revised contract for Rules Lawyer approval before further authoritative execution of the changed scope.

This is not classified as a contract defect.

It is a user-directed scope change.

---

# Information Boundaries

The minimum information-sharing rules are:

### Strategic Agent sees

- original request;
- original context;
- relevant source material;
- specialist findings it requested;
- Rules Lawyer contract-review deficiencies when applicable;
- later contract-defect reports when applicable.

### Specialist sees

- relevant original request/context;
- its focused assignment;
- source material necessary for that assignment.

### Work Process sees

- original request/context;
- approved Execution Contract;
- repair reports when applicable.

### Rules Lawyer sees during contract review

- original request/context;
- Draft Execution Contract.

### Rules Lawyer sees during completion review

- original request/context;
- approved Execution Contract;
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
Pre-execution Rules Lawyer review(s):
Contract revision count before execution:
Worker READY FOR REVIEW submissions:
Completion review result(s):
Repair-loop count:
Post-execution contract-defect count:
Final terminal state:
Human evaluation:
Notable missed requirement or false-completion event:
Notable unnecessary scope added:
```

The baseline run should use the same original user request and the same Work Process without the Strategerium wrapper wherever practical.

The purpose of the experiment is not to prove Strategerium works. It is to determine whether it does.

---

# v0 Success Question

After a meaningful sample of representative tasks, the first decision is simple:

> Does Strategerium materially reduce incomplete, weak, falsely completed, or unnecessarily expanded work enough to justify its added cost and complexity?

If not, the protocol should be revised or abandoned rather than expanded ceremonially.
