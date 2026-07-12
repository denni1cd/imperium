# Deliberation Lifecycle

## Status

**Approved — protocol version 1.3, 2026-07-12.**

The authoritative machine-readable contract is [`../config/protocol.yaml`](../config/protocol.yaml). Stage prompts are stored in [`../prompts/`](../prompts/).

- Protocol 1.1 introduced advocate-authored challenge turns.
- Protocol 1.2 clarified conditional challenge outputs, evidence cardinality, halt behavior, and canonical challenge storage.
- Protocol 1.3 clarified that newly requested evidence is resolved only after the current challenge phase and therefore cannot justify another round inside that same phase.

## Governing Principle

Imperium controls what each member sees, which artifacts cross each boundary, and what validated output is required before the lifecycle advances. It is a deliberation state machine, not an unrestricted shared-agent chat.

## Authority Hierarchy

When priorities conflict, the council respects this order:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty;
5. member values and doctrines.

Members may challenge whether a proposed means will achieve the user's broader intent. They may not silently replace the user's priorities.

## Approved Lifecycle

### 1. Preserve the Sovereign Request

**Transition:** `created` → `request_preserved`  
**Owner:** engine

Preserve the original request, goals, constraints, prohibitions, supplied facts, and relevant context without strategic reinterpretation.

### 2. Select the Fixed Council

**Transition:** `request_preserved` → `council_selected`  
**Owner:** engine

Snapshot the approved council. Select the four fixed advocates and the non-advocating Seneschal. Dynamic selection remains deferred.

### 3. Independent Interpretation

**Transition:** `council_selected` → `interpretations_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/interpretation.md`

Each advocate receives only:

- the preserved request;
- its own approved profile snapshot;
- facts supplied in the request.

It receives no other profile, interpretation, proposal, synthesis, or Seneschal opinion.

Each advocate produces one validated `Interpretation` with the core decision, desired outcome, opportunities, risks, assumptions, missing information, initial inclination, material value influence, and confidence.

### 4. Compare Frames and Normalize Claims

**Transition:** `interpretations_complete` → `frames_compared`  
**Owner:** Seneschal  
**Prompt:** `prompts/compare_frames.md`

The Seneschal compares blind interpretations without proposing a strategy. It produces:

- one frame-phase `ClaimRegister`;
- one `FrameRegister` preserving shared, contested, and unique frames and separating factual, interpretive, and value disagreement.

Normalization preserves source wording, artifact and member IDs, material conditions, dependencies, confidence, and minority formulations.

### 5. Challenge Frames

**Transition:** `frames_compared` → `frame_challenges_complete`  
**Coordinator:** Seneschal  
**Participants:** assigned advocates  
**Prompts:** `prompts/challenge_frames.md`, `prompts/author_challenge.md`, `prompts/respond_challenge.md`

Each round contains:

1. **Selection:** the Seneschal produces and validates a bounded `ChallengePlan`.
2. **Authored challenge:** each assigned challenger produces its own `ChallengeArtifact`.
3. **Target response:** each assigned target defends, refines, concedes, withdraws, or requests evidence.
4. **Round decision:** the Seneschal stops or authorizes one additional bounded round after all assignments are complete.

The Seneschal may select, route, and validate. It may not author either advocate's contribution.

A challenge stage always produces one plan and one continuation or stopping decision. A plan with N assignments produces exactly N challenges and N responses. An empty plan produces zero of each and explains why no material target exists.

### 6. Resolve Frame Evidence

**Transition:** `frame_challenges_complete` → `evidence_resolved` only when the session may continue  
**Owner:** engine and authorized evidence source

Evidence is resolved after frame debate, not between rounds of that debate.

- zero requests produce zero resolutions;
- N requests produce exactly N resolutions;
- each request ID is resolved exactly once;
- duplicate, missing, and orphan resolutions are invalid.

Allowed outcomes:

- gathered evidence;
- user clarification required;
- proceed conditionally;
- deliberation paused.

User clarification sets `waiting_for_user`; pause sets `paused`. Neither status may advance. Gathered and conditional outcomes may advance only with explicit provenance, assumptions, uncertainty, bounds, and reconsideration triggers as applicable.

Resolved frame evidence informs strategy development but does not rewrite blind interpretations or reopen frame debate in protocol 1.3.

### 7. Develop Independent Strategies

**Transition:** `evidence_resolved` → `strategies_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/proposal.md`

Each advocate receives the deliberately disclosed frame record, challenge exchange, and resolved frame evidence, then produces one complete `StrategyProposal`.

