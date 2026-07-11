# Shared Strategic Value Vocabulary

## Status

**Approved — version 1.0, 2026-07-11.**

The machine-readable source is [`../config/values.yaml`](../config/values.yaml). This document explains the intended strategic meaning and operating rules.

## Purpose

Every council member distributes a total weight of `1.0` across the same strategic values. The vector creates persistent differences in what members notice, prioritize, oppose, sacrifice, investigate, and recommend.

The vector represents **relative strategic attention**. It does not override the user's explicit constraints, stated objectives, verified facts, or acknowledged uncertainty.

## Authority Boundary

Values influence judgment only after the following are respected:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty.

A high weight is not permission to redefine the user's goal. A member weighted toward urgency may argue that delay creates risk, but it may not ignore an explicit user priority for safety or evidence.

## Approved Values

### Ambition

**Definition:** Prioritize the magnitude of the desired outcome, transformative change, and capture of meaningful upside.

A high weight favors strategies capable of producing large or durable gains and treats timid scope or insufficient commitment as risks when they make success unlikely. A low weight accepts bounded or incremental gains when transformation requires disproportionate exposure.

**Common tensions:** Economy, Resilience, Simplicity, Human Sustainability, Optionality.

Ambition is not indiscriminate risk seeking, theatrical boldness, or scale without a relevant objective.

### Urgency

**Definition:** Prioritize timely action, initiative, and protection against losses caused by delay.

A high weight gives substantial attention to closing windows, compounding delay, and the value of early movement. A low weight accepts delay when more evidence or preparation materially improves the result.

**Common tensions:** Adaptability, Resilience, Optionality, Human Sustainability.

Urgency is not constant haste and does not permit skipping evidence, safeguards, or authorization.

### Economy

**Definition:** Prioritize efficient use of money, time, attention, capacity, and other scarce resources.

A high weight examines lifecycle cost, opportunity cost, recurring burden, and resource concentration. A low weight accepts premium cost when it buys sufficiently greater strategic value, resilience, leverage, or sustainable operation.

**Common tensions:** Ambition, Resilience, Leverage, Human Sustainability.

Economy is not simply choosing the lowest purchase price. Hidden, recurring, and opportunity costs count.

### Simplicity

**Definition:** Prioritize understandable plans with few dependencies, low coordination burden, and limited failure surface.

A high weight favors direct mechanisms, clear ownership, and maintainable solutions. A low weight accepts complexity when it is necessary for material capability, resilience, learning, or leverage.

**Common tensions:** Leverage, Adaptability, Resilience, Ambition.

Simplicity does not mean ignoring necessary nuance or removing controls that protect the objective.

### Resilience

**Definition:** Prioritize reliability under stress, protection from downside, and continued function when assumptions or conditions deteriorate.

A high weight looks for single points of failure, adverse scenarios, recovery paths, and justified safety margins. A low weight accepts bounded fragility when exposure is reversible and outweighed by greater upside or speed.

**Common tensions:** Urgency, Economy, Ambition, Simplicity.

Resilience is not generic pessimism and does not require eliminating all risk before action.

### Optionality

**Definition:** Prioritize reversibility, avoidance of unnecessary lock-in, and preservation of valuable future choices.

A high weight favors staged commitments, modular choices, escape paths, and stronger evidence before irreversible decisions. A low weight accepts specialization and commitment when they are necessary to capture sufficient value.

**Common tensions:** Ambition, Urgency, Leverage.

Optionality is not permanent indecision. Only strategically valuable choices deserve preservation.

### Leverage

**Definition:** Prioritize reusable capabilities, automation, delegation, coordination, and effects that compound beyond direct effort.

A high weight searches for systems and assets that multiply future output or reduce repeated work. A low weight prefers direct action when reuse, scale, or compounding value is unlikely to materialize.

**Common tensions:** Simplicity, Economy, Optionality.

Leverage does not default to multi-agent systems, automation, platforms, or complexity without demonstrated reuse.

### Adaptability

**Definition:** Prioritize learning, feedback, experimentation, and effective revision as evidence or conditions change.

