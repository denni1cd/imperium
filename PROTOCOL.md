# Strategerium v0 Protocol

## Purpose

This protocol defines the minimum repeatable lifecycle needed to test Strategerium's central hypothesis:

> Separating the definition of success, execution, and completion judgment should make complex AI-assisted work more complete and reliable than the same Work Process operating alone.

This is a behavioral protocol, not an implementation architecture.

The first version should be runnable through instructions and isolated agent instances before additional software machinery is introduced.

---

# Core Principle: Acceptance Criteria Define Outcomes, Not Implementation Means

The Execution Contract turns the user's request into a complete, explicit, and bounded definition of success.

The governing scope rule is:

> **If an outcome, deliverable, feature, behavior, or quality requirement is not represented in the acceptance criteria, it is not part of the authorized product scope.**

The target is the **minimum product scope that satisfies every stated and reasonably implied user goal**.

This is a boundary on **what the Work Process is trying to achieve**, not on **how it may achieve it**.

The Work Process has broad execution authority. It may create supporting code, tools, scripts, tests, asset pipelines, temporary infrastructure, research artifacts, generators, converters, internal utilities, or other intermediate capabilities whenever they are reasonably useful in satisfying the approved acceptance criteria. Supporting work does not require its own acceptance criterion unless that supporting artifact is itself a required user-facing deliverable or outcome.

For example, a request to create a tower-defense game with unique art may legitimately lead the Work Process to build an art-generation or asset-building tool if that helps satisfy the approved criteria. It does not authorize building an unrelated stock tracker.

The distinction is:

> **The Strategic Agent controls what must be achieved. The Work Process has wide discretion over how to achieve it. The Rules Lawyer determines whether the approved outcomes were achieved. The user authorizes execution.**

This does not mean the Strategic Agent should interpret vague requests narrowly. When a request is vague, incomplete, or expressed at a high level, the Strategic Agent must infer and define the acceptance criteria reasonably necessary for the user to regard the result as successful.

Expansion of **product scope** belongs only to the Strategic Agent and must be approved by the Rules Lawyer before execution. Expansion of **implementation means** belongs to the Work Process and does not require contract amendment when it materially serves the approved criteria.

---

# Core Lifecycle

```text
USER REQUEST
    |
    v
STRATEGIC AGENT
    |
    +--> optional isolated Specialist Agents --> findings
    |
    v
DRAFT EXECUTION CONTRACT
    |
    v
RULES LAWYER — CONTRACT REVIEW
    |
    +--> CONTRACT REVISION REQUIRED --> STRATEGIC AGENT
    |
    v
CONTRACT APPROVED
    |
    v
USER APPROVAL GATE
    |
    +--> CHANGE REQUEST --> STRATEGIC AGENT --> RULES LAWYER — CONTRACT REVIEW
    |
    v
USER APPROVED
    |
    v
WORK PROCESS
    |
    v
READY FOR REVIEW
Artifacts + Evidence
    |
    v
RULES LAWYER — COMPLETION REVIEW
    |
    +--> COMPLETE
    +--> REPAIR REQUIRED --> WORK PROCESS --> READY FOR REVIEW
    +--> BLOCKED
    +--> CONTRACT DEFECT --> STRATEGIC AGENT --> CONTRACT REVIEW --> USER APPROVAL
```

No work begins until both of these conditions are satisfied:

1. the Rules Lawyer has returned `CONTRACT APPROVED`; and
2. the user has explicitly approved that same contract for execution.

Rules Lawyer approval is a quality gate, not execution authority.

---

# Phase 0 — Intake

The original user request and all user-provided context are preserved as immutable source material for the run.

Later agents may interpret the request but may not replace it with a rewritten version and treat the rewrite as authoritative.

The Strategic Agent should ask for clarification only when ambiguity would materially change the required outcome or acceptance criteria and a reasonable inference would risk producing the wrong result. Otherwise it should make the best supported interpretation and record material assumptions.

---

# Phase 1 — Strategic Definition

## Actor

Strategic Agent

## Objective

Translate the user's request into the smallest complete set of acceptance criteria that, if all satisfied, should make the user reasonably consider the request fulfilled.

