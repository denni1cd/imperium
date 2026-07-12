# Protocol 1.3 — Evidence and Debate-Round Ordering

## Status

**Approved correction, 2026-07-12.**

Protocol 1.3 resolves a sequencing contradiction found during the final Stage 4 plan review. It preserves the manifesto, council, value matrices, twelve top-level lifecycle transitions, challenge thresholds, evidence routes, and two-round safety limit.

## The Contradiction

Protocol 1.2 listed `decision_critical_evidence` as a reason to continue another round inside the same challenge phase.

However, newly requested evidence is resolved only in the next top-level lifecycle transition:

- frame challenge is followed by frame evidence resolution;
- proposal challenge is followed by proposal evidence resolution.

The current challenge-turn information contracts do not permit newly resolved same-phase evidence to be inserted between round one and round two. Leaving that continuation reason in place would require the Stage 4 engine either to bypass stage boundaries or to claim a second round had new evidence that the participants were not allowed to see.

## Corrected Rule

Another round within the same challenge phase is permitted only for:

- a newly material frame already exposed by the completed exchange;
- an unresolved high or critical claim with materially revised or narrowed content;
- a specific follow-up that could change adjudication using information already permitted in the phase.

A decision-critical evidence request does not authorize another same-phase debate round.

Instead:

1. complete all assigned challenge and response turns for the current round;
2. issue a stopping decision that identifies the evidence dependency;
3. complete the current challenge phase;
4. route every evidence request through the following evidence-resolution transition;
5. use the resulting evidence in independent strategy development or advocate revision, as defined by the lifecycle.

## Second-Round Fixtures

The Stage 4 second proposal round must use a materially revised or narrowed claim produced by round-one response or other already-permitted phase context.

It must not depend on evidence that is resolved only after the proposal-challenge transition has completed.

## Preserved Evidence Behavior

Protocol 1.3 does not remove evidence requests or any evidence outcome. Gathered evidence, user clarification, conditional planning, and deliberation pause remain unchanged.

The correction changes only whether unresolved evidence can be described as a reason for another round inside the same challenge phase.

## Compatibility

Protocol 1.0, 1.1, and 1.2 sessions remain associated with their original version unless explicitly migrated. Protocol 1.3 sessions must not silently reinterpret an older continuation decision.