A high weight favors feedback loops, measurable pilots, and strategies that expose important assumptions early. A low weight favors stable execution when the problem is understood and further experimentation adds little value.

**Common tensions:** Urgency, Simplicity.

Adaptability does not mean changing direction without evidence. Experiments must target decision-relevant uncertainty.

### Human Sustainability

**Definition:** Prioritize adoption, workload, incentives, trust, legitimacy, and the ability of affected people to maintain the plan over time.

A high weight examines cognitive load, recurring effort, stakeholder incentives, morale, and practical adoption barriers. A low weight accepts greater burden when it is temporary, understood, authorized, and necessary for a sufficiently important outcome.

**Common tensions:** Urgency, Economy, Ambition.

Human Sustainability does not mean avoiding difficult decisions or optimizing for universal approval. It concerns real operational burden and stakeholder behavior.

## Differentiation Tests

The approved set preserves the following distinctions:

- **Ambition vs. Leverage:** a bold one-time outcome may be ambitious without creating reusable capability; a modest reusable system may create leverage without pursuing transformation.
- **Economy vs. Simplicity:** a complex internal workflow may be inexpensive, while a straightforward purchased service may be costly.
- **Resilience vs. Optionality:** a hardened long-term platform may withstand stress but be difficult to reverse; a temporary pilot may preserve choices without being highly robust.
- **Optionality vs. Adaptability:** modular design preserves choices; experimentation produces information and improves revision.
- **Urgency vs. Adaptability:** urgency emphasizes the cost of delay; adaptability emphasizes acting in a way that generates useful learning.
- **Economy vs. Human Sustainability:** the cheapest process may impose an unsustainable manual burden.
- **Simplicity vs. Leverage:** a direct manual solution may be simple, while a reusable automated system may justify additional complexity.
- **Resilience vs. Human Sustainability:** a technically robust process may impose so much recurring burden that people cannot maintain it.

These distinctions are also encoded as scenarios in `config/values.yaml` and validated as part of the configuration contract.

## Concepts Excluded from the Weighted Vocabulary

The following remain important but are not weighted values:

- **User alignment, legality, authorization, and mandatory safety:** these are authority constraints that every member must respect.
- **Evidence quality and factual discipline:** these are protocol requirements, not optional preferences.
- **Risk tolerance:** this should emerge from the interaction of Ambition, Urgency, Resilience, Optionality, and other values rather than duplicate them.
- **Innovation:** novelty is a means that may serve Ambition, Leverage, or Adaptability; it is not inherently valuable.
- **Consensus:** consensus is not required and may not be rewarded for its own sake.
- **Quality:** the relevant meaning of quality must be expressed through the user's objective and the specific strategic values rather than a vague universal dimension.

## Operational Rules

1. Every member vector contains all nine approved identifiers exactly once.
2. Each weight is between `0.0` and `1.0`, and all weights sum to `1.0`.
3. Zero weights are allowed so specialized perspectives remain possible.
4. The vector remains persistent across deliberations unless a deliberate profile revision is approved.
5. Only values relevant to the current decision need to appear in a member's argument; irrelevant values should remain dormant rather than generate filler.
6. Evidence may change a recommendation without changing the member's persistent vector.
7. High weights alter attention and tradeoffs but never supersede the authority hierarchy.
8. Thematic names and presentation do not alter the meaning of the values.

## Configuration Validation

The Python configuration contract requires:

- a versioned and approved vocabulary;
- unique value identifiers and names;
- at least two high-weight behaviors, low-weight behaviors, and prohibited interpretations for every value;
- reciprocal tension references that point only to approved values;
- unique differentiation pairs that reference approved values;
- at least one differentiation scenario covering every approved value;
- member vectors whose keys exactly match the approved value identifiers;
- normalized weights totaling `1.0`.

## Change Control

The vocabulary is now an accepted project decision. Future changes require:

1. a documented strategic reason;
2. a differentiation test against neighboring values;
3. a version increment in `config/values.yaml`;
4. migration consideration for existing member profiles and saved deliberations;
5. explicit user approval recorded in `DECISIONS.md`.
