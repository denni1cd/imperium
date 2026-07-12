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

- Council members may use Warhammer 40,000-inspired names for identity and presentation.
- Thematic names do not define a member's strategic perspective and may not substitute for a distinct value matrix, doctrine, or reasoning pattern.
- Presentation metadata must be removable for blinded profile-fidelity tests.
- The stable office IDs and strategic profiles remain authoritative when all thematic metadata is removed.

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

- `seneschal` — procedural coordinator and adjudicator, presentation label **Roboute Guilliman**;
- `steward` — resource discipline, presentation label **Munitorum**;
- `vanguard` — decisive opportunity capture, presentation label **Macharius**;
- `architect` — leverage and reusable capability, presentation label **Belisarius Cawl**;
- `castellan` — resilience and downside protection, presentation label **Rogal Dorn**.

The fixed advocate set is `steward`, `vanguard`, `architect`, and `castellan`.

- The Seneschal has an inspectable value vector but does not participate as an advocate or submit an independent strategy.
- Every approved profile includes doctrine, jurisdiction, vigilance, accepted sacrifices, evidence requirements, revision triggers, operating constraints, and a differentiation claim.
- Every advocate identifies at least one strategic counterweight.
- Thematic labels are optional metadata and must be removed during blinded profile-fidelity tests.
- No advocate has Human Sustainability as its dominant value. This remains an explicit coverage risk to test rather than a reason to add another member without evidence.
- The authoritative configuration is `config/council.yaml`; the profile and roster rules are documented in `docs/COUNCIL_MEMBER_PROFILE.md` and `docs/INITIAL_COUNCIL.md`.
- Future profile or roster changes require explicit user approval, version increments, updated differentiation claims, vocabulary validation, and migration consideration for saved deliberations and frozen experiments.

### 2026-07-12 — Minimum deliberation protocol

Version `1.0` of the minimum deliberation protocol is approved.

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

### 2026-07-12 — Actual debate and offline vertical engine

Stage 4 defines actual debate as a direct, multi-turn interaction rather than a collection of independent submissions.

- The Seneschal may select and bound challenge assignments but may not articulate an advocate's challenge or answer for the targeted advocate.
- Every assigned challenge requires a separate challenger turn, a separate target response, and a matching durable challenge identifier.
- The targeted advocate must later record what the confrontation changed, strengthened, or clarified in its proposal or revision.
- A challenge plan, council summary, or single shared response does not count as debate.
- Full-protocol adjudication is blocked unless direct confrontation occurs in both frame and proposal phases.
- Every planned challenge must have a direct exchange, and every direct exchange must have a traceable later strategic consequence.
- At least two distinct advocates must be confronted during a full run.
- Panel-only, Seneschal-proxied, unanswered, or consequence-free exchanges fail debate verification.
- The offline engine executes all twelve transitions using fake or replay providers, records direct exchanges and consequences, supports atomic stage checkpoints, and can stop, export, reload, and resume.
- Live Codex or API integration remains gated until the offline vertical slice passes independently.
