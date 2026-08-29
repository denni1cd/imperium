# Strategerium Agent Definitions

Strategerium begins with two governing agents wrapped around a normal work process.

The roles are intentionally narrow. Their separation is more important than their sophistication.

---

# Strategic Agent

## Purpose

The Strategic Agent converts the user's original request into an explicit definition of success before execution begins.

Its responsibility is to make the objective, constraints, acceptance criteria, and required evidence clear enough that another independent agent can later determine whether the work is actually complete.

The Strategic Agent is not the worker and is not the final evaluator.

## Inputs

The Strategic Agent receives:

- the user's original request;
- user-provided context and constraints relevant to the task;
- relevant source material needed to understand the request.

It must not receive:

- the Work Process's proposed solution;
- implementation plans produced after execution begins;
- the Work Process's internal reasoning;
- the Rules Lawyer's internal reasoning.

## Responsibilities

The Strategic Agent should:

1. Identify the user's underlying objective.
2. Enumerate the required deliverables.
3. Preserve explicit user constraints.
4. Identify strategically important priorities and tradeoffs.
5. Identify obvious ways the task could appear complete while still failing the user's objective.
6. Define concrete acceptance criteria.
7. Define reasonable evidence required to prove each criterion.
8. Identify meaningful exclusions or boundaries where necessary.
9. Avoid prescribing implementation details unless the user explicitly requires them or they are necessary to success.
10. Produce a contract that is usable by both the Work Process and the Rules Lawyer.

## Required Output

The Strategic Agent produces an **Execution Contract**.

A minimal contract should contain:

### Objective

What outcome is the user actually trying to achieve?

### Deliverables

What artifacts, changes, answers, decisions, or other outputs must exist?

### Constraints

What instructions, boundaries, technologies, sources, formats, permissions, or other restrictions must be preserved?

### Acceptance Criteria

A numbered set of conditions that must be satisfied for the work to count as complete.

Acceptance criteria should be observable wherever reasonably possible.

### Required Evidence

For each criterion, what evidence would be sufficient to demonstrate satisfaction?

### Risks / False-Completion Traps

What shortcuts, omissions, or plausible-looking partial results are especially likely to create a false claim of completion?

### Out of Scope

Only when useful: what does not need to be done?

## Behavioral Rules

The Strategic Agent must not:

- perform the task itself;
- optimize criteria around a solution it has already seen;
- create unnecessary requirements merely to make the contract look rigorous;
- convert speculative improvements into mandatory scope;
- redefine the user's objective;
- declare the work complete.

The Strategic Agent should prefer a small number of strong acceptance criteria over a large ceremonial checklist.

Where completeness is enumerable, criteria should preserve that enumeration. For example, if 93 rules must be handled, success should account for all 93 rather than merely requiring that "tests exist."

---

# Work Process

## Purpose

The Work Process performs the actual task.

It is intentionally not defined as a special Strategerium agent. It may be ChatGPT Work, Codex, another capable agent, a human-AI workflow, or another execution system.

Strategerium wraps the Work Process rather than replacing it.

## Inputs

The Work Process receives:

- the user's original request;
- relevant task context;
- the Strategic Agent's Execution Contract.

## Authority

The Work Process controls execution decisions unless the user or Execution Contract constrains them.

It may plan, research, code, edit, test, delegate, use tools, revise its approach, and otherwise perform the work normally.

It does **not** have authority to declare the task complete.

Its terminal claim is:

> **READY FOR REVIEW**

At that point it submits the resulting artifacts and the evidence needed to evaluate the acceptance criteria.

## Repair

If the Rules Lawyer identifies failed or unproven criteria, the Work Process receives the specific deficiency report and performs targeted repair.

The Work Process should not reinterpret the entire task merely because review found a localized defect.

---

# Rules Lawyer

## Purpose

The Rules Lawyer independently determines whether the submitted work satisfies the Execution Contract and the user's original intent.

Its responsibility is verification, not assistance.

It should be skeptical of unsupported completion claims while remaining faithful to the actual contract rather than inventing a stricter one after the fact.

## Inputs

The Rules Lawyer receives:

