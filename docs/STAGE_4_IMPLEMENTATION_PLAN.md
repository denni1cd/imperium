# Stage 4 Implementation Plan

## Status

**Plan only — implementation and merge are not authorized by this document.**

This plan executes the approved design without changing it:

- `MANIFESTO.md`;
- value vocabulary `1.0`;
- council `1.0`;
- protocol `1.3`;
- accepted decisions and prompt contracts.

Protocol 1.3 is the Stage 3 baseline for implementation. Stage 4 may add execution state, persistence, and test fixtures, but it may not redefine strategic artifacts, information boundaries, evidence ordering, challenge policy, or stopping rules.

## Objective

Build the smallest complete provider-neutral offline engine that runs a synthetic council session from a preserved request to one of these valid outcomes:

- actionable plan complete;
- waiting for user clarification;
- deliberation paused;
- explicit failure with an inspectable checkpoint.

Reasoning content is scripted or replayed. The following behavior is real code:

- configuration and prompt freezing;
- lifecycle orchestration;
- per-member context construction;
- provider-call routing;
- direct challenge exchange;
- evidence routing and halt behavior;
- continuation and stopping decisions;
- cross-artifact validation;
- atomic checkpoint, reload, and resume;
- transcript, lineage, and plan export.

Stage 4 proves process execution, not strategic superiority.

## Governing Requirements

The engine must preserve:

- the sovereign request as authoritative intent;
- blind independent interpretation;
- persistent profile-driven perspectives;
- direct advocate-authored challenges and responses;
- specific and consequential disagreement;
- explicit evidence and uncertainty;
- serious minority objections;
- Seneschal coordination without pre-framing or impersonation;
- bounded rounds and stopping reasons;
- actionable output;
- recommendation rather than authorization or execution.

It must not become an unrestricted shared chat, coding swarm, general workflow platform, database service, plugin framework, or autonomous executor.

## Execution Terms

- **Session:** one deliberation from creation until complete, waiting, paused, or failed.
- **Lifecycle transition:** one of the twelve approved top-level state changes.
- **Model turn:** one fake/replay provider invocation by one advocate or the Seneschal.
- **Challenge assignment:** one challenger, target, target artifact, normalized claim, materiality, and expected consequence.
- **Debate round:** one bounded plan, all assigned challenge-response pairs, and one continuation or stopping decision.
- **Checkpoint:** one atomically persisted and validated session envelope.

## Required Council Behavior

### Describe

Each advocate independently produces:

- one blind interpretation;
- one initial strategy proposal;
- actions and expected benefits;
- assumptions and uncertainty;
- tradeoffs, risks, and sacrifices;
- evidence needs;
- triggers and reconsideration conditions;
- confidence.

### Discuss

Each advocate participates directly in the primary proposal-debate fixture as challenger, target, or both.

For every nonempty assignment:

1. the Seneschal selects and validates the assignment;
2. the challenger receives permitted target material and authors one `ChallengeArtifact`;
3. the target receives that artifact and authors one `ChallengeResponse`;
4. evidence requests are collected but not resolved inside the challenge phase;
5. after all assignments are complete, the Seneschal produces the continuation or stopping decision.

The Seneschal may select, route, and validate. It may not write either advocate artifact.

### Deliberate

After the approved debate record and any following evidence-resolution transition, each advocate independently produces one complete `Revision`.

The revision contains either:

- a changed complete proposal; or
- a reasoned retention of a materially unchanged complete proposal.

It records changes or retention, reasons, responsible challenges or evidence, concessions, surviving disagreements, new risks or sacrifices, expected strategic effect, and confidence.

The Seneschal adjudicates only after every selected advocate has a valid final revision.

## Lifecycle Execution

The engine executes the twelve transitions in order whenever the current session status permits advancement:

1. preserve request;
2. select fixed council;
3. collect blind interpretations;
4. compare frames and normalize claims;
5. challenge frames;
6. resolve frame evidence;
7. develop independent strategies;
8. challenge proposals;
9. resolve proposal evidence;
10. collect revisions;
11. adjudicate;
12. produce actionable plan.

