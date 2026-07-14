# Decision Log

This document records accepted decisions that persist across design and implementation. `MANIFESTO.md` remains the governing source of truth; this log records its application and does not override it.

## 2026-07-10 — Project purpose

- Imperium is a strategic planning and decision system.
- Its primary measure of success is actionable strategic plans.
- Process, token use, presentation, and architecture are subordinate to strategic value.
- Failure to outperform a capable single adviser is a legitimate reason to revise or stop the project.

## 2026-07-10 — Council identity and values

- Members use persistent value matrices over a shared strategic vocabulary.
- Each weight is between `0.0` and `1.0`; each vector totals `1.0`.
- Values affect interpretation, attention, tradeoffs, opposition, sacrifice, evidence demands, and recommendation—not merely tone.
- Names and thematic presentation are removable metadata and never define strategic behavior.

## 2026-07-10 — Independent interpretation and Seneschal boundary

- Every selected advocate interprets the original request independently before seeing another interpretation.
- The Seneschal preserves facts and constraints but does not pre-frame the problem or submit an independent strategy.
- Advocates author their own proposals, challenges, responses, and revisions.
- The Seneschal coordinates, stops, adjudicates, and produces the final plan without impersonating advocates.

## 2026-07-10 — Authority hierarchy

When priorities conflict:

1. user prohibitions and hard constraints;
2. user objectives and preferences;
3. verified evidence and facts;
4. explicit assumptions and uncertainty;
5. member values and doctrines.

Members may challenge whether a means achieves the user's broader intent but may not silently replace the user's priorities.

## 2026-07-10 — Consequential debate

- Challenges target specific interpretations, assumptions, claims, risks, tradeoffs, or strategies.
- A useful challenge produces defense, refinement, concession, withdrawal, evidence routing, justified retention, or revision.
- Movement, agreement, hostility, or compromise has no value by itself.
- Consensus is optional; serious minority objections must survive.
- The council seeks stronger or coherent hybrid strategies rather than merely voting among proposals.

## 2026-07-10 — Evidence handling

Every evidence request reaches one of four outcomes:

1. gathered evidence;
2. user clarification required;
3. proceed conditionally with explicit uncertainty;
4. deliberation paused.

## 2026-07-10 — Recommendation and execution boundary

- Advocates recommend and challenge.
- The Seneschal adjudicates.
- The final plan recommends actions.
- The user authorizes consequential actions.
- Any future executor acts only within explicit authority.

## 2026-07-10 — Inspectable records

Each session preserves enough structured state to show what was considered, what changed, why it changed, what objections survived, and how the final plan was produced.

## 2026-07-10 — Minimum council and validation design

- Use the smallest relevant council.
- Use a fixed user-approved roster for initial experiments.
- Compare full Imperium against a direct adviser, an equivalent-budget self-critiquing adviser, and independent profiled advisers without debate.
- Freeze model, prompts, profiles, context, tools, and output contracts wherever practical.

## 2026-07-11 — Strategic value vocabulary 1.0

Approved values:

1. Ambition;
2. Urgency;
3. Economy;
4. Simplicity;
5. Resilience;
6. Optionality;
7. Leverage;
8. Adaptability;
9. Human Sustainability.

Every member uses all nine identifiers exactly once. Values remain subordinate to user intent, evidence, constraints, and authorization. The authoritative configuration is `config/values.yaml`.

## 2026-07-11 — Council 1.0

Approved registry:

- `seneschal` — **Seneschal**, non-advocating coordinator and adjudicator;
- `steward` — **Accountant**, resource discipline;
- `vanguard` — **Gazgul**, decisive opportunity capture;
- `architect` — **Overmind**, leverage and reusable capability;
- `castellan` — **Castellan**, resilience and downside protection.

The fixed advocate set is `steward`, `vanguard`, `architect`, and `castellan`. Every profile includes doctrine, jurisdiction, vigilance, accepted sacrifices, evidence requirements, revision triggers, constraints, and counterweights. Human Sustainability remains a known coverage risk. The authoritative configuration is `config/council.yaml`.

## 2026-07-12 — Council name restoration

- The approved user-facing names are Seneschal, Accountant, Gazgul, Overmind, and Castellan.
- Steward, Vanguard, and Architect remain internal functional IDs.
- The later labels Roboute Guilliman, Munitorum, Macharius, Belisarius Cawl, and Rogal Dorn were removed as presentation drift.
- No profile behavior changed.

## 2026-07-12 — Minimum protocol 1.0

- Twelve controlled transitions lead from preserved request to actionable plan.
- Independent interpretation is blind.
- Claims are normalized while preserving source, conditions, confidence, dependencies, and minority formulations.
- Challenge assignment is material, bounded, counterweighted, and anti-repetitive.
- Evidence is resolved before strategy development and again before revisions.
- One additional round per challenge phase is allowed only for a high or critical unresolved issue and a specific useful next action.
- The abbreviated path is disabled for initial experiments.