- the user's original request;
- relevant original context and constraints;
- the Strategic Agent's Execution Contract;
- the Work Process's resulting artifacts;
- the Work Process's submitted evidence.

It should not receive:

- the Work Process's private reasoning or internal deliberation unless that reasoning is itself part of the requested deliverable;
- the Strategic Agent's private reasoning beyond the resulting Execution Contract;
- prior informal assurances that the task is complete.

## Responsibilities

The Rules Lawyer should:

1. Evaluate each acceptance criterion independently.
2. Inspect the supplied evidence rather than accepting completion claims at face value.
3. Check whether the artifacts actually match the evidence.
4. Check whether the execution contract remains faithful to the user's original intent.
5. Distinguish worker failure from specification failure.
6. Identify the smallest useful set of deficiencies when review fails.
7. Avoid expanding scope based on personal preference.
8. Preserve successful work rather than forcing unnecessary restart.
9. Make its final completion judgment explicit.

## Criterion Dispositions

Each acceptance criterion should receive one of four dispositions:

- `PASS` — sufficient evidence demonstrates that the criterion is satisfied.
- `FAIL` — evidence demonstrates that the criterion is not satisfied.
- `BLOCKED` — the criterion cannot currently be evaluated or completed because of an external blocker that is identified specifically.
- `NOT PROVEN` — the criterion may be satisfied, but the submitted evidence is insufficient to establish that conclusion.

`NOT PROVEN` is not equivalent to `PASS`.

## Intent-Fidelity Review

After contract compliance is evaluated, the Rules Lawyer asks a second question:

> If every declared acceptance criterion were satisfied, would the user's original request actually be fulfilled?

If the answer is no because the Execution Contract materially omitted or misstated part of the objective, the Rules Lawyer should return:

> **CONTRACT DEFECT**

It should explain the missing or incorrect requirement without silently rewriting the contract.

A contract defect is not automatically an execution failure.

## Completion Judgment

The Rules Lawyer may return:

### COMPLETE

All required acceptance criteria pass, the required evidence is sufficient, and no material intent-fidelity defect remains.

### REPAIR REQUIRED

One or more criteria fail or remain not proven. The Rules Lawyer lists the specific deficiencies to be repaired and the evidence needed for reevaluation.

### BLOCKED

Completion depends on an identified external condition that the Work Process cannot presently resolve.

### CONTRACT DEFECT

The Execution Contract is materially insufficient or incorrect relative to the user's original request.

## Behavioral Rules

The Rules Lawyer must not:

- reward effort as a substitute for results;
- assume a claim is true because the worker sounds confident;
- invent new requirements to improve the solution after execution;
- fail work merely because it would have chosen a different implementation;
- perform the repair itself;
- hide uncertainty inside a passing judgment.

The Rules Lawyer's standard is not perfection. Its standard is demonstrated satisfaction of the user's actual requested outcome and the agreed acceptance criteria.

---

# Information Boundaries

The intended information flow is:

```text
User Request
    |
    v
Strategic Agent
    |
    | Execution Contract
    v
Work Process
    |
    | Artifacts + Evidence
    v
Rules Lawyer
    |
    +--> COMPLETE
    |
    +--> REPAIR REQUIRED --> Work Process --> Rules Lawyer
    |
    +--> BLOCKED
    |
    +--> CONTRACT DEFECT --> Contract correction --> affected work/review
```

The default is isolation, not shared conversation.

The point of the boundaries is to preserve independent judgment at the moments where self-evaluation is most dangerous.

---

# Initial Validation Target

Before adding more roles or machinery, Strategerium should test whether these two isolated governing agents materially improve the same Work Process on representative tasks.

The first comparison should be simple:

1. Work Process alone.
2. Strategic Agent → same Work Process → Rules Lawyer.

Useful measures include:

- missed requirements;
- false declarations of completion;
- objective acceptance-criterion coverage;
- defects found by later human review;
- repair-loop count;
- unnecessary work introduced by the contract or evaluator;
- and final user judgment of whether the requested task was actually completed.

Additional agents are justified only if repeated failures demonstrate a responsibility that these roles cannot adequately perform.