Every transition validates:

- current and resulting lifecycle state;
- actor or procedural role;
- permitted input artifacts;
- prompt contract and digest;
- output model, ownership, identity, and cardinality;
- evidence and stopping policy;
- frozen configuration identity;
- session status.

Waiting, paused, failed, and complete sessions do not advance.

## Challenge Cardinality

A challenge stage always produces:

- one `ChallengePlan`;
- one `ContinuationDecision`.

A plan with N assignments produces exactly:

- N `ChallengeArtifact` objects;
- N `ChallengeResponse` objects.

An empty plan produces zero of both and requires a nonempty reason.

The engine must apply both:

- stage-output validation;
- exact assignment-to-challenge-to-response validation.

No exchange may be fabricated to satisfy a schema.

## Challenge Context Boundaries

### Seneschal

The Seneschal receives only the artifacts permitted by the current stage and produces the bounded plan, claim register, continuation decision, adjudication, or final plan assigned to it.

### Challenger

The assigned challenger receives only:

- preserved request;
- its own complete profile snapshot;
- assignment;
- normalized target claim;
- permitted target source artifact;
- prior response or other phase-permitted material only when explicitly allowed.

### Target

The assigned target receives only:

- preserved request;
- its own complete profile snapshot;
- assignment;
- authored challenge;
- relevant source artifact;
- explicitly permitted supporting context.

### Profile Projection

An advocate context contains only that advocate's profile. It must reject another member's profile or the full council registry. The `council_snapshot` artifact kind does not authorize broad profile disclosure.

## Second-Round Ordering

The primary proposal fixture must exercise one justified second round.

Under protocol 1.3, another round inside the same phase may use only:

- a newly material frame exposed by the completed exchange;
- a materially revised or narrowed claim;
- another specific adjudication-relevant follow-up using information already permitted in that phase.

The primary fixture will use a materially revised claim from round one.

It must:

- create a superseding `ClaimRegisterSnapshot`;
- preserve the prior register ID;
- identify the revised claim as new input;
- validate the second plan against prior plans;
- disclose the permitted prior response;
- reject repeated wording or reasoning without material change.

A decision-critical evidence request ends the challenge phase and proceeds to the following evidence transition. Newly resolved evidence does not feed another round of the phase that created it.

## Evidence Cardinality

For each evidence stage:

- zero requests require zero current resolutions;
- N requests require exactly N current resolutions;
- every request ID appears exactly once;
- duplicate, missing, and orphan resolutions fail;
- callers must provide actual input counts to cardinality validation.

No placeholder resolution is created when no request exists.

## Evidence Outcomes

### Gathered

Offline evidence comes from a named synthetic fixture or replay source. Evidence and provenance are preserved. The engine never implies live research occurred.

### Proceed conditionally

The current resolution must preserve:

- planning assumptions;
- exposure bounds;
- remaining uncertainty;
- decision triggers;
- reconsideration or exit conditions.

### User clarification required

The engine:

- stores the current resolution for the request;
- sets status to `waiting_for_user`;
- checkpoints without advancing;
- accepts only explicit later input to resume.

When the user answer is supplied, the authoritative current resolution for that request is replaced by a gathered or conditional resolution. The execution trace preserves the earlier waiting disposition and the replacement event, so the current record still contains exactly one resolution per request without losing history.

### Deliberation paused

The engine:

- stores the current paused resolution;
- sets status to `paused`;
- checkpoints without advancing;
- requires explicit resume authority or new evidence.

If resumed, the current resolution may be replaced only through a validated resume event, while the execution trace preserves the prior pause disposition.

## Canonical Records

The offline session contains:

- `DeliberationRecord` for request, profiles, interpretations, responses, evidence, proposals, revisions, adjudication, plan, and usage;
- `ProtocolTrace` for claim snapshots, challenge plans, authored challenges, and continuation decisions;
- Stage 4 execution trace for calls, contexts, checkpoints, evidence-disposition history, and lineage.