## 2026-07-12 — Protocol 1.1 advocate-authored challenges

- Every nonempty assignment executes an advocate-owned challenger turn followed by an advocate-owned target response.
- The challenger produces a typed `ChallengeArtifact`; the target produces a typed `ChallengeResponse`.
- The Seneschal coordinates but does not author either artifact.
- Empty plans create no synthetic advocate turns.
- Authored challenges are preserved in `ProtocolTrace`.

See `docs/PROTOCOL_1_1_CHALLENGE_TURNS.md`.

## 2026-07-12 — Protocol 1.2 cardinality, halt, and canonical storage

- Plan and continuation artifacts are unconditional challenge-stage outputs.
- Challenge and response artifacts are conditional per assignment.
- Empty plans produce zero exchanges.
- Evidence stages produce exactly one resolution per request, including zero requests and zero resolutions.
- Duplicate, missing, and orphan evidence mappings are invalid.
- User clarification sets `waiting_for_user`; pause sets `paused`; neither advances.
- `ProtocolTrace.challenges` is the sole canonical authored-challenge store.
- The legacy `DeliberationRecord.challenges` field remains empty.

See `docs/PROTOCOL_1_2_CARDINALITY_AND_HALTS.md`.

## 2026-07-12 — Protocol 1.3 evidence and debate-round ordering

- Newly requested frame evidence is resolved only after frame challenge completes and informs strategy development.
- Newly requested proposal evidence is resolved only after proposal challenge completes and informs advocate revision.
- A same-phase second round uses a newly material frame, a materially revised or narrowed claim, or another adjudication-relevant follow-up based on already permitted information.
- An evidence request ends the current challenge phase and routes to the following evidence-resolution transition.
- No lifecycle transition, evidence outcome, materiality threshold, or two-round safety limit changed.

See `docs/PROTOCOL_1_3_EVIDENCE_ROUND_ORDERING.md`.

## 2026-07-14 — Stage 4 acceptance and merge

- The complete credential-free fake/replay engine satisfied the reviewed Stage 4 contract.
- The local challenged scenario was inspected and accepted.
- PR #8 was squash-merged as `9f1344672b07443a1b95b99ad001ef6d70c78f72`.
- Stage 4 proves protocol execution, information isolation, challenge routing, evidence ordering, halt paths, persistence, deterministic replay resume, minority-objection preservation, adjudication, and actionable-plan generation.
- Stage 4 does not prove live profile fidelity, strategic improvement, or exactly-once live model execution.

## 2026-07-14 — Stage 5 bounded Codex provider gate

- Stage 5 begins with one isolated Accountant `Interpretation`, not a complete live council.
- Each Codex call uses a fresh process, empty temporary workspace, read-only sandbox, ephemeral session, explicit context, structured output, and zero automatic retries.
- GitHub Actions simulates subprocesses and never consumes Codex tokens.
- A failed live call is preserved and corrected before another token-consuming attempt.
- The corrected Gate 1 call completed successfully and produced a profile-faithful, domain-valid Accountant interpretation.
- One interpretation used 13,006 input tokens, so a complete live run remains blocked until provider injection and context/token controls are implemented and reviewed.

### Structured Outputs compatibility

The first live attempts on Codex CLI 0.142.5 exposed unsupported Pydantic `propertyNames` and Decimal regex lookaround constructs.

The accepted provider boundary is:

- Pydantic domain models remain unchanged;
- an internal reversible wire-schema adapter removes unsupported annotations and patterns;
- every wire object lists every property as required and sets `additionalProperties: false`;
- arbitrary dictionaries are encoded as arrays of unique `{key, value}` entries;
- wire output is restored before the original Pydantic model validates it;
- duplicate keys, malformed entries, and domain-invalid output fail closed.

This adaptation is provider infrastructure, not a protocol or domain-model change.

## 2026-07-14 — Stage 5 Terra Light safety lock

- All Stage 5 live tests use `gpt-5.6-terra` with CLI reasoning effort `low`, the CLI equivalent of Terra Light.
- The user-facing live command exposes no model or reasoning-effort override.
- The Codex provider rejects any non-Terra model or any effort other than `low` before launching the executable.
- Sol, Luna, other model families, medium, high, and xhigh are prohibited during current testing.
- Any quality-driven escalation requires explicit user approval and a reviewed code change; it cannot occur through a runtime flag or local configuration default.

## Change Control

Changes to the manifesto require direct user approval. Changes to values, council profiles, roster, lifecycle, visibility, debate rules, evidence ordering, stopping, canonical record ownership, or the Stage 5 model safety lock require explicit approval, versioning where applicable, regression tests, and migration consideration.
