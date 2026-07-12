# Decision Log

This document records accepted project decisions that should persist across conversations and design iterations.

`MANIFESTO.md` remains the governing source of truth. This log records how its rules are being applied; it does not override them.

## Accepted Decisions

### 2026-07-10 — Project purpose and success measure

- Imperium is a strategic planning and decision system.
- Its primary measure of success is the production of actionable plans.
- Process, token use, thematic presentation, and architectural complexity are subordinate to strategic value.

### 2026-07-10 — Council identity

- Council members use persistent value matrices scored from `0.0` to `1.0`.
- Every member's weights sum to `1.0` across a shared strategic vocabulary.
- Values must affect interpretation, attention, tradeoffs, opposition, sacrifice, and recommendation—not merely tone.

### 2026-07-10 — Thematic naming

- Council members may use distinctive names for identity and presentation.
- Names do not define a member's strategic perspective and may not substitute for a distinct value matrix, doctrine, or reasoning pattern.
- Presentation metadata must be removable for blinded profile-fidelity tests.
- The stable office IDs and strategic profiles remain authoritative when all names are removed.

### 2026-07-10 — Independent interpretation

- Each selected advocate interprets the original user request independently before seeing another advocate's interpretation.
- The Seneschal may preserve facts and constraints but must not pre-frame the strategic problem for the council.
- The Seneschal does not submit an independent strategy proposal.

### 2026-07-10 — Deliberative authority

The order of authority is:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty;
5. council-member values and doctrines.

Members may challenge whether a stated objective will achieve the user's broader intent, but they may not silently replace the user's priorities with their own.

### 2026-07-10 — Consequential debate

- Debate must address specific interpretations, assumptions, claims, risks, tradeoffs, or strategies.
- Challenges must produce a meaningful consequence such as defense, refinement, concession, withdrawal, evidence gathering, or revision.
- Movement alone is not success. Changes must be justified and must improve the plan or clarify the decision.
- Consensus is not required, and meaningful minority objections must be preserved.

### 2026-07-10 — Evidence handling

A request for evidence must lead to one of four outcomes:

1. evidence is gathered;
2. the user is asked for decision-critical information;
3. the council proceeds under explicit uncertainty with conditional recommendations;
4. deliberation pauses because responsible planning is not possible without the missing information.

### 2026-07-10 — Recommendation and action boundary

- Council members advocate.
- The Seneschal adjudicates.
- The final plan recommends actions.
- The user authorizes consequential actions.
- Any future executor may perform only actions within the authority explicitly granted to it.

### 2026-07-10 — Inspectable deliberation

Each council session must preserve enough structured state to show what was considered, what changed, why it changed, what objections survived, and how the final plan was produced.

### 2026-07-10 — Minimum council and implementation gate

- Convene only the smallest relevant set of members.
- Use a fixed, user-approved roster for the first validation experiments to avoid confounding council selection with deliberation quality.
- Substantial implementation must wait until the minimum viable deliberation protocol is clear enough to test.

### 2026-07-10 — Validation design

Imperium must be compared against:

- a direct single-adviser response;
- a single adviser using a roughly equivalent inference budget with structured self-critique;
- multiple independent advisers without debate;
- the full Imperium deliberation process.

The first experiments should hold model capability, prompts, profiles, context, tools, and output requirements constant wherever practical.

### 2026-07-11 — Shared strategic value vocabulary

Version `1.0` of the shared strategic value vocabulary is approved with nine dimensions:

1. Ambition;
2. Urgency;
3. Economy;
4. Simplicity;
5. Resilience;
6. Optionality;
7. Leverage;
8. Adaptability;
9. Human Sustainability.

- Every council member must use all nine identifiers exactly once in a normalized vector totaling `1.0`.
- Zero weights are permitted.
- Values represent relative strategic attention and remain subordinate to user intent, evidence, constraints, and authorization.
- Risk tolerance, innovation, consensus, evidence quality, legality, and user alignment are not separate weighted values.
- The authoritative machine-readable vocabulary is `config/values.yaml`; its intended meaning is documented in `docs/VALUE_VOCABULARY.md`.
- Future vocabulary changes require explicit user approval, a version increment, differentiation testing, and migration consideration for saved profiles and deliberations.

### 2026-07-11 — Member profile contract and fixed initial council

Version `1.0` of the council profile contract and fixed initial roster is approved.

The first experimental registry contains:

- `seneschal` — procedural coordinator and adjudicator, council name **Seneschal**;
- `steward` — resource discipline, council name **Accountant**;
- `vanguard` — decisive opportunity capture, council name **Gazgul**;
- `architect` — leverage and reusable capability, council name **Overmind**;
- `castellan` — resilience and downside protection, council name **Castellan**.

The fixed advocate set is `steward`, `vanguard`, `architect`, and `castellan`.

- The Seneschal has an inspectable value vector but does not participate as an advocate or submit an independent strategy.
- Every approved profile includes doctrine, jurisdiction, vigilance, accepted sacrifices, evidence requirements, revision triggers, operating constraints, and a differentiation claim.
- Every advocate identifies at least one strategic counterweight.
- Council names are optional presentation metadata and must be removed during blinded profile-fidelity tests.
- No advocate has Human Sustainability as its dominant value. This remains an explicit coverage risk to test rather than a reason to add another member without evidence.
- The authoritative configuration is `config/council.yaml`; the profile and roster rules are documented in `docs/COUNCIL_MEMBER_PROFILE.md` and `docs/INITIAL_COUNCIL.md`.
- Future profile or roster changes require explicit user approval, version increments, updated differentiation claims, vocabulary validation, and migration consideration for saved deliberations and frozen experiments.

