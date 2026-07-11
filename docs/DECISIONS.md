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
- Roboute Guilliman is the current candidate presentation identity for the Seneschal.
- The rest of the roster and all substantive profiles remain unapproved until the value vocabulary and profile design are completed.

### 2026-07-10 — Independent interpretation

- Each selected member interprets the original user request independently before seeing another member's interpretation.
- The Seneschal may preserve facts and constraints but must not pre-frame the strategic problem for the council.

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
