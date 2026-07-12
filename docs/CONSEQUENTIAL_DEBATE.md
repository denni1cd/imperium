# Consequential Debate

## Status

**Approved — protocol version 1.3, 2026-07-12.**

Protocol 1.1 added advocate-authored challenge turns. Protocol 1.2 clarified conditional challenge artifacts, evidence cardinality, halt behavior, and canonical challenge ownership. Protocol 1.3 clarifies that newly requested evidence is resolved after the current challenge phase and cannot justify another round inside that same phase.

## Core Rule

A debate contribution is useful only when it changes the decision state, clarifies a material uncertainty, strengthens a justified position, or improves the resulting actionable plan.

Change alone is not success. A concession, revision, hybrid, or retained position counts only when its reason is explicit and the result improves the decision or represents uncertainty more honestly.

## Required Multi-Turn Structure

For each nonempty assignment:

1. the Seneschal selects a bounded target;
2. the assigned challenger authors its own `ChallengeArtifact`;
3. the assigned target answers that exact challenge;
4. the exchange can affect continuation, evidence routing, revision, adjudication, or the final plan.

The Seneschal coordinates but does not impersonate either advocate.

An empty challenge plan is valid when it explains why no material target exists. It produces no challenge or response artifacts.

## Materiality

- **Low:** unlikely to change a meaningful part of the recommendation.
- **Medium:** could change a tradeoff, mitigation, sequence, or bounded plan element.
- **High:** could change the preferred strategy, immediate next action, major commitment, or important condition.
- **Critical:** could violate user authority or expose the user to severe, irreversible, or irresponsible consequences.

Low claims are not challenged merely to create activity. A second debate round requires an unresolved high or critical issue.

## Consequential Events

A contribution is consequential when it records decision impact and produces at least one of:

- a newly recognized material frame;
- an exposed hidden or unsupported assumption;
- separation of factual, interpretive, and value disagreement;
- a materially strengthened defense;
- a refined or narrowed claim;
- a concession or withdrawal;
- an evidence request routed to a defined outcome;
- a changed strategy;
- a stronger hybrid strategy;
- a preserved serious minority objection;
- a reasoned confidence change;
- a safer or more executable plan;
- a justified decision to retain a challenged position.

## Required Revision Record

Every advocate `Revision` records:

- the original proposal ID;
- the complete revised or retained proposal;
- changes, which may be empty for justified retention;
- reasons and responsible challenge, evidence, or reasoning;
- expected strategic effect;
- new risk, sacrifice, or uncertainty;
- concessions and unresolved disagreement;
- final confidence.

Revision ownership must remain consistent across the revision, original proposal, and revised proposal.

Whether a change was beneficial, neutral, or harmful is an experiment judgment and must not be inferred merely from movement.

## Challenge Quality

Every challenge must:

- match a valid assignment;
- identify a normalized claim and source artifact;
- come from the assigned challenger;
- explain materiality and expected consequence;
- fit a declared counterweight or explain the override;
- avoid repetition without materially new phase-permitted input.

Every target response must:

- come from the assigned target;
- answer the authored challenge;
- defend, refine, concede, withdraw, or request evidence;
- provide any revised claim or evidence request required by its disposition.

## Conditional Cardinality

Every challenge stage contains one plan and one continuation or stopping decision.

A plan with N assignments contains exactly:

- N authored challenges;
- N target responses.

An empty plan contains zero of each.

Evidence stages contain exactly one resolution per request, including the valid zero-request and zero-resolution case.

## Evidence Ordering

Evidence requests created during a challenge phase are resolved in the following evidence-resolution lifecycle transition.

They do not provide newly resolved evidence to another round inside the phase that created them.

Another same-phase round may proceed only from:

- a new material frame exposed by the completed exchange;
- a materially revised or narrowed claim;
- another specific follow-up using information already permitted in that phase that could change adjudication.

A decision-critical evidence request ends the challenge phase and informs:

- later strategy development after frame evidence resolution; or
- later advocate revision after proposal evidence resolution.

Allowed evidence outcomes remain gathered, user clarification, conditional planning, and pause. Waiting and paused outcomes prevent lifecycle advancement.

## Non-Contributions

The following do not count as meaningful debate by themselves:

- agreement without new reasoning;
- paraphrasing another position;
- generic caution without decision impact;
- attacks on tone or identity;
- repeated objections without new input;
- disagreement that affects no claim, proposal, uncertainty, or adjudication;
- theatrical hostility;
- revision made only to demonstrate movement;
- weak compromise presented as synthesis;
- evidence requests without decision impact or a valid route;
- forced challenges;
- confidence changes without reasons.

## Hybrid Strategy Test

A meaningful hybrid:

1. incorporates compatible strengths from more than one proposal;
2. resolves or explicitly bounds a material conflict;
3. produces one coherent course of action;
4. explains remaining sacrifices and assumptions;
5. converts cleanly into the actionable-plan contract.

A summary, average, vote, or compromise is not automatically a hybrid.

Adjudication must either construct a justified hybrid or explain why no hybrid improves on the chosen revised strategy.

## Minority Objection Preservation

A serious minority objection remains traceable through:

- its source interpretation or proposal;
- related challenges and responses;
- the advocate's final revision;
- adjudication;
- the user-facing export;
- relevant plan assumptions, risks, mitigations, triggers, or reconsideration conditions.

Internal preservation alone is insufficient when the objection changes execution or reconsideration.

## Canonical Records

`ProtocolTrace.challenges` is the sole canonical collection of advocate-authored challenges. The legacy `DeliberationRecord.challenges` field must remain empty.

Stage 4 may add execution and context lineage but must distinguish process traceability from claims of strategic improvement.

## Automated Measurements

The system can measure:

- normalized claims and materiality;
- distinct frames and proposals;
- challenge assignments by phase and round;
- challenge and response completion per assignment;
- response dispositions;
- rejected repetitions;
- evidence requests, outcomes, and halt status;
- revisions and reasons;
- continuation and stopping reasons;
- preserved objections;
- model calls, tokens, latency, and retries;
- actionable-plan field completion.

These measurements describe process. They do not prove strategic improvement.

## Human or Model-Assisted Evaluation

Blinded evaluation is required for whether:

- perspectives are genuinely distinct;
- a challenge exposed an important issue;
- a revision improved the strategy;
- a hybrid is coherent and stronger;
- the final plan is strategically sound and actionable;
- objections were handled responsibly;
- added deliberation justified its cost.

## Minimum Success Test

Full deliberation must outperform both independent profiled advisers without debate and a roughly equivalent-budget single adviser using structured self-critique.

If debate adds ceremony but not strategic value, the protocol must be revised before more architecture is added.

## Change Control

Changes to debate materiality, assignment, challenge cardinality, evidence ordering, evidence cardinality, halt behavior, continuation, stopping, canonical record ownership, or measurement require a protocol version increment, regression tests, migration consideration, and explicit user approval.
