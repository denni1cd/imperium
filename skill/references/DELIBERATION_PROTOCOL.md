# Deliberation Protocol

This document records the accepted minimum Imperial Council lifecycle. It is subordinate to `MANIFESTO.md` and should be implemented as instructions before infrastructure.

## 1. Sovereign invocation

The Sovereign explicitly convenes the Council. There is no automatic routing into Council deliberation in v1.

## 2. Independent counsel

Each participating councillor receives:

- the Sovereign's original request;
- identical shared factual context;
- only that councillor's persistent profile and private instructions.

No councillor may receive another member's proposal, interpretation, recommendation, or private context before every initial proposal is complete.

Each councillor produces a complete initial strategic proposal.

### Rules Lawyer gate

Before disclosure begins, the Rules Lawyer verifies that every required independent proposal exists and that the independence boundary was preserved.

If the gate fails, disclosure does not begin. The incomplete or invalid prior stage is resumed and corrected.

## 3. Full disclosure

After every initial proposal is complete, the chamber opens.

Every councillor receives:

- every other councillor's complete initial proposal;
- the shared context;
- the complete evolving Council record from this point onward, with compression permitted only when no material argument, concession, evidence item, unresolved issue, or position change is lost.

The Seneschal must not replace full initial proposals with summaries or pre-select the permissible debate agenda.

## 4. Opening Council

Each councillor independently decides what deserves engagement after reading the full proposals.

Members may challenge, support, defend, extend, distinguish, concede, revise, combine, or synthesize arguments as warranted.

Agreement may produce reinforcement or alliance. Disagreement may be cross-cutting rather than binary.

## 5. Open debate

Debate is natural rather than ticket-driven. Councillors receive the material Council state needed to understand and answer live arguments.

Debate continues only while new material reasoning is being added, including:

- unanswered consequential arguments;
- new evidence;
- unresolved assumptions;
- meaningful modifications;
- or new syntheses that could change the strategy.

Repetition of a known preference is not sufficient reason to continue.

A direct material challenge remains open until the challenged councillor answers it, concedes it, demonstrates that its premise is false, or explains why no additional material answer exists.

Councillors should challenge not only each other's strategies and evidence, but also shared decision criteria or assumptions that emerge during debate when those criteria materially shape the Council's judgment.

Research may continue during debate when a disputed factual claim or live uncertainty warrants verification.

## 6. Persistent councillor state

A councillor is a persistent strategic identity and position state, not a persistent runtime process.

A fresh delegated worker may represent a councillor when supplied with sufficient state to continue that councillor faithfully.

Persistent state includes at minimum:

- immutable profile and value matrix;
- immutable original proposal;
- current recommendation;
- current rationale;
- accepted and rejected arguments;
- unresolved concerns;
- concessions and revisions;
- causal reason for material position changes;
- evidence relied upon and its source/confidence where relevant;
- disputed factual claims;
- open research questions;
- previous public statement when useful.

A fresh worker must treat current state as the starting judgment rather than reconsidering from scratch.

A material recommendation change requires a causal bridge identifying:

1. the new argument, evidence, or synthesis causing the change;
2. the previous assumption or rationale defeated or modified;
3. why the new position is superior;
4. why the revision remains consistent with the councillor's persistent values.

Unexplained stochastic drift is not a valid Council state change. Conversely, persistent state must not prevent rational mind-changing when stronger evidence or reasoning warrants it.

## 7. Call for vote

Any councillor may call for a vote when they believe further discussion is no longer materially improving the decision.

Each member receives one opportunity to identify specific unfinished material reasoning.

If none exists, debate may close.

If a member claims unfinished material reasoning, the Council votes by simple majority on whether another exchange is warranted. The Seneschal breaks a procedural tie.

### Rules Lawyer gate

Before a strategic ballot begins, the Rules Lawyer verifies that:

- every councillor received the unfinished-business opportunity;
- every material direct challenge is resolved or explicitly preserved as unresolved;
- no required causal bridge or state update is missing;
- the surviving strategies are clearly identified.

If the gate fails, the Council returns to the prior debate stage and completes the missing work.

## 8. Strategic decision

A Council session terminates through one of three paths:

1. convergence;
2. synthesis;
3. decision by vote.

When a strategy vote is required, councillors vote on the surviving strategies produced by the debate, not necessarily their own initial proposals.

A strategy wins only with **strictly more than 50% of the votes cast by participating councillors**.

For four councillors, two votes are exactly 50% and are **not** a majority.

If more than two alternatives remain and none receives a strict majority, lower-supported alternatives are eliminated and a runoff is held. If multiple alternatives tie for lowest support and eliminating all of them would bypass the strict-majority requirement, the Seneschal resolves only that elimination tie from the complete deliberative record by selecting one tied-lowest alternative for elimination. This authority may not be used to declare a winner; the remaining alternatives proceed to another ballot. If two alternatives remain tied, the Seneschal resolves the final tie from the complete deliberative record and must not invent a compromise merely to resolve it.

### Rules Lawyer ballot check

After every ballot, and before any result is declared, the Rules Lawyer independently verifies:

- number of participating councillors;
- number of valid votes cast;
- vote totals for each surviving strategy;
- whether any strategy actually exceeds the required majority threshold;
- whether a runoff or Seneschal tie-break is required.

The Rules Lawyer reports only procedural validity. It has no vote and may not recommend a strategy.

If the ballot is invalid or the result is calculated incorrectly, no decision is declared. The ballot stage is corrected and completed.

## 9. Unified plan

The Seneschal converts the decided strategy into one official Council plan containing:

1. Council decision;
2. why the strategy won;
3. sequenced action plan;
4. critical assumptions and tradeoffs;
5. decision/change triggers;
6. meaningful minority objections.

The result must not return several competing official recommendations.

## 10. Fidelity review

Councillors may review the drafted final plan only to identify concrete inconsistencies with the strategy actually decided.

A losing member may not reopen settled strategic disagreement solely because they still prefer another option.

### Rules Lawyer final gate

Before the Council presents the final plan as complete, the Rules Lawyer verifies procedural completeness, including:

- a valid decision path exists;
- the declared winner matches the valid vote or convergence/synthesis record;
- required councillor state transitions are persisted;
- required minority objections are preserved;
- required deliberative artifacts are present;
- the Council is not claiming completion while a mandatory protocol item is missing.

If the final gate fails, the Council returns to the stage where the omission occurred and completes it before finalization.

## Rules Lawyer role

The Rules Lawyer is an independent procedural gate guardian.

It is **not** a councillor, strategist, debate participant, or substitute Seneschal.

The Rules Lawyer:

- has no strategic values matrix;
- has no vote;
- does not advocate for or against any strategy;
- does not decide what arguments are persuasive;
- does not synthesize the final plan;
- does not pre-frame the Sovereign's problem;
- validates only compliance with explicit Council protocol and stage-completion requirements.

The Rules Lawyer should be invoked at protocol gates rather than continuously during every conversational turn. A fresh disposable worker is sufficient because it has no strategic identity or prior position to preserve.

When it finds an error, the consequence is deterministic: **the Council does not advance. The previous stage is resumed and completed or corrected.**

## Governing authority split

- **Sovereign:** decides when to convene and retains final human authority.
- **Councillors:** own the reasoning, research, and debate.
- **Seneschal:** owns orchestration, debate closure, final tie-breaking where authorized, and coherent synthesis.
- **Rules Lawyer:** independently validates procedural gates and prevents advancement when protocol requirements are incomplete or invalid.
