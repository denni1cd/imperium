# Consequential Debate

## Status

**Approved — protocol version 1.0, 2026-07-12.**

This document defines what debate must change, how the effect is recorded, and when discussion is considered strategically useless.

## Core Rule

A debate contribution is useful only when it changes the decision state, clarifies a material uncertainty, strengthens a justified position, or improves the resulting actionable plan.

Change alone is not success. A concession, revision, or hybrid counts only when its reason is explicit and the result improves the decision or represents uncertainty more honestly.

## Materiality

Every normalized claim and challenge uses one of four levels:

- **Low:** unlikely to change a meaningful part of the recommendation or plan.
- **Medium:** could change a tradeoff, mitigation, sequencing choice, or bounded component of the plan.
- **High:** could change the preferred strategy, immediate next action, major commitment, or important condition.
- **Critical:** could make the strategy violate user authority, become irresponsible, or expose the user to severe or irreversible consequences.

Low claims are not challenged in the minimum protocol merely to create activity. A second debate round requires at least one unresolved high or critical claim.

## Consequential Events

A contribution is consequential when it produces at least one of the following and records its decision impact:

- a newly recognized material frame;
- exposure of a hidden or unsupported assumption;
- separation of factual, interpretive, and value disagreement;
- a defense that materially strengthens a claim;
- refinement or narrowing of a claim;
- explicit concession or withdrawal;
- decision-critical evidence routed to a defined outcome;
- modification of a proposed strategy;
- creation of a stronger hybrid strategy;
- preservation of a serious minority objection;
- a reasoned confidence change;
- a more specific, safer, or executable final plan;
- a justified decision to retain a challenged position.

## Required Change Record

Every advocate revision records:

- the original position or claim;
- the revised position or explicit decision to retain it;
- the challenge, evidence, or reasoning responsible;
- the expected strategic benefit;
- any new risk, sacrifice, or uncertainty;
- concessions;
- unresolved disagreement;
- final confidence.

The Seneschal then records whether the change was beneficial, neutral, or harmful to adjudication. This judgment is part of experiment analysis and must not be inferred merely from the fact that a revision occurred.

## Challenge Quality Requirements

Every challenge must:

- identify a normalized claim and source artifact;
- explain why the claim is material;
- identify the consequence expected from a useful response;
- come from another advocate;
- fit a declared counterweight or explain the override;
- avoid repeating an answered claim without new evidence or revision.

An empty challenge plan is valid when no material target exists and the reason is recorded.

## Non-Contributions

The following do not count as meaningful debate by themselves:

- agreement without new reasoning;
- paraphrasing another position;
- generic caution without decision impact;
- attacks on tone, style, personality, or thematic identity;
- objections already answered without new input;
- disagreement that never affects a claim, proposal, uncertainty, or adjudication;
- theatrical hostility;
- revision made only to demonstrate movement;
- compromise that weakens the plan without resolving a material conflict;
- evidence requests that do not identify why the evidence matters or what route follows;
- forced challenges assigned only because the protocol contains a debate stage;
- confidence changes without stated reasoning.

## Hybrid Strategy Test

A strategy is a meaningful hybrid only when it:

1. incorporates compatible strengths from more than one proposal;
2. resolves or explicitly bounds a material conflict between them;
3. produces a coherent course of action rather than a list of options;
4. explains which sacrifices and assumptions remain;
5. can be converted into the actionable-plan contract.

A summary, average, or compromise is not automatically a hybrid.

## Automated Measurements

The system can measure reliably:

- number and materiality of normalized claims;
- number of distinct frames and proposals;
- challenge assignments by phase and round;
- defenses, refinements, concessions, withdrawals, and evidence requests;
- repeated challenges rejected for lack of new input;
- evidence outcomes;
- proposal revisions and recorded reasons;
- continuation and stopping reasons;
- unresolved objections preserved;
- model calls, tokens, latency, and retries;
- completion of required actionable-plan fields.

These measurements describe the process. They do not prove strategic improvement.

## Human or Model-Assisted Evaluation

Blinded evaluation is required for:

- whether independent perspectives are genuinely distinct;
- whether a challenge exposed an important issue;
- whether a revision improved the strategy;
- whether a hybrid is coherent and stronger;
- whether the final plan is strategically sound and actionable;
- whether minority objections were handled responsibly;
- whether the added deliberation justified its cost.

Automated counts may support evaluation but may not substitute for these judgments.

## Debate-Effect Summary

Each completed session should eventually report:

- claims challenged by materiality;
- consequential outcomes by disposition;
- evidence requests and routes;
- proposals changed or retained;
- changes judged beneficial, neutral, or harmful;
- surviving minority objections;
- rounds continued and stopped, with reasons;
- plan improvements attributed to debate;
- debate calls and token use;
- unresolved high or critical issues.

The Stage 3 `ProtocolTrace` preserves the typed inputs needed for this report. Stage 4 will attach the trace to the complete offline session.

## Minimum Success Test

The full debate process must outperform both:

- independent profiled advisers without debate; and
- a roughly equivalent-budget single adviser using structured self-critique.

It must do so often enough, and by enough strategic value, to justify its additional cost and complexity.

If debate does not improve the output beyond independent collection or self-critique, the protocol must be revised before more architecture is added.

## Failure Signals

Stage 3 should be reconsidered when testing shows:

- most challenge plans are empty or target only medium-impact wording differences;
- advocates repeatedly collapse into generic consensus;
- second rounds rarely change adjudication;
- revisions are predominantly neutral or harmful;
- the Seneschal rewards compromise rather than decisive reasoning;
- important human or stakeholder consequences are repeatedly missed;
- the final plan becomes less actionable as deliberation grows;
- the additional inference cost is not matched by strategic improvement.

## Change Control

Changes to debate materiality, assignment, continuation, stopping, or measurement rules require a protocol version increment, regression tests, experiment migration consideration, and explicit user approval.
