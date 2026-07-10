# Shared Strategic Value Vocabulary

## Status

**Open design item.** No final value set has been approved.

## Purpose

Every council member will distribute a total weight of `1.0` across the same strategic values. The vocabulary must create persistent differences in what members notice, prioritize, oppose, sacrifice, and recommend.

The vector represents relative strategic attention. It does not override the user's explicit constraints, stated objectives, or verified facts.

## Requirements

The final vocabulary should:

- describe strategic priorities rather than communication styles;
- apply across many kinds of personal, organizational, technical, and operational decisions;
- contain values that create real tradeoffs;
- avoid duplicate or nearly synonymous dimensions;
- be understandable without extensive interpretation;
- be compact enough that each weight remains meaningful;
- permit agents with distinct but coherent doctrines;
- produce observable and testable differences in reasoning;
- remain subordinate to the project's authority hierarchy.

## Authority Boundary

The shared values influence how a member evaluates options only after the following are respected:

1. user prohibitions and hard constraints;
2. user-stated objectives and preferences;
3. verified facts and evidence;
4. explicit assumptions and acknowledged uncertainty.

A high weight is not a license to disregard user intent. For example, a member weighted toward speed may argue that delay creates risk, but it may not silently redefine a request that explicitly prioritizes safety over speed.

## Candidate Selection Test

A proposed value belongs in the vocabulary only when changing its weight should predictably change at least one of the following:

- the agent's interpretation of the problem;
- the opportunities or risks it notices;
- the strategy it prefers;
- the sacrifice it accepts;
- the evidence it demands;
- the conditions under which it changes its recommendation.

If changing a value mainly changes tone or wording, it does not belong in the strategic vector.

## Differentiation Test

Before approval, each proposed value should be tested against neighboring concepts.

For every pair of similar values, the design must identify at least one realistic decision where:

- increasing one value while holding the other lower leads to a different interpretation, tradeoff, or strategy;
- the difference is understandable without relying on thematic personality;
- the distinction remains useful across more than one narrow domain.

Values that cannot pass this test should be combined or removed.

## Design Questions

- Should the vocabulary contain approximately 8, 12, or 15 values?
- Which concepts are genuinely distinct rather than different names for the same priority?
- Should opposing priorities be represented as separate values or as competition for finite weight?
- Are there values that should be universal constraints rather than weighted preferences?
- How should context-specific priorities be handled without changing a member's persistent identity?
- How should numeric weights be translated into prompt instructions and observable behavior?

## Required Output

This document will eventually contain:

1. the approved value list;
2. a precise definition for each value;
3. examples of high- and low-weight behavior;
4. known tensions with other values;
5. rules for validating that every member's vector sums to `1.0`;
6. tests showing that neighboring values produce materially different strategic behavior.