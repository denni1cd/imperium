# Deliberation Lifecycle

## Status

**Approved — protocol version 1.0, 2026-07-12.**

The authoritative machine-readable contract is [`../config/protocol.yaml`](../config/protocol.yaml). Stage-specific model instructions are stored in [`../prompts/`](../prompts/).

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

For initial validation, snapshot the approved version 1.0 council and select the four fixed advocates. The Seneschal is also snapshotted but is not an advocate.

Dynamic selection remains deferred because it could pre-frame the problem or confound the first experiments.

### 3. Independent Interpretation

**Transition:** `council_selected` → `interpretations_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/interpretation.md`

Each advocate receives only:

- the preserved sovereign request;
- its own approved profile snapshot;
- supplied facts already contained in the request.

It receives no other interpretation, frame, proposal, synthesis, or Seneschal opinion.

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
**Respondents:** targeted advocates  
**Prompt:** `prompts/challenge_frames.md`

The Seneschal produces a bounded `ChallengePlan` targeting normalized claims that could materially change the decision.

A challenge must identify:

- challenger and target advocate;
- target artifact and normalized claim;
- materiality;
- why the claim matters;
- the consequence expected from a useful response.

The challenged advocate must defend, refine, concede, withdraw, or request evidence.

An empty challenge plan is allowed only when it explicitly records why no material challenge exists. Debate is not forced merely to make the process look active.

After responses, a `ContinuationDecision` either stops the phase or authorizes one additional bounded round for a specific unresolved issue.

### 6. Resolve Frame Evidence

**Transition:** `frame_challenges_complete` → `evidence_resolved`  
**Owner:** engine and authorized evidence source

Each evidence request must identify the disputed claim, decision impact, information needed, and preferred source.

Routing rules:

- **Ask the user** when the missing information is a user-exclusive preference, constraint, supplied fact, or authorization issue and plausible answers materially change the plan.
- **Research externally** when the issue is factual, publicly resolvable, and decision-critical.
- **Proceed conditionally** when the uncertainty can be bounded with an explicit assumption and reconsideration trigger without exposing the user to severe or irreversible downside.
- **Pause** when responsible planning is impossible or proceeding could create severe, irreversible, or unauthorized consequences.

Evidence added here informs later stages but does not rewrite the historical blind interpretations.

### 7. Develop Independent Strategies

**Transition:** `evidence_resolved` → `strategies_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/proposal.md`

Each advocate receives the deliberately disclosed frame record, challenges, responses, and resolved evidence, then produces one `StrategyProposal`.

Every proposal includes actions, benefits, assumptions, tradeoffs, risks, sacrifices, decision triggers, reconsideration conditions, and confidence.

Advocates should remain responsive to evidence without optimizing for agreement.

### 8. Challenge Proposals

**Transition:** `strategies_complete` → `proposal_challenges_complete`  
**Coordinator:** Seneschal  
**Respondents:** targeted advocates  
**Prompt:** `prompts/challenge_proposals.md`

The Seneschal first creates a proposal-phase `ClaimRegister`, then assigns targeted challenges to controlling assumptions, forecasts, actions, costs, dependencies, burdens, risks, tradeoffs, or reconsideration conditions.

The same materiality, counterweight, response, continuation, and anti-repetition rules used during frame challenge apply here.

### 9. Resolve Proposal Evidence

**Transition:** `proposal_challenges_complete` → `proposal_evidence_resolved`  
**Owner:** engine and authorized evidence source

New evidence requests created during proposal debate are resolved before advocates revise.

This explicit stage prevents a decision-critical factual request from being hidden inside a revision or ignored because the first evidence stage has already passed.

### 10. Revise Positions

**Transition:** `proposal_evidence_resolved` → `revisions_complete`  
**Owner:** each advocate independently  
**Prompt:** `prompts/revision.md`

Each advocate submits a complete final proposal and records:

- what changed or was deliberately retained;
- why;
- the challenge, evidence, or reasoning responsible;
- concessions;
- unresolved disagreements;
- new risks, sacrifices, or uncertainty;
- expected strategic effect;
- final confidence.

A well-defended unchanged position is valid. Performative movement is not.

### 11. Seneschal Adjudication

**Transition:** `revisions_complete` → `adjudicated`  
**Owner:** Seneschal  
**Prompt:** `prompts/adjudication.md`

The Seneschal evaluates the complete record and selects or constructs the strongest strategy.

The adjudication must:

- identify decisive reasons;
- preserve accepted frames;
- explain why major alternatives lost;
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

The two-round limit is a minimum-protocol safety bound, not permission to truncate a model response or conceal unfinished work.

## Abbreviated Path

The abbreviated path is disabled for initial experiments.

After validation, a decision may be eligible only when it is reversible within bounded cost and time, has no severe downside, lacks decision-critical user-exclusive uncertainty, contains no material goal conflict, and produces no high or critical contested frame.

Even then, Imperium may skip a challenge phase only through an explicit empty `ChallengePlan`. It may never skip the authority hierarchy, actionable-plan contract, inspectable record, or preservation of serious objections.

## Recommendation and Action Boundary

- Advocates recommend and challenge.
- The Seneschal coordinates and adjudicates.
- The final plan recommends actions.
- The user authorizes consequential actions.
- A future executor may perform only explicitly authorized actions.

No member gains operational authority because it argued forcefully.

## Required Protocol Trace

In addition to the established deliberation record, each session preserves:

- frame and proposal claim registers;
- every challenge plan by phase and round;
- continuation or stopping decisions;
- reasons for empty challenge plans;
- issues preserved at the round safety limit;
- stage contracts, prompt versions, profile snapshots, and configuration versions used.

The record must make it possible to reconstruct what each stage saw, what changed, why debate continued or stopped, and whether the final plan benefited.

## Change Control

Protocol changes require:

1. a documented strategic reason;
2. a protocol version increment;
3. updated stage, visibility, prompt, and record contracts;
4. migration consideration for saved sessions and frozen experiments;
5. regression tests with fake and replay providers;
6. explicit user approval recorded in `DECISIONS.md`.
