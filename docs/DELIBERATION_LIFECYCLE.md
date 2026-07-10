# Deliberation Lifecycle

## Status

**Draft based on accepted discussion.** The sequence is agreed in outline but still requires exact data contracts, prompts, and stopping rules.

## Governing Principle

The system must control what each member sees and when. Imperium is a deliberation process, not an unrestricted shared agent chat.

## Authority Hierarchy

When priorities conflict, the council must respect the following order:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty;
5. council-member values and doctrines.

Members may challenge whether a stated objective will achieve the user's broader intent. They may not silently replace the user's priorities with their own.

## Proposed Lifecycle

### 1. Preserve the Sovereign Request

Store the original request, explicit goals, constraints, prohibitions, supplied facts, and relevant context without strategic reinterpretation.

### 2. Select the Council

Choose the smallest set of members capable of providing relevant and meaningfully different perspectives. The user may directly select or exclude members.

The selection process must not pre-frame the problem for the chosen members.

For the first validation experiments, use a fixed, user-approved roster so council selection does not become an uncontrolled variable.

### 3. Independent Interpretation

Each selected member receives the original request and permitted shared context, but no other member's interpretation.

Each member independently identifies:

- the decision it believes is being made;
- the desired outcome;
- important opportunities and risks;
- hidden assumptions and missing information;
- its initial strategic inclination.

### 4. Compare Frames

Collect the independent interpretations and identify:

- shared frames;
- conflicting frames;
- unique frames;
- factual disagreements;
- interpretive disagreements;
- value disagreements.

Multiple valid frames should remain visible rather than being prematurely collapsed into one summary.

### 5. Challenge Frames

Assign targeted challenges to interpretations or assumptions that could materially change the decision. The challenged member must defend, refine, concede, withdraw, or request evidence.

### 6. Resolve Evidence Needs

Every request for evidence must identify:

- the disputed claim or uncertainty;
- why it matters to the decision;
- what information would resolve or narrow it;
- whether the source should be the user, external research, or existing context.

The request must produce one of four outcomes:

1. evidence is gathered and added to the shared factual record;
2. the user is asked for decision-critical information;
3. the council proceeds under explicit uncertainty with conditional recommendations;
4. deliberation pauses because responsible planning is not possible without the missing information.

Evidence gathered after independent interpretation must not retroactively rewrite those initial submissions. It informs later strategy and revision stages.

### 7. Develop Independent Strategies

After frame challenges and evidence resolution are visible, each member develops its own proposed strategy. Proposals must identify expected benefits, assumptions, tradeoffs, risks, sacrifices, and reconsideration conditions.

### 8. Debate Proposals

Extract decisive claims and assign targeted challenges. Members should attack material assumptions, consequences, and tradeoffs rather than personalities or wording.

New decision-critical evidence requests follow the same resolution rules as Stage 6.

### 9. Revise Positions

Each member submits a final position that records:

- what changed;
- why it changed;
- the evidence or reasoning that caused the change;
- concessions and unresolved disagreements;
- the expected effect on the resulting strategy;
- remaining confidence.

A member may retain its original position when challenges do not justify a change.

### 10. Seneschal Adjudication

The Seneschal evaluates the complete record and selects or constructs the strongest strategy. The adjudication must preserve meaningful minority objections and explain why major alternatives lost.

The Seneschal must distinguish between:

- an advocate's recommendation;
- the council's final strategic judgment;
- actions that require user authorization.

### 11. Produce an Actionable Plan

The final output must include, where relevant:

- the decision and intended objective;
- the immediate next action;
- ordered steps;
- responsible owner or party;
- prerequisites and dependencies;
- checkpoints or milestones;
- principal risks and mitigations;
- assumptions that must remain true;
- decision triggers;
- stop, exit, or reconsideration conditions.

A strategically insightful explanation without concrete next steps is not a complete Imperium result.

## Recommendation and Action Boundary

- Council members advocate.
- The Seneschal adjudicates.
- The final plan recommends actions.
- The user authorizes consequential actions.
- Any future executor may perform only actions within explicitly granted authority.

No council member gains operational authority merely because it argued forcefully for a course of action.

## Required Deliberation Record

Each session must preserve at least:

- the original request and explicit constraints;
- the selected council and selection basis;
- independent interpretations;
- the frame register;
- challenges and responses;
- evidence requests, sources, and outcomes;
- initial strategies;
- revisions, concessions, and reasons for change;
- unresolved minority objections;
- the Seneschal's adjudication;
- the final actionable plan;
- available cost and debate-effect metrics.

The record must make it possible to determine whether debate materially improved the decision rather than merely adding dialogue.

## Information Boundaries

- Members see the raw request before any council interpretation.
- Initial interpretations are blind and independent.
- Later visibility is deliberate and stage-specific.
- No member should receive the full transcript merely because it exists.
- The Seneschal receives the full record only when required for coordination or adjudication.

## Stopping Principle

Debate should stop when additional discussion no longer introduces a material frame, changes a claim, produces justified revision, improves the plan, resolves a decision-critical uncertainty, or changes the adjudication.

## Open Questions

- Which stages can be omitted for simple decisions?
- How many challenges should be assigned in the minimum viable protocol?
- Who extracts and normalizes claims?
- What objective signal ends a debate round?
- What threshold makes missing information important enough to ask the user rather than proceed conditionally?
- Which actions should always require explicit confirmation if execution capabilities are added later?