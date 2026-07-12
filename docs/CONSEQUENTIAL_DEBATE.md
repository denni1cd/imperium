# Consequential Debate

## Status

**Approved — protocol version 1.2, 2026-07-12.**

This document defines what debate must change, how the effect is recorded, and when discussion is strategically useless. Protocol 1.1 added advocate-authored challenge turns. Protocol 1.2 clarified conditional challenge artifacts, evidence cardinality, halt behavior, and canonical challenge ownership.

## Core Rule

A debate contribution is useful only when it changes the decision state, clarifies a material uncertainty, strengthens a justified position, or improves the resulting actionable plan.

Change alone is not success. A concession, revision, hybrid, or retained position counts only when its reason is explicit and the result improves the decision or represents uncertainty more honestly.

## Required Multi-Turn Structure

A challenged claim is not debated merely because the Seneschal describes an objection and summarizes a response.

For each nonempty assignment:

1. the Seneschal selects the bounded target;
2. the assigned challenger authors its own `ChallengeArtifact`;
3. the assigned target answers that exact challenge;
4. the exchange can affect evidence, continuation, revision, adjudication, or the final plan.

The Seneschal coordinates but does not impersonate either advocate.

An empty challenge plan remains valid when it explains why no material target exists. It produces no challenge or response artifacts.

## Materiality

Every normalized claim and challenge uses one of four levels:

- **Low:** unlikely to change a meaningful part of the recommendation or plan.
- **Medium:** could change a tradeoff, mitigation, sequencing choice, or bounded component of the plan.
- **High:** could change the preferred strategy, immediate next action, major commitment, or important condition.
- **Critical:** could make the strategy violate user authority, become irresponsible, or expose the user to severe or irreversible consequences.

Low claims are not challenged merely to create activity. A second debate round requires at least one unresolved high or critical claim.

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

Every advocate `Revision` records:

- the original proposal identifier;
- the complete revised proposal or complete retained proposal;
- changes, which may be empty for justified retention;
- the challenge, evidence, or reasoning responsible;
- the expected strategic effect;
- any new risk, sacrifice, or uncertainty;
- concessions;
- unresolved disagreement;
- final confidence.

Revision ownership must remain consistent: the revision member, original proposal owner, and revised proposal member are the same advocate.

The Seneschal later records whether the change contributed to adjudication. Whether it was beneficial, neutral, or harmful is an experiment judgment and must not be inferred merely from movement.

## Challenge Quality Requirements

Every authored challenge must:

- match a valid assignment;
- identify a normalized claim and source artifact;
- come from the assigned challenger rather than the Seneschal;
- explain why the claim is material;
- identify the consequence expected from a useful response;
- fit a declared counterweight or explain the override;
- avoid repeating an answered claim without new evidence or revision.

Every target response must:

- come from the assigned target;
- answer the actual authored challenge;
- defend, refine, concede, withdraw, or request evidence;
- include the revised claim or evidence request required by its disposition.

## Conditional Debate Cardinality

A challenge stage always contains one plan and one continuation or stopping decision.

If the plan contains N assignments, the round contains exactly:

- N authored challenges;
- N target responses.

If the plan is empty, both counts are zero. Synthetic artifacts created only to satisfy a schema are invalid.

## Evidence Consequences

Every evidence request terminates in exactly one outcome:

- gathered evidence;
- user clarification required;
- proceed conditionally;
- deliberation paused.

Zero requests produce zero resolutions. N requests produce N resolutions. Orphan or duplicate resolutions are invalid.

User clarification and pause outcomes halt lifecycle advancement while preserving the session. Conditional planning proceeds only with explicit assumptions, bounds, and reconsideration triggers.

Stage 4 gathered evidence must identify synthetic fixture or replay provenance. It must not imply that live research occurred.

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

A summary, average, vote, or compromise is not automatically a hybrid.

Adjudication must either construct a justified hybrid or explain why no hybrid improves on the chosen revised strategy.

## Minority Objection Preservation

A serious minority objection must remain traceable through:

- the source interpretation or proposal;
- any challenge and response;
- the advocate's final revision;
- Seneschal adjudication;
- the user-facing export;
- relevant plan assumptions, risks, mitigations, triggers, or reconsideration conditions.

Internal preservation alone is insufficient when the objection changes how the user should execute or reconsider the plan.

## Canonical Records

`ProtocolTrace.challenges` is the sole canonical collection of advocate-authored challenge artifacts.

The legacy `DeliberationRecord.challenges` field must remain empty. Maintaining two independently writable challenge histories is invalid.

Stage 4 may add execution and context lineage around the strategic artifacts, but the trace must distinguish routing evidence from claims of strategic improvement.

## Automated Measurements

The system can measure reliably:

- number and materiality of normalized claims;
- number of distinct frames and proposals;
- challenge assignments by phase and round;
- authored challenge and response completion per assignment;
- defenses, refinements, concessions, withdrawals, and evidence requests;
- repeated challenges rejected for lack of new input;
- evidence outcomes and halt status;
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
- plan elements attributed to debate;
- debate calls and token use;
- unresolved high or critical issues.

The Stage 3 `ProtocolTrace` preserves the strategic artifacts needed for this report. Stage 4 attaches execution, context, and plan lineage to the complete offline session.

## Minimum Success Test

The full debate process must outperform both:

- independent profiled advisers without debate; and
- a roughly equivalent-budget single adviser using structured self-critique.

It must do so often enough, and by enough strategic value, to justify its additional cost and complexity.

If debate does not improve the output beyond independent collection or self-critique, the protocol must be revised before more architecture is added.

## Failure Signals

The protocol should be reconsidered when testing shows:

- most challenge plans are empty or target only wording differences;
- advocates repeatedly collapse into generic consensus;
- second rounds rarely change adjudication;
- revisions are predominantly neutral or harmful;
- the Seneschal rewards voting or compromise rather than decisive reasoning;
- important human or stakeholder consequences are repeatedly missed;
- the final plan becomes less actionable as deliberation grows;
- the additional inference cost is not matched by strategic improvement.

## Change Control

Changes to debate materiality, assignment, challenge cardinality, evidence cardinality, halt behavior, continuation, stopping, canonical record ownership, or measurement rules require a protocol version increment, regression tests, migration consideration, and explicit user approval.
