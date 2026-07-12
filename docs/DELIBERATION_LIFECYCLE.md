# Deliberation Lifecycle

## Status

**Approved — protocol version 1.2, 2026-07-12.**

The authoritative machine-readable contract is [`../config/protocol.yaml`](../config/protocol.yaml). Stage-specific model instructions are stored in [`../prompts/`](../prompts/). Protocol 1.1 introduced advocate-authored challenge turns; protocol 1.2 clarified conditional challenge outputs, evidence cardinality, and halt behavior.

## Governing Principle

Imperium controls what each member sees, which artifacts may cross each boundary, and what validated output is required before the lifecycle advances. It is a deliberation state machine, not an unrestricted shared-agent chat.

## Authority Hierarchy

When priorities conflict, the council must respect this order:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty;
5. council-member values and doctrines.

Members may explicitly challenge whether a chosen means will achieve the user's broader intent. They may not silently replace the user's priorities.

## Approved Lifecycle

### 1. Preserve the Sovereign Request

**Transition:** `created` → `request_preserved`  
**Owner:** engine

Store the original request, goals, constraints, prohibitions, supplied facts, and relevant context without strategic reinterpretation.

The preserved request is the authoritative reference for later alignment checks.

### 2. Select the Fixed Council

**Transition:** `request_preserved` → `council_selected`  
**Owner:** engine

For initial validation, snapshot the approved council and select the four fixed advocates. The Seneschal is also snapshotted but is not an advocate.

Dynamic selection remains deferred because it could pre-frame the problem or confound the first experiments.

### 3. Independent Interpretation

**Transition:** `council_selected` → `interpretations_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/interpretation.md`

Each advocate receives only:

- the preserved sovereign request;
- its own approved profile snapshot;
- supplied facts already contained in the request.

It receives no other profile, interpretation, frame, proposal, synthesis, or Seneschal opinion.

Each advocate produces one validated `Interpretation` identifying the core decision, desired outcome, opportunities, risks, assumptions, missing information, initial inclination, material value influence, and confidence.

### 4. Compare Frames and Normalize Claims

**Transition:** `interpretations_complete` → `frames_compared`  
**Owner:** Seneschal  
**Prompt:** `prompts/compare_frames.md`

The Seneschal compares the completed blind interpretations without proposing a strategy.

It produces:

- one frame-phase `ClaimRegister`;
- one `FrameRegister` preserving shared, contested, and unique frames plus factual, interpretive, and value disagreements.

#### Claim Normalization Method

1. Preserve source wording, artifact ID, and member ID.
2. Represent one decision-relevant proposition per claim.
3. Split compound claims when components could be challenged independently.
4. Classify each claim as fact, assumption, interpretation, value judgment, forecast, proposed action, tradeoff, or risk.
5. Assign materiality according to expected effect on the recommendation.
6. Merge only claims asserting the same proposition under the same conditions.
7. Preserve materially different conditions, confidence, and minority formulations.
8. Record claim dependencies so challenges target controlling premises.

Normalization is for comparison and targeting. It must not erase genuine disagreement or convert majority support into truth.

### 5. Challenge Frames

**Transition:** `frames_compared` → `frame_challenges_complete`  
**Coordinator:** Seneschal  
**Challengers and respondents:** assigned advocates  
**Prompts:** `prompts/challenge_frames.md`, `prompts/author_challenge.md`, `prompts/respond_challenge.md`

The challenge stage contains four controlled operations inside one top-level lifecycle transition:

1. **Selection — Seneschal**
   - produce a bounded `ChallengePlan` targeting normalized claims that could materially change the decision;
   - identify challenger, target, source artifact, claim, materiality, reason, and expected consequence.
2. **Authored challenge — assigned challenger**
   - receive only its own profile, the assignment, and permitted target material;
   - produce its own typed `ChallengeArtifact`.
