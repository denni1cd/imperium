# Consequential Debate

## Status

**Open design item.** This document defines how Imperium will distinguish strategic disagreement from debate-shaped theater.

## Core Rule

A debate contribution is useful only when it changes the decision state, clarifies a material uncertainty, or improves the resulting plan.

Change alone is not success. A revision, concession, or hybrid strategy counts only when the reasoning for the change is explicit and the change is judged to improve the decision or make its uncertainty more honest.

## Consequential Events

A challenge or response is consequential when it produces at least one of the following:

- a newly recognized interpretation of the problem;
- exposure of a hidden or unsupported assumption;
- clarification of a factual, interpretive, or value disagreement;
- defense that materially strengthens a claim;
- refinement or narrowing of a claim;
- explicit concession or withdrawal;
- a request for evidence that identifies a decision-critical uncertainty and leads to a defined resolution path;
- modification of a proposed strategy;
- creation of a stronger hybrid strategy;
- preservation of a serious minority objection;
- a change in confidence supported by reasoning;
- a more concrete or executable final plan.

## Required Change Record

Every material change must record:

- the original position or claim;
- the revised position or claim;
- the challenge, evidence, or reasoning that caused the change;
- the expected strategic benefit of the change;
- any new risk, sacrifice, or uncertainty introduced;
- whether the Seneschal judged the change beneficial, neutral, or harmful.

Members are not required to change their positions when the challenge does not justify it. A well-defended unchanged position may be more valuable than a performative concession.

## Non-Contributions

The following do not count as meaningful debate by themselves:

- agreement without additional reasoning;
- paraphrasing another member's position;
- generic cautions that have no consequence;
- attacks on tone, style, or personality;
- repeated objections that have already been answered;
- disagreement that never affects a claim, proposal, or adjudication;
- theatrical hostility without strategic content;
- revision made only to demonstrate movement;
- compromise that weakens the plan without resolving a material conflict;
- requests for evidence that do not identify why the evidence matters or what happens next.

## Candidate Measurements

### Diversity Before Debate

- number of materially distinct frames;
- number of materially distinct proposed strategies;
- degree of value-vector separation among selected members;
- evidence that member differences correspond to their profiles rather than presentation style.

### Debate Effects

- assumptions exposed;
- claims defended, refined, conceded, or withdrawn;
- evidence requests resolved;
- strategies revised;
- hybrid strategies created;
- confidence changes with stated reasons;
- unresolved objections preserved;
- material changes judged beneficial, neutral, or harmful.

### Plan Improvement

- added specificity;
- clearer sequencing and ownership;
- identified dependencies and decision triggers;
- stronger risk mitigation;
- clearer exit or reconsideration conditions;
- improved alignment with the user's stated objective;
- human-rated actionability and strategic quality.

### Efficiency

- model calls and tokens used;
- debate contributions that produced no measurable change or clarification;
- improvement relative to the independent-panel baseline;
- improvement relative to an equivalent-budget single adviser.

Efficiency is a constraint and diagnostic, not the primary measure of success.

## Minimum Success Test

The full debate process should outperform both an independent panel and an equivalent-budget single adviser often enough, and by enough strategic value, to justify its additional cost and complexity.

If debate does not improve the output beyond collecting independent opinions or structured self-critique, the debate protocol must be revised before additional architecture is added.

## Open Questions

- Which measurements can be automated reliably?
- Which require blinded human judgment?
- How should hybrid strategies be distinguished from simple summaries?
- What threshold defines a material revision?
- How should valid but unchanged minority objections be scored?
- How should harmful or pressure-driven revisions be detected?
- How many test cases are needed before the protocol is considered promising?