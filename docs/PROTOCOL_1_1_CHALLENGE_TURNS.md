# Protocol 1.1 — Advocate-Authored Challenge Turns

## Status

**Approved correction, 2026-07-12; incorporated into current protocol 1.2.**

This amendment resolved the advocate-authorship gap discovered before Stage 4 implementation. Protocol 1.2 later clarified conditional challenge outputs, evidence cardinality, halt behavior, and canonical challenge storage. See [`PROTOCOL_1_2_CARDINALITY_AND_HALTS.md`](PROTOCOL_1_2_CARDINALITY_AND_HALTS.md).

Protocol 1.1 did not alter `MANIFESTO.md`, the fixed council, value matrices, the twelve top-level lifecycle transitions, challenge-selection thresholds, evidence routes, or stopping rules.

## The Gap

Protocol 1.0 correctly required targeted challenge assignments and consequential responses, but the stage contract represented each challenge phase only as a Seneschal-owned transition. It did not explicitly represent the assigned challenger's own provider turn or authored challenge artifact.

That ambiguity could allow the Seneschal or orchestration layer to paraphrase or manufacture the advocate's objection. Such behavior would violate the council boundary: members must challenge one another's actual claims, while the Seneschal coordinates rather than impersonates advocates.

## Corrected Internal Sequence

Each nonempty frame or proposal challenge round executes inside the existing top-level challenge transition:

1. **Selection — Seneschal**
   - normalize the relevant claims;
   - produce and validate the bounded `ChallengePlan`;
   - identify challenger, target, target artifact, target claim, materiality, and expected consequence.

2. **Authored challenge — assigned challenger**
   - receive only the assignment and permitted target material;
   - produce one typed `ChallengeArtifact`;
   - preserve every assignment identifier;
   - state the specific objection and failure consequence in the challenger's own reasoning.

3. **Response — assigned target**
   - receive the authored challenge and permitted supporting context;
   - produce one typed `ChallengeResponse`;
   - defend, refine, concede, withdraw, or request evidence.

4. **Continuation — Seneschal**
   - evaluate completed exchanges;
   - continue only under the approved high/critical unresolved-issue rule with a specific next action;
   - otherwise stop with an approved reason.

## Information Boundaries

The challenger may see only:

- the preserved sovereign request;
- its own approved profile snapshot;
- the challenge assignment;
- the normalized target claim;
- the permitted target source artifact;
- explicitly disclosed evidence or prior response when allowed by the current round.

The target may see only:

- the preserved sovereign request;
- its own approved profile snapshot;
- the challenge assignment;
- the challenger-authored `ChallengeArtifact`;
- the target's relevant source artifact and permitted supporting context.

Neither advocate receives an unrestricted accumulated council transcript.

## Empty Plans

An empty `ChallengePlan` remains valid when it records why no material challenge exists. No challenger or target subturn is created for an empty plan.

Protocol 1.2 makes that conditional cardinality explicit in the stage contract so empty plans no longer conflict with required stage outputs.

## Round Repetition

Protocol 1.1 did not loosen the anti-repetition rule. A later round may not repeat the same targeted challenge unless new evidence or a revised claim creates materially new input.

The later claim register must preserve the supersession relationship so the engine can demonstrate what changed between rounds.

## Trace Requirements

The `ProtocolTrace` preserves authored challenge artifacts in addition to claim-register snapshots, challenge plans, and continuation decisions.

Every authored challenge must match its assignment on:

- challenge ID;
- phase;
- round;
- challenger;
- target;
- target artifact;
- target claim.

Stage 4 will add execution and context lineage around these approved strategic artifacts. That implementation trace may prove routing and disclosure, but it must not claim that a scripted challenge improved the plan.

## Compatibility

Protocol 1.1 keeps the same twelve lifecycle stages and configuration dependencies. Saved or replayed protocol 1.0 or 1.1 sessions require explicit migration or must remain associated with their original protocol version; they must not be silently interpreted as current protocol sessions.