3. **Response — assigned target**
   - receive its own profile, the assignment, and the authored challenge;
   - defend, refine, concede, withdraw, or request evidence.
4. **Continuation — Seneschal**
   - evaluate completed exchanges;
   - stop or authorize one additional bounded round under the approved rule.

The Seneschal may select, route, and validate exchanges. It may not author either advocate's challenge or response.

#### Conditional Challenge Outputs

Every challenge stage always produces:

- one `ChallengePlan`;
- one `ContinuationDecision`.

For each nonempty assignment it additionally produces:

- exactly one `ChallengeArtifact` from the assigned challenger;
- exactly one `ChallengeResponse` from the assigned target.

An empty challenge plan is allowed only when it records why no material challenge exists. It produces zero challenge and response artifacts. Debate is never fabricated to satisfy a stage schema.

### 6. Resolve Frame Evidence

**Transition:** `frame_challenges_complete` → `evidence_resolved` only when the session may continue  
**Owner:** engine and authorized evidence source

Each evidence request must identify the disputed claim, decision impact, information needed, and preferred source.

Evidence output cardinality is exact:

- zero requests produce zero resolutions;
- each request produces exactly one `EvidenceResolution`;
- orphan and duplicate resolutions are invalid.

Routing rules:

- **Ask the user** when the missing information is a user-exclusive preference, constraint, supplied fact, or authorization issue and plausible answers materially change the plan.
- **Research externally** when the issue is factual, publicly resolvable, and decision-critical. Stage 4 uses only explicit fake or replay evidence sources; it does not perform live network research.
- **Proceed conditionally** when the uncertainty can be bounded with an explicit assumption and reconsideration trigger without severe or irreversible downside.
- **Pause** when responsible planning is impossible or proceeding could create severe, irreversible, or unauthorized consequences.

Session behavior:

- gathered evidence and valid conditional planning allow advancement;
- user clarification sets the session to `waiting_for_user` and prevents advancement;
- a pause sets the session to `paused` and prevents advancement;
- the request, unresolved issue, and checkpoint remain inspectable and resumable.

Evidence added here informs later stages but does not rewrite historical blind interpretations.

### 7. Develop Independent Strategies

**Transition:** `evidence_resolved` → `strategies_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/proposal.md`

Each advocate receives the deliberately disclosed frame record, authored challenges, responses, and resolved evidence, then produces one `StrategyProposal`.

Every proposal includes actions, benefits, assumptions, tradeoffs, risks, sacrifices, decision triggers, reconsideration conditions, and confidence.

Advocates remain responsive to evidence without optimizing for agreement.

### 8. Challenge Proposals

**Transition:** `strategies_complete` → `proposal_challenges_complete`  
**Coordinator:** Seneschal  
**Challengers and respondents:** assigned advocates  
**Prompts:** `prompts/challenge_proposals.md`, `prompts/author_challenge.md`, `prompts/respond_challenge.md`

The Seneschal first creates a proposal-phase `ClaimRegister`, then applies the same selection, authored-challenge, target-response, conditional-output, continuation, counterweight, and anti-repetition rules used during frame challenge.

Targets may include controlling assumptions, forecasts, actions, costs, dependencies, burdens, risks, tradeoffs, or reconsideration conditions.

### 9. Resolve Proposal Evidence

**Transition:** `proposal_challenges_complete` → `proposal_evidence_resolved` only when the session may continue  
**Owner:** engine and authorized evidence source

New evidence requests created during proposal debate are resolved before advocates revise. The same exact zero-or-one-per-request cardinality and waiting, pause, gathered, and conditional outcomes apply.

This explicit stage prevents a decision-critical factual request from being hidden inside a revision or ignored because the first evidence stage has already passed.

### 10. Revise Positions

**Transition:** `proposal_evidence_resolved` → `revisions_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/revision.md`

Each advocate submits one complete `Revision`, including when retaining its original position.

The record states:

