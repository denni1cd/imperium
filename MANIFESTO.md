# Strategerium Manifesto

## Purpose

**Strategerium exists to make complex AI-assisted work more reliable by separating the definition of success, the performance of work, and the judgment of completion.**

Its purpose is not to make a worker agent more elaborate. Its purpose is to prevent a worker from quietly redefining the task, lowering the standard, or declaring success without sufficient evidence.

The system should improve the probability that the user receives the work they actually asked for, completed to an explicit and verifiable standard.

That is the measure against which Strategerium should be judged.

---

## The Central Hypothesis

A capable AI worker can plan and execute complex tasks, but a recurring failure mode is that the same process which performs the work also decides whether its own work is complete.

Strategerium tests a different hypothesis:

> **Complex AI work becomes more reliable when definition of success, execution, and verification are separated, and when completion authority belongs to an independent evaluator rather than the process performing the work.**

If this separation does not materially improve completeness, fidelity, and quality over an ordinary capable worker, Strategerium has failed regardless of how sophisticated its architecture becomes.

---

## The Fundamental Rule

> **The process that performs the work does not have authority to declare the work complete.**

The worker may report progress and may state that it is ready for evaluation.

Only independent verification can establish that the requested work is complete.

---

## The Three Responsibilities

Strategerium separates complex work into three responsibilities.

### 1. Strategy

Before execution begins, an independent **Strategic Agent** interprets the user's request and defines what successful completion means.

It produces an execution contract containing, as appropriate:

- the underlying objective;
- required deliverables;
- explicit constraints;
- strategic priorities;
- important risks and likely failure modes;
- acceptance criteria;
- evidence required to demonstrate each criterion;
- and meaningful exclusions from scope.

The Strategic Agent defines the destination and the standard of success. It does not prescribe unnecessary implementation details or perform the work itself.

### 2. Execution

A normal **Work Process** performs the task.

The Work Process may use whatever planning, tools, agents, code, research, or workflows are appropriate to the task. Strategerium should not unnecessarily constrain how competent work is performed.

The Work Process receives the user's original request and the execution contract.

It may not declare the task complete. When it believes the work is finished, it submits the resulting artifacts and supporting evidence as **READY FOR REVIEW**.

### 3. Verification

An independent **Rules Lawyer** evaluates the result.

The Rules Lawyer determines whether the work actually satisfies the execution contract and remains faithful to the user's original intent.

It does not reward effort, plausible explanations, or unsupported claims. It evaluates demonstrated results.

For each acceptance criterion, the Rules Lawyer should reach an explicit disposition such as:

- `PASS`;
- `FAIL`;
- `BLOCKED`;
- or `NOT PROVEN`.

A task is complete only when the required criteria have passed and no unresolved defect prevents the user's objective from being satisfied.

---

## Isolation Is a Design Requirement

The Strategic Agent and Rules Lawyer must be isolated from the Work Process and from one another's internal reasoning.

The Strategic Agent defines success before seeing the worker's proposed solution. This prevents acceptance criteria from being unconsciously tailored to whatever implementation the worker happens to choose.

The Rules Lawyer does not participate in execution. This prevents it from becoming invested in defending decisions it helped make.

Information should flow deliberately:

**User Request → Strategic Agent → Work Process → Rules Lawyer**

The system should not default to a shared multi-agent conversation.

Only the artifacts and context necessary for the next responsibility should cross each boundary.

---

## Evidence, Not Assertion

Strategerium distinguishes between work that may have happened and work that has been demonstrated.

> **Absence of evidence is not evidence of completion.**

Claims such as "all tests pass," "all requirements were reviewed," or "the implementation is complete" are not sufficient by themselves when objective evidence can reasonably be provided.

Acceptance criteria should define what evidence is appropriate for the task. Evidence may include test results, artifact inspection, counts, traceability records, source citations, screenshots, diffs, executed commands, or other verifiable outputs.

The amount of evidence should be proportional to the consequence and complexity of the task. Strategerium should demand proof where proof matters, not bureaucracy for its own sake.

---

## Contract Compliance and Intent Fidelity

A worker can satisfy a bad specification.

Therefore the Rules Lawyer has two distinct responsibilities:

### Contract Compliance

Did the Work Process satisfy the acceptance criteria established before execution?

### Intent Fidelity

Would satisfying those criteria actually satisfy the user's original request and objective?

The Rules Lawyer may not silently invent new requirements merely because it prefers a different solution.

If the execution contract itself is materially incomplete or incorrect, the Rules Lawyer should identify a **CONTRACT DEFECT** rather than misclassifying the problem as worker failure.

The contract can then be corrected and the affected work reevaluated.

---

## Failures Should Be Diagnosable

Strategerium should make failures attributable rather than merely producing a generic unsuccessful result.

Important failure categories include:

- **Strategy failure** — the Strategic Agent misunderstood or materially underspecified the objective.
- **Execution failure** — the Work Process had an adequate contract but failed to satisfy it.
- **Evidence failure** — completion may be plausible, but required evidence is missing or insufficient.
- **Verification failure** — the Rules Lawyer incorrectly accepted or rejected the result.

These categories exist to improve the system through measurement, not to assign blame.

---

## Repair Should Be Targeted

A failed review should not automatically restart the task or rewrite the strategy.

The Rules Lawyer should identify the smallest useful set of deficiencies and return those to the Work Process for correction.

The worker should repair the failed or unproven criteria and resubmit the relevant evidence.

The execution contract should remain stable unless review identifies a genuine contract defect or the user's objective changes.

This protects the task from review-driven scope drift.

---

## The User Remains Authoritative

The user's goals, constraints, and explicit instructions are authoritative.

The Strategic Agent may clarify implications and expose contradictions. The Rules Lawyer may determine that a result does not actually satisfy the stated objective. Neither may quietly substitute its own preferred objective for the user's.

Strategerium exists to enforce fidelity to the requested outcome, not to create a new authority over the user.

---

## Simplicity Is a Requirement

Strategerium should use the simplest mechanism capable of testing its central hypothesis.

Therefore:

> **Instructions before infrastructure.**

> **Explicit responsibility before additional agents.**

> **Evidence of failure before additional machinery.**

The initial system needs only:

1. one Strategic Agent;
2. one normal Work Process;
3. one Rules Lawyer;
4. and a repair loop when verification fails.

No voting system, critic swarm, committee, elaborate state machine, or additional supervisory layer is justified until repeated evaluation demonstrates a problem that requires it.

---

## Validation Before Expansion

The first objective is to determine whether the architecture actually improves work.

Strategerium should be evaluated against ordinary Work processes on real tasks where completeness and quality can be judged.

The minimum system must demonstrate that:

- the Strategic Agent captures the user's actual objective;
- acceptance criteria are concrete enough to expose incomplete work;
- the Work Process remains free to execute effectively without controlling the success standard;
- the Rules Lawyer catches meaningful omissions and unsupported completion claims;
- failed reviews produce useful, targeted repairs rather than churn;
- successful reviews correspond to genuinely satisfactory outcomes;
- and the resulting work is measurably more complete and reliable than the same Work process operating alone.

Expansion should occur only in response to demonstrated limitations.

---

## Governing Principle

When there is tension between making Strategerium more elaborate and making the work more reliable, choose reliability.

When there is tension between trusting a worker's declaration and inspecting the evidence, inspect the evidence.

When there is tension between enforcing a contract and satisfying the user's actual intent, expose the contract defect rather than pretending the two are equivalent.

When there is tension between restarting everything and repairing a specific deficiency, repair the deficiency.

**Strategerium exists to define success before work begins, preserve freedom during execution, and require proof before declaring the work complete.**