For vague or high-level requests, the Strategic Agent must identify implied conditions necessary for genuine user satisfaction while avoiding speculative extras.

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
12. for criteria concerning observable runtime or interactive behavior, requires evidence that directly exercises that behavior when doing so is reasonably feasible;
13. removes optional product embellishment or speculative scope not necessary to satisfy the user's goals;
14. records meaningful out-of-scope boundaries where useful;
15. publishes a Draft Execution Contract for independent contract review.

## Specialist Rule

Specialists are optional. The Strategic Agent owns the decision to invoke them and remains responsible for the resulting contract. Specialist findings are advisory inputs, not independent requirements.

## Architecture Rule

The Strategic Agent does not normally design the implementation architecture. It may consider architecture, design principles, technology constraints, security, maintainability, performance, interoperability, or similar concerns when they materially affect whether the user's objective can be satisfied.

Those concerns should normally appear as outcome-oriented acceptance criteria or constraints rather than prescribed implementation choices.

## Scope Authority

Only the Strategic Agent may expand **product scope** beyond what the user stated explicitly, and only when the expansion is reasonably necessary to satisfy the user's actual objective.

It must not add user-facing work merely because that work would be useful, elegant, conventional, or considered best practice.

The test is:

> **Would omitting this outcome create a material risk that all existing criteria could pass while the user would still reasonably consider the requested task incomplete or unsatisfactory?**

If yes, the Strategic Agent should normally add or refine an acceptance criterion. If no, the outcome should normally remain outside product scope.

This rule does not restrict implementation methods available to the Work Process.

## Output

One versioned **Draft Execution Contract** for Rules Lawyer review.

---

# Execution Contract Format

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

Execution Authorization:
PENDING USER APPROVAL | USER APPROVED
```

`Contract Status: APPROVED` records Rules Lawyer approval. It does not imply execution authorization.

---

# Acceptance-Criterion Rules

Acceptance criteria are the authoritative definition of required outcomes and product scope.

Every criterion should be:

- traceable to the user's objective, a required deliverable, an explicit constraint, or a material implied success condition;
- independently understandable;
- observable or testable where reasonably possible;
- specific enough that the Rules Lawyer can distinguish pass from failure;
- no broader than necessary to protect the user's requested outcome;
- paired with reasonable evidence sufficient for independent verification.

Every required deliverable and material constraint must be covered by at least one acceptance criterion.

A condition that appears only in explanatory prose, a risk section, an assumption, a deliverables list, or worker reasoning is not sufficient if it is required for user-facing completion. If an outcome must be satisfied for completion, it belongs in the acceptance criteria.

Internal implementation choices and supporting artifacts do not need acceptance criteria merely because the Work Process creates them.

Where completeness is enumerable, the criterion must preserve the enumeration.

Acceptance criteria should define outcomes rather than prescribe implementation unless the implementation itself is a user requirement or unavoidable constraint.

The target is the **smallest complete product contract that captures everything necessary to satisfy the user's stated and reasonably implied goals**, while leaving the Work Process broad freedom to determine the means.

## Behavioral Evidence Rule

Evidence must prove the kind of claim being made.

When an acceptance criterion concerns observable runtime or interactive behavior and that behavior can reasonably be exercised, the required evidence must include direct execution, interaction, an automated behavioral test, an end-to-end run, or another method that actually exercises the behavior.

Source inspection, syntax validation, static analysis, configuration review, or code reading may support behavioral verification, but they do not by themselves prove that feasible observable behavior works.

If direct exercise is not reasonably feasible because of a specific external condition, the evidence requirement should identify that limitation. Completion review must not manufacture a `PASS` from static inspection alone; `BLOCKED` or `NOT PROVEN` should be used when appropriate.

Verification remains proportional. The protocol requires exercised evidence where behavior matters, not ceremony where it does not.

---

# Phase 2 — Pre-Execution Contract Review

## Actor

Rules Lawyer

## Objective

Determine whether the Draft Execution Contract is complete, faithful, minimal, and sufficiently verifiable before it is presented to the user for execution approval.

## Review Questions

The Rules Lawyer evaluates:

1. **Goal fidelity** — Do the criteria collectively capture the user's actual objective?
2. **Coverage** — Is every required deliverable, explicit constraint, and material implied success condition represented?
3. **Sufficiency** — If every criterion passed, would the user reasonably regard the request as fulfilled?
4. **Product minimality** — Does the contract avoid unrelated or unnecessary product scope without restricting useful implementation means?
5. **Verifiability** — Can an independent evaluator reasonably determine whether each criterion passed, including exercised evidence for feasible observable behavior?
6. **Scope integrity** — Are mandatory outcomes expressed as acceptance criteria rather than hidden elsewhere?
7. **Implementation neutrality** — Does the contract leave the Work Process free to choose supporting architecture, tools, code, infrastructure, and methods unless genuinely constrained?

## Contract Review Output

```text
Contract Review