- what changed or was deliberately retained;
- why;
- the challenge, evidence, or reasoning responsible;
- concessions;
- unresolved disagreements;
- new risks, sacrifices, or uncertainty;
- expected strategic effect;
- final confidence.

Reasoned retention uses the same `Revision` artifact with a materially unchanged complete proposal, an empty or accurate change list, and explicit reasons. Revision member, original proposal owner, and revised proposal member must match.

A well-defended unchanged position is valid. Performative movement is not.

### 11. Seneschal Adjudication

**Transition:** `revisions_complete` → `adjudicated`  
**Owner:** Seneschal  
**Prompt:** `prompts/adjudication.md`

The Seneschal evaluates the complete record and selects or constructs the strongest strategy.

The adjudication must:

- identify decisive reasons;
- preserve accepted frames;
- explain why every major alternative lost, was incorporated, or survives as a minority objection;
- seek a coherent hybrid when compatible strengths can resolve a material conflict;
- explain why no hybrid is superior when selecting one revised strategy substantially intact;
- preserve serious minority objections and reconsideration triggers;
- state assumptions and residual uncertainty;
- identify actions requiring user authorization;
- distinguish recommendation from authorization.

Majority support, rhetorical force, or compromise is not sufficient justification.

### 12. Produce the Actionable Plan

**Transition:** `adjudicated` → `plan_complete`  
**Owner:** Seneschal  
**Prompt:** `prompts/actionable_plan.md`

The final `ActionablePlan` includes:

- the decision and objective;
- the immediate next action;
- ordered steps;
- responsible owner or party where relevant;
- dependencies and completion signals;
- checkpoints;
- risks and mitigations;
- assumptions;
- decision triggers;
- stop, exit, or reconsideration conditions.

A serious surviving objection must remain visible through applicable risks, assumptions, triggers, mitigations, or reconsideration conditions rather than being hidden only in internal state.

A strategically interesting explanation without concrete next steps is incomplete.

## Challenge Assignment Policy

Challenges are ranked by:

1. conflict with a user hard constraint or stated objective;
2. critical or high effect on the recommendation;
3. unsupported controlling fact, assumption, or forecast;
4. severe downside, irreversibility, or missing recovery path;
5. breadth of disagreement among independent advocates;
6. fit with a declared strategic counterweight;
7. stable artifact, claim, and advocate-order tie-breaks.

Minimum-protocol bounds:

- no more than four primary assignments in one round;
- no advocate receives more than two primary challenges in one round;
- no self-challenge;
- declared counterweights are preferred when relevant;
- a non-counterweight assignment requires an explicit reason;
- a repeated challenge to the same claim requires new evidence or a revised claim;
- low-materiality claims are not challenged merely for completeness.

## Stopping Rule

A debate phase begins with one bounded challenge round.

A second round is permitted only when all of the following are true:

- at least one high or critical claim remains unresolved;
- the issue could introduce a material frame, change a claim, resolve decision-critical evidence, or change adjudication;
- a specific next challenge or evidence action is identified;
- the action is not repetition without new input.

The phase stops when:

- no material open issue remains;
- objections repeat without new evidence or revision;
- user clarification is required;
- responsible deliberation must pause;
- the phase is complete;
- the two-round safety limit is reached.

The safety limit never silently discards unresolved issues. At the limit, Imperium must preserve them and either pause or proceed conditionally with explicit assumptions and reconsideration triggers.

## Canonical Challenge Record

Protocol 1.2 uses `ProtocolTrace.challenges` as the sole canonical store for advocate-authored challenge artifacts.

The legacy `DeliberationRecord.challenges` field must remain empty and exists only for compatibility with the early foundation schema. Export validation rejects a record that attempts to store a second challenge history there.

## Change Control

Changes to lifecycle stages, visibility, challenge materiality, assignment, continuation, evidence cardinality, halt behavior, stopping, or canonical record ownership require a protocol version increment, regression tests, migration consideration, and explicit user approval.