### 2026-07-12 — Council name restoration

- The original council identities are **Seneschal, Accountant, Gazgul, Overmind, and Castellan**.
- Steward, Vanguard, and Architect remain internal functional offices and stable IDs rather than user-facing names.
- The later labels Roboute Guilliman, Munitorum, Macharius, Belisarius Cawl, and Rogal Dorn were removed as naming drift.
- This correction changes presentation metadata only. It does not alter member values, doctrines, counterweights, authority, or protocol behavior.

### 2026-07-12 — Minimum deliberation protocol

Version `1.0` of the minimum deliberation protocol was approved.

- The lifecycle contains twelve controlled transitions from preserved request through actionable plan.
- Proposal debate has its own explicit evidence-resolution stage before advocate revision.
- Every transition declares its prerequisite stage, resulting stage, owner, allowed input artifacts, required outputs, prompt contract, and evidence-request permission.
- Independent interpretation is blind and may receive only the sovereign request and the advocate's own profile snapshot.
- Claims are normalized into one decision-relevant proposition each while preserving source wording, conditions, confidence, dependencies, and minority formulations.
- Claims are classified as facts, assumptions, interpretations, value judgments, forecasts, proposed actions, tradeoffs, or risks.
- Challenge assignment prioritizes authority conflicts, materiality, controlling unsupported premises, severe downside, irreversibility, breadth of disagreement, and declared counterweights.
- A challenge must target a normalized claim; generic or theatrical objections do not qualify.
- Empty challenge plans are permitted only when they explain why no material challenge exists.
- One additional debate round is allowed only for a high or critical unresolved issue with a specific next action.
- The minimum protocol allows at most two rounds per challenge phase. Reaching the safety limit preserves unresolved issues and requires a pause or explicit conditional planning rather than silent truncation.
- Repeated challenges require new evidence or a revised claim.
- Evidence is routed to user clarification, external research, conditional planning, or pause according to decision impact and reversibility.
- The abbreviated path is disabled for the initial controlled experiments.
- The protocol trace preserves claim registers, challenge plans, continuation decisions, empty-plan reasons, and issues surviving the safety limit.
- The authoritative configuration is `config/protocol.yaml`; stage prompt contracts are stored in `prompts/`; the lifecycle and debate rules are documented in `docs/DELIBERATION_LIFECYCLE.md` and `docs/CONSEQUENTIAL_DEBATE.md`.
- Future protocol changes require explicit user approval, a version increment, regression tests, and migration consideration for saved sessions and frozen experiments.

### 2026-07-12 — Protocol 1.1 advocate-authored challenge turns

Version `1.1` corrects an execution gap in the approved challenge stages without changing the twelve top-level lifecycle transitions, challenge-selection policy, evidence routes, or stopping rules.

- The Seneschal selects and coordinates challenge assignments but may not author an advocate's challenge or response.
- Every nonempty assignment executes an advocate-owned challenger subturn followed by an advocate-owned target-response subturn.
- The challenger receives the permitted target claim and source artifact and produces a typed `ChallengeArtifact` using the assignment's identifiers.
- The target receives that authored challenge and produces a typed `ChallengeResponse` attributed to the assigned target.
- The Seneschal issues a continuation or stopping decision only after the assigned exchanges are complete.
- Empty challenge plans remain permitted and do not create synthetic advocate turns.
- Authored challenges are included in the protocol trace and must match their assignment's phase, round, members, artifact, and claim.
- The same structure applies to frame and proposal challenge phases.
- The amendment is documented in `docs/PROTOCOL_1_1_CHALLENGE_TURNS.md`.

### 2026-07-12 — Protocol 1.2 cardinality, halt, and canonical record semantics

Version `1.2` corrects remaining execution contradictions without changing the twelve lifecycle transitions, challenge-selection policy, evidence routes, or stopping thresholds.

- `ChallengePlan` and `ContinuationDecision` are unconditional challenge-stage outputs.
- `ChallengeArtifact` and `ChallengeResponse` are conditional per-assignment outputs.
- An empty challenge plan produces zero challenge and response artifacts; synthetic exchanges are invalid.
- Every evidence stage resolves exactly one `EvidenceResolution` per `EvidenceRequest`, including the valid zero-request and zero-resolution case.
- Duplicate, orphan, and unresolved evidence mappings are invalid.
- User-clarification outcomes set the session to `waiting_for_user` and prevent lifecycle advancement.
- Deliberation-pause outcomes set the session to `paused` and prevent lifecycle advancement.
- Gathered evidence and conditional planning may continue only with explicit provenance, conditions, uncertainty, and reconsideration triggers.
- `ProtocolTrace.challenges` is the sole canonical store for advocate-authored challenges.
- The legacy `DeliberationRecord.challenges` field must remain empty and is rejected during record validation if populated.
- `docs/DELIBERATION_LIFECYCLE.md` and `docs/CONSEQUENTIAL_DEBATE.md` are synchronized to protocol 1.2.
- Saved protocol 1.0 or 1.1 sessions must remain associated with their original version unless explicitly migrated.
- The authoritative machine-readable contract is `config/protocol.yaml`; the amendment is documented in `docs/PROTOCOL_1_2_CARDINALITY_AND_HALTS.md`.