Goal Fidelity:
PASS | REVISION REQUIRED

Coverage:
PASS | REVISION REQUIRED

Product Minimality:
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

`CONTRACT APPROVED` means the contract is fit to present to the user. It does not authorize the Work Process to begin.

---

# Phase 2.5 — User Approval Gate

## Actor

User / Sovereign

## Objective

Give the user explicit authority over whether the approved Execution Contract should actually be executed.

## Procedure

After the Rules Lawyer returns `CONTRACT APPROVED`:

1. present the approved Execution Contract to the user;
2. stop before invoking the Work Process;
3. ask for explicit approval to execute that contract;
4. begin execution only if the user approves;
5. if the user requests a material contract change, return the affected scope to the Strategic Agent and then through Rules Lawyer review before seeking approval again.

The approval gate is hard.

The system must not treat any of the following as approval:

- the user's original request to perform the task;
- silence;
- lack of objections;
- a prior approval of an earlier contract version;
- the Rules Lawyer's `CONTRACT APPROVED` judgment;
- an agent's belief that execution is obviously desired.

If completion review later identifies a `CONTRACT DEFECT` and the contract changes, the corrected contract must receive fresh explicit user approval before execution resumes.

Ordinary `REPAIR REQUIRED` work under an unchanged, already user-approved contract does not require another approval.

## Output

Record one of:

```text
Execution Authorization:
USER APPROVED
```

or

```text
Execution Authorization:
NOT APPROVED — contract change requested
```

---

# Phase 3 — Execution

## Actor

Work Process

## Prerequisite

Execution may begin only after the current approved contract has explicit `USER APPROVED` execution authorization.

## Authority

The Work Process owns implementation and has broad authority to do everything reasonably useful in completing the task, subject to user permissions, safety constraints, available tools, and the approved product scope.

It may, among other things:

- plan and revise its plan;
- choose or change architecture;
- research implementation details;
- write supporting or production code;
- build internal tools and utilities;
- create asset-generation or transformation pipelines;
- create tests, validators, benchmarks, and test harnesses;
- create temporary infrastructure or intermediate artifacts;
- use tools and external resources;
- delegate to execution subagents;
- generate, transform, or organize assets;
- automate repetitive work;
- and otherwise choose the means it judges useful for satisfying the approved acceptance criteria.

Supporting work is permitted when it has a reasonable connection to satisfying one or more approved criteria. It need not be separately enumerated in the contract and need not be proven indispensable.

## Product-Scope Boundary

The Work Process may not independently add a new user-facing outcome, feature, deliverable, strategic goal, or quality target unrelated to the approved acceptance criteria.

The relevant test is not "Was this implementation step explicitly listed?" It is:

> **Does this work reasonably serve the approved outcomes, or is it pursuing a new outcome of its own?**

Work that reasonably serves the approved outcomes is within execution authority. Work pursuing an unrelated outcome is outside scope.

If the Work Process discovers that an additional **product outcome** appears necessary to satisfy the user's actual objective but is absent from the approved criteria, it reports a `POTENTIAL CONTRACT DEFECT`. It does not need contract revision merely to create a new implementation means for an already-approved outcome.

## Completion Boundary

The Work Process may never authoritatively emit `COMPLETE`.

When it believes all approved acceptance criteria are satisfied, it emits `READY FOR REVIEW` and submits:

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
- [none or explicit missing product outcome]