`ProtocolTrace.challenges` is the sole canonical store for authored challenges.

The legacy `DeliberationRecord.challenges` field remains empty and is rejected if populated.

Challenge responses link to canonical challenges by challenge ID.

## Frozen Session Manifest

Resume must not reload mutable current files as if they were the original run inputs.

At session creation, freeze:

- value vocabulary content and digest;
- complete selected profiles and Seneschal profile;
- council configuration and digest;
- protocol configuration and digest;
- exact text and digest of every usable prompt;
- fake/replay fixture identity and digest;
- package/schema version;
- synthetic case identity.

The session stores this manifest. Resume uses the frozen content or fails closed.

## Stable IDs and Call Keys

Synthetic fixtures use explicit stable IDs rather than random defaults.

Each provider call key includes applicable values:

- session ID;
- protocol and prompt digests;
- stage;
- challenge phase and round;
- role and member;
- assignment or target artifact;
- expected output model.

Changing prompt, protocol, profile, target, or expected output changes the key.

## Call and Crash Semantics

For each provider operation:

1. validate the current session;
2. persist pending-call intent;
3. invoke fake/replay provider;
4. validate returned artifact;
5. persist completed call and result atomically;
6. begin no later call until completion is durable.

A fake/replay call may safely be repeated after a crash before completion is saved because it is side-effect free and identified by a stable key.

Stage 4 does not claim universal exactly-once execution for future live providers.

## Offline Session Envelope

The envelope includes:

- deliberation record;
- protocol trace;
- frozen manifest;
- context and execution trace;
- lifecycle history and current status;
- active phase and round;
- current claim snapshot;
- ordered assignments and cursor;
- completed and pending subturns;
- current evidence resolutions and disposition history;
- completed and pending call keys;
- pending continuation decision;
- checkpoint sequence;
- stop or failure reason.

It may add execution state but may not redefine approved strategic artifacts.

## Context Inspection

Every provider call records:

- call key;
- speaker and role;
- stage, phase, and round;
- prompt path and digest;
- profile ID and digest;
- visible artifact IDs and kinds;
- target and prior-response IDs where applicable;
- hash of explicit structured input;
- output artifact ID and model type;
- provider and usage metadata.

Only deliberately disclosed inputs and outputs are recorded. Hidden chain-of-thought is neither requested nor stored.

## Cross-Artifact Validation

Stage 4 enforces:

- exactly one interpretation, proposal, and revision per selected advocate;
- matching member ownership across proposal and revision;
- exactly one challenge and response per assignment;
- zero exchanges for empty plans;
- matching phase, round, claim, artifact, challenger, and target IDs;
- exact current evidence request-resolution mapping;
- no continuation decision before all round assignments complete;
- evidence requests routed only after challenge-phase completion;
- no adjudication before all revisions;
- no plan before adjudication;
- no advancement while waiting, paused, failed, or complete.

## Minority Objection Acceptance

The primary challenged fixture preserves at least one serious unresolved objection and traces it through:

- source interpretation or proposal;
- challenge and response;
- final revision;
- adjudication;
- readable export;
- relevant plan risk, assumption, mitigation, trigger, or reconsideration condition.

Internal-only preservation is insufficient when the objection affects action.

## Hybrid-or-No-Hybrid Acceptance

The Seneschal must seek a stronger strategy rather than vote among proposals.

The primary fixture requires either:

- a coherent hybrid using identified strengths from multiple revisions while resolving or bounding a material conflict; or
- an explicit explanation of why no hybrid improves on the selected revision.

Every non-selected revision is classified as rejected with reasons, partially incorporated, or preserved as a serious minority objection.

Majority support, proposal count, rhetorical force, and compromise are not decision rules.

## Debate-to-Plan Lineage

Where applicable, lineage links:

- normalized claim;
- assignment;
- challenge;
- response;
- evidence request and resolution;
- superseding claim snapshot;
- revision;
- adjudication reason;
- plan element.

