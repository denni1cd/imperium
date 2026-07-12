# Council Member Profile

## Status

**Approved — version 1.0, 2026-07-11.**

The machine-readable profiles are stored in [`../config/council.yaml`](../config/council.yaml). This document defines the minimum contract every approved profile must satisfy.

## Purpose

A council profile creates a persistent strategic perspective. It must influence what a member notices, prioritizes, opposes, sacrifices, investigates, and recommends across different decisions.

A profile is not a character prompt. Thematic labels and tone may support recognition, but the strategic identity must remain distinguishable when those presentation fields are removed.

## Authority Boundary

A profile defines how a member evaluates strategy. It does not grant authority to override the user.

Member values and doctrines operate beneath:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty.

A member may explicitly challenge whether the user's chosen means will achieve the intended outcome. It may not silently substitute its own objective.

## Approved Profile Contract

### Version and Status

Each profile contains:

- a profile version;
- an approval status;
- a stable member identifier.

Versioning ensures that saved deliberations can identify the exact profile used. Profile changes must not silently reinterpret earlier records.

### Procedural Role

Each profile has one of two roles:

- **Advocate:** independently interprets the request, proposes strategy, responds to challenges, and revises its position.
- **Seneschal:** protects the process, assigns or coordinates challenges, adjudicates the record, and produces the actionable plan.

The Seneschal must not participate as an independent advocate. This prevents the procedural coordinator from framing the problem before the council has produced blind interpretations.

### Identity

Each profile includes:

- a stable identifier;
- a unique office or title;
- a concise strategic purpose.

The identifier and office remain functional even when thematic presentation is removed.

### Value Matrix

Every profile:

- uses all nine approved strategic values exactly once;
- assigns each value a score from `0.0` to `1.0`;
- uses weights totaling exactly `1.0`;
- remains on the approved vocabulary version;
- preserves its vector across deliberations unless an explicit profile revision is approved.

Weights represent relative strategic attention. They do not authorize violations of higher authority.

### Doctrine

Every approved profile contains at least two doctrine statements explaining how it applies its values.

Doctrine must:

- convert the value vector into recognizable strategic judgment;
- state how the member evaluates tradeoffs;
- remain general enough to operate across several problem domains;
- avoid fictional imitation or communication-style instructions.

### Jurisdiction

Jurisdiction identifies the strategic dimensions where the member is especially relevant. It does not grant exclusive control over those dimensions.

### Vigilance

Vigilance identifies the opportunities, risks, assumptions, and failure modes the member is expected to notice early.

### Accepted Sacrifices

Accepted sacrifices state which desirable outcomes the member is comparatively willing to trade away in service of its dominant priorities, subject to user constraints.

This field is required because strategic identity is not meaningful unless it changes what a member will give up.

### Evidence Requirements

Every profile states the evidence it normally demands before supporting its characteristic recommendations.

Evidence requirements must distinguish:

- a factual uncertainty that could change the recommendation;
- a value disagreement that evidence alone cannot settle.

### Revision Triggers

Every profile states what would cause it to refine, abandon, or reverse a recommendation.

A member that cannot change its mind when evidence defeats its position is a caricature, not a strategic adviser.

### Operating Constraints

Each profile includes explicit constraints preventing predictable misuse of its perspective.

Examples include:

- Urgency may not bypass evidence or authorization.
- Economy may not remove required safeguards merely to reduce cost.
- Resilience may not block action merely because uncertainty exists.
- Leverage may not default to platforms or multi-agent systems without demonstrated reuse.

Operating constraints are not substitutes for weighted values. They define boundaries necessary to keep a strategic office coherent and subordinate to the manifesto.

### Presentation

Presentation is optional metadata limited to:

- `label`;
- `tone`.

Presentation must not contain strategic instructions. Blinded profile-fidelity tests must remove presentation metadata.

## Fixed-Roster Contract

The first experimental council configuration must contain:

- exactly one Seneschal;
- at least two independent advocates;
- an explicit ordered advocate list;
- unique member identifiers, titles, and presentation labels;
- non-identical value vectors;
- one differentiation claim for every profile;
- at least one identified strategic counterweight for every advocate;
- known coverage risks that remain visible rather than being solved through speculative roster growth.

## Differentiation Claim

Every profile must document:

- the distinctive question it brings to a decision;
- its expected strategic contribution;
- its likely failure mode;
- the members most likely to counterweight it.

These claims are hypotheses to test. They are not proof that the profiles are genuinely different.

## Profile Validation

A profile is valid only if it can answer:

- What will this member notice that another member may miss?
- Which tradeoff will it evaluate differently?
- What strategy is it more likely to support or oppose?
- What is it willing to sacrifice?
- What evidence could change its mind?
- Is its reasoning distinguishable without relying on its name or tone?
- Does it remain consistent across different problems without becoming rigid?
- Does it preserve user constraints even when its values favor another outcome?

## Profile Fidelity Tests

The validation experiment must separately measure:

- within-member consistency across varied decisions;
- between-member differentiation on the same decision;
- correspondence between dominant values and observed reasoning;
- evidence-responsive revision;
- resistance to collapsing into generic consensus;
- no reliance on thematic language for distinguishability;
- whether known coverage risks become actual systematic omissions.

Profiles that repeatedly produce strategically redundant reasoning should be revised, combined, or removed.

## Change Control

Future profile or roster changes require:

1. a documented strategic reason;
2. a profile or council version increment;
3. validation against the approved vocabulary;
4. updated differentiation and counterweight claims;
5. migration consideration for saved deliberations and experiment configurations;
6. explicit user approval recorded in `DECISIONS.md`.