Every proposal states actions, benefits, assumptions, tradeoffs, risks, sacrifices, triggers, reconsideration conditions, and confidence.

### 8. Challenge Proposals

**Transition:** `strategies_complete` → `proposal_challenges_complete`  
**Coordinator:** Seneschal  
**Participants:** assigned advocates  
**Prompts:** `prompts/challenge_proposals.md`, `prompts/author_challenge.md`, `prompts/respond_challenge.md`

The Seneschal normalizes controlling proposal claims, then applies the same conditional challenge-turn and ownership rules used for frame debate.

Targets may include assumptions, forecasts, actions, costs, dependencies, burdens, risks, tradeoffs, or reconsideration conditions.

### 9. Resolve Proposal Evidence

**Transition:** `proposal_challenges_complete` → `proposal_evidence_resolved` only when the session may continue  
**Owner:** engine and authorized evidence source

Proposal evidence requests are resolved after proposal debate and before revisions. They cannot be introduced between proposal debate rounds under protocol 1.3.

The same exact cardinality and gathered, conditional, waiting, and pause behavior applies.

### 10. Revise Positions

**Transition:** `proposal_evidence_resolved` → `revisions_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/revision.md`

Each advocate produces one complete `Revision` recording:

- the changed or deliberately retained proposal;
- reasons;
- responsible challenge, evidence, or reasoning;
- concessions;
- unresolved disagreements;
- new risk, sacrifice, or uncertainty;
- expected strategic effect;
- final confidence.

A reasoned retention uses the same artifact with a materially unchanged complete proposal. Performative movement is invalid.

### 11. Seneschal Adjudication

**Transition:** `revisions_complete` → `adjudicated`  
**Owner:** Seneschal  
**Prompt:** `prompts/adjudication.md`

The Seneschal selects or constructs the strongest strategy. It must:

- identify decisive reasons;
- preserve accepted frames;
- explain why major alternatives lost, were incorporated, or remain minority objections;
- seek a coherent hybrid when it improves the strategy;
- explain why no hybrid is superior when selecting one revised strategy substantially intact;
- preserve serious objections and reconsideration triggers;
- state assumptions, uncertainty, confidence, and actions requiring user authorization.

Majority support, rhetorical force, or compromise is not sufficient justification.

### 12. Produce the Actionable Plan

**Transition:** `adjudicated` → `plan_complete`  
**Owner:** Seneschal  
**Prompt:** `prompts/actionable_plan.md`

The final plan includes:

- decision and objective;
- immediate next action;
- ordered steps;
- owners where relevant;
- dependencies and completion signals;
- checkpoints;
- risks and mitigations;
- assumptions;
- decision triggers;
- stop, exit, and reconsideration conditions.

A serious surviving objection must remain visible wherever it changes execution or reconsideration.

## Challenge Assignment Policy

Challenges are ranked by:

1. conflict with user authority or objectives;
2. expected effect on the recommendation;
3. unsupported controlling facts, assumptions, or forecasts;
4. severe downside, irreversibility, or missing recovery path;
5. breadth of independent disagreement;
6. fit with a declared counterweight;
7. stable artifact, claim, and member-order tie-breaks.

Bounds:

- no more than four assignments per round;
- no advocate receives more than two primary challenges per round;
- no self-challenge;
- counterweights are preferred when relevant;
- overrides require reasons;
- repeated challenges require a revised claim or other materially new input already permitted within the phase;
- low-materiality claims are not challenged merely for completeness.

## Debate-Round Ordering

One additional round is permitted only when:

- a high or critical issue remains unresolved;
- the completed exchange exposed a new material frame, a materially revised claim, or a follow-up that could change adjudication;
- a specific next challenge is identified;
- the next challenge is not repetition without new phase-permitted input.

A decision-critical evidence request ends the challenge phase and routes to the next evidence-resolution transition. Newly resolved evidence informs strategies or revisions; it does not feed a second round of the phase that created the request.

The phase stops when:

- no material issue remains;
- objections repeat without new input;
- user clarification is required;
- responsible deliberation must pause;
- the phase is complete;
- the two-round safety limit is reached.

The safety limit never silently discards unresolved issues.

## Canonical Challenge Record

`ProtocolTrace.challenges` is the sole canonical store for advocate-authored challenge artifacts. The legacy `DeliberationRecord.challenges` field must remain empty and is rejected during record validation if populated.

## Change Control

Changes to lifecycle stages, visibility, challenge materiality, assignment, continuation, evidence ordering, evidence cardinality, halt behavior, stopping, or canonical record ownership require a protocol version increment, regression tests, migration consideration, and explicit user approval.
