# Protocol 1.2 — Cardinality, Halt, and Canonical Record Semantics

## Status

**Approved correction, 2026-07-12.**

Protocol 1.2 resolves contract contradictions discovered during the second Stage 4 readiness review. It preserves `MANIFESTO.md`, the fixed council, value matrices, challenge-selection policy, evidence routing policy, stopping thresholds, and all twelve top-level lifecycle transitions.

## Why the Correction Was Required

Protocol 1.1 correctly introduced advocate-authored challenge turns, but three execution ambiguities remained:

1. challenge and response artifact kinds were required even when a valid challenge plan was empty;
2. evidence stages required one generic resolution even though valid sessions may contain zero, one, or several evidence requests;
3. the early foundation record and the protocol trace could both store different challenge representations.

Those ambiguities could force synthetic debate, orphan evidence artifacts, or divergent histories. Protocol 1.2 removes them before the offline engine is implemented.

## Conditional Challenge Outputs

A frame or proposal challenge stage always produces:

- one `ChallengePlan`;
- one `ContinuationDecision`.

For each assignment in a nonempty plan, the stage additionally produces:

- exactly one `ChallengeArtifact` authored by the assigned challenger;
- exactly one `ChallengeResponse` authored by the assigned target.

An empty plan produces zero challenge and response artifacts. Its required `no_challenge_reason` explains why no material target exists.

Challenge and response artifacts are therefore conditional subturn outputs rather than unconditional stage outputs.

## Evidence Cardinality

Each evidence stage uses an explicit output-cardinality rule:

- count `EvidenceRequest` inputs;
- require exactly the same number of `EvidenceResolution` outputs.

Consequences:

- zero requests produce zero resolutions;
- every request is resolved once;
- duplicate resolutions are invalid;
- orphan resolutions are invalid;
- unresolved requests prevent stage completion.

## Evidence Halt Behavior

After evidence resolutions are validated:

- gathered evidence leaves the session active;
- proceed-conditionally leaves the session active only when planning conditions are explicit;
- user clarification sets the session to `waiting_for_user`;
- deliberation paused sets the session to `paused`.

A waiting or paused session does not advance to the next lifecycle stage. It preserves the unresolved request, current artifacts, and checkpoint for later inspection or resume.

In Stage 4, gathered evidence must come from an explicit synthetic fixture or replay source. The offline engine may not imply that live research occurred.

## Canonical Challenge Storage

`ProtocolTrace.challenges` is the sole canonical collection of protocol 1.1+ advocate-authored challenge artifacts.

The legacy `DeliberationRecord.challenges` field remains in the early foundation schema only for compatibility. It must remain empty, and export validation rejects records that populate it.

This avoids two independently writable accounts of the same debate.

## Resume and Migration

Protocol 1.0 and 1.1 saved sessions must remain associated with their original protocol version unless explicitly migrated.

A protocol 1.2 session must freeze or identify the exact configuration and prompt content used by the run. Stage 4 will define the execution envelope and content digests needed for deterministic resume.

No saved session may be silently reinterpreted under protocol 1.2.

## Validation Added

Protocol 1.2 adds deterministic validation for:

- challenge-stage unconditional versus assignment-conditional outputs;
- exact challenge and response coverage for every assignment;
- valid empty challenge rounds;
- evidence output counts based on request counts;
- one-to-one evidence request and resolution identifiers;
- required session status after evidence outcomes;
- rejection of legacy challenge storage.

## Scope Boundary

Protocol 1.2 does not implement the Stage 4 engine. It defines the corrected contracts that Stage 4 must execute.