Worker Claim:
READY FOR REVIEW
```

The Work Process must not rewrite or add acceptance criteria in its submission.

---

# Phase 4 — Completion Review

## Actor

Rules Lawyer

The Rules Lawyer receives the original request/context, approved and user-authorized Execution Contract, Review Package, and access to necessary artifacts/evidence.

For every acceptance criterion it assigns exactly one disposition:

- `PASS`
- `FAIL`
- `BLOCKED`
- `NOT PROVEN`

It evaluates approved outcomes, not whether it personally approves of the Work Process's implementation choices or supporting work.

For observable runtime or interactive behavior that can reasonably be exercised, `PASS` requires evidence from actual execution, interaction, an automated behavioral test, an end-to-end run, or equivalent direct exercise. Static inspection alone is insufficient proof of feasible behavior.

After criterion review, it again asks:

> **If every approved acceptance criterion passed exactly as written, would the user's original request materially be fulfilled?**

If no because the approved contract omitted or misstated a material outcome, it returns `CONTRACT DEFECT`. It must not silently add new criteria and fail the Work Process against them.

## Completion Review Output

```text
Verification Report

Criterion Results:
- AC-1: PASS | FAIL | BLOCKED | NOT PROVEN
  Evidence: ...
  Deficiency: [only if applicable]

Intent Fidelity:
PASS | CONTRACT DEFECT
Reason: ...

Terminal Judgment:
COMPLETE | REPAIR REQUIRED | BLOCKED | CONTRACT DEFECT

Required Action:
[none, targeted repair, blocker resolution, or contract correction]
```

---

# Terminal States and Loops

## COMPLETE

Allowed only when every approved criterion passes, required evidence is sufficient, intent fidelity passes, and no unresolved blocker prevents the requested outcome.

## REPAIR REQUIRED

Used when criteria fail or remain unproven while the contract remains valid. The Work Process receives targeted deficiencies and retains broad implementation authority in repairing them.

Because the contract is unchanged, ordinary repair does not require another user approval.

## BLOCKED

Used when completion depends on a specific external condition that cannot currently be resolved.

## CONTRACT DEFECT

Used when the approved contract materially fails to represent the original user request. The issue returns to the Strategic Agent, which revises the affected product scope and resubmits the contract to the Rules Lawyer for approval.

Because the contract changed, the corrected contract must then receive fresh explicit user approval before the Work Process resumes execution.

Ordinary repair does not change the contract. Contract defects and material user-directed scope changes do.

---

# Information Boundaries

- **Strategic Agent:** original request/context, relevant source material, requested specialist findings.
- **Specialist:** relevant request/context, focused assignment, necessary sources.
- **User approval gate:** approved Execution Contract only; execution remains paused until explicit approval.
- **Work Process:** original request/context, approved Execution Contract, recorded user execution authorization, repair reports when applicable.
- **Rules Lawyer:** original request/context, current contract, and during completion review the Review Package plus necessary artifacts/evidence.

Private reasoning is not a handoff artifact. Shared conversation is not the default coordination model.

---

# What v0 Does Not Define

The protocol intentionally does not yet define a required orchestration platform, permanent specialist set, model-selection rules, token budgets, automatic parallelism, persistent state implementation, autonomous external action, voting, mandatory architecture review, or fixed repair-attempt count.

These should be introduced only when testing demonstrates a need.

---

# Minimum Experimental Record

Record:

```text
Run ID:
Task:
Worker system/model:
Baseline or Strategerium:
Strategic Agent system/model:
Specialists invoked:
Execution Contract version(s):
Pre-execution contract-review result(s):
User execution approval event(s):
Worker READY FOR REVIEW submissions:
Rules Lawyer system/model:
Completion verification result(s):
Behavioral evidence used for behavioral criteria:
Repair-loop count:
Contract-defect count:
Final terminal state:
Human evaluation:
Notable missed requirement, false-completion event, unnecessary product scope, implementation restriction, approval-gate violation, or verification weakness:
```

The baseline should use the same original request and same Work Process without the Strategerium wrapper wherever practical.

---

# v0 Success Question

> **Does Strategerium materially reduce incomplete, weak, falsely completed, or unnecessarily expanded work without materially impairing the Work Process's ability to solve the task?**

If not, revise or abandon the protocol rather than expanding it ceremonially.