Lineage proves process influence, not strategic benefit.

## Required Synthetic Fixtures

### Challenged complete session

- four blind interpretations;
- four initial proposals;
- one positive frame challenge;
- first proposal round involving all four advocates;
- separate challenger and target calls;
- one materially revised high or critical claim;
- one valid second proposal round;
- four revisions or retentions;
- one surviving minority objection;
- hybrid-or-no-hybrid adjudication;
- actionable plan.

Recommended first-round cycle:

- Accountant challenges Gazgul;
- Gazgul challenges Castellan;
- Castellan challenges Overmind;
- Overmind challenges Accountant.

This is fixture design, not a universal participation quota.

### No-material-challenge session

Proves empty plans, zero synthetic exchanges, zero-request evidence stages, and valid completion.

### User-wait session

Produces `waiting_for_user`, prevents advancement, accepts a later synthetic answer, preserves disposition history, and resumes deterministically.

### Paused session

Produces `paused`, prevents downstream work, and requires an explicit validated resume event.

### Conditional session

Proceeds with explicit assumptions, bounds, uncertainty, triggers, and reconsideration conditions.

### Interrupted session

Stops after a challenge or response, reloads, avoids duplicate accepted artifacts, and matches the uninterrupted final structured result.

### Failure tests

Reject:

- malformed checkpoints;
- changed frozen prompt or configuration;
- foreign profile disclosure;
- skipped or repeated transitions;
- wrong challenger or target;
- duplicate or orphan artifacts;
- second-round repetition without a revised claim or permitted new frame;
- evidence resolution inside the challenge phase;
- Seneschal-authored advocate artifacts;
- adjudication before revisions;
- plan generation while waiting or paused;
- legacy duplicate challenge storage.

## Developer Entry Point

Provide one simple credential-free command for the primary synthetic fixture. It requires no source editing, network access, Codex, or API key and writes to an explicit output directory.

## CI and Privacy

GitHub Actions runs:

- full unit and integration suite;
- primary challenged synthetic fixture.

CI uploads only predefined synthetic outputs:

- authoritative session JSON;
- frozen manifest;
- derived readable transcript;
- context/debate/plan lineage;
- actionable-plan export;
- pytest log.

CI never automatically uploads arbitrary user requests, local real sessions, credentials, or personal deliberation data.

## What Stage 4 Can Validate

- protocol execution;
- blind context isolation;
- multiple direct advocate turns;
- correct challenge and evidence ordering/cardinality;
- waiting and pause behavior;
- revised-claim second round;
- minority-objection preservation;
- non-voting adjudication;
- deterministic persistence and resume;
- actionable-plan contract completion.

## What Stage 4 Cannot Validate

- genuine cognitive diversity;
- challenge intelligence;
- authentic belief change;
- strategic superiority of a hybrid;
- Seneschal wisdom;
- advantage over A1, A2, or B;
- justification of eventual model cost.

Those remain live-model and controlled-experiment questions.

## Explicit Exclusions

Stage 4 will not:

- modify the manifesto, council, values, or protocol 1.3;
- add live providers, network research, or execution;
- add dynamic selection or experiment conditions;
- add a database, queue, web UI, MCP service, or plugin system;
- claim the council premise is validated;
- upload non-synthetic user data in CI;
- merge automatically after tests.

Any new constitutional or protocol gap is resolved separately rather than hidden in engine code.

## Completion Criteria

Stage 4 is ready for hands-on review only when:

- complete, waiting, paused, conditional, empty-challenge, and interrupted paths pass;
- every advocate describes, discusses, and deliberates in the primary session;
- the second proposal round uses a materially revised claim;
- context inspection proves own-profile and allowed-artifact boundaries;
- minority objection and hybrid-or-no-hybrid requirements pass;
- frozen inputs and stable call keys support deterministic resume;
- a valid actionable plan and all synthetic review artifacts are exported;
- no credential or live provider is required;
- the completed implementation remains unmerged until explicit user authorization.
