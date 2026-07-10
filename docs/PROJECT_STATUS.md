# Project Status

## Stage

Imperium is in the **design and validation stage**.

The current objective is to define a minimum viable deliberation protocol capable of testing whether structured disagreement produces better actionable plans than simpler alternatives.

## Confirmed Decisions

- Imperium is primarily a strategic planning and decision system.
- Actionable plans are the primary measure of success.
- `MANIFESTO.md` is the governing project document.
- Council members use persistent strategic value matrices scored from `0.0` to `1.0`, with all values summing to `1.0`.
- Values must materially affect reasoning, tradeoffs, objections, and recommendations.
- Members independently interpret the original request before seeing other interpretations.
- The Seneschal coordinates and adjudicates but does not pre-frame the problem.
- Debate must challenge specific interpretations, assumptions, claims, risks, tradeoffs, or strategies.
- Consensus is not required, and consequential minority objections must survive adjudication.
- The council should seek improved or hybrid strategies rather than merely vote among initial proposals.
- Council size and deliberation depth should remain proportional to the decision.

## Current Design Work

1. Define the shared value vocabulary.
2. Define the council member profile format.
3. Finalize the deliberation lifecycle and information boundaries.
4. Define consequential debate and its measurements.
5. Select and configure the initial council.
6. Design the validation experiment.

## Implementation Gate

Substantial implementation should not begin until the six design items above are clear enough to test as a coherent protocol.

## Open Questions

- Which values belong in the shared vocabulary?
- How many values provide useful differentiation without creating noise?
- How should numeric values be translated into model instructions?
- Which profile fields are essential beyond the value matrix?
- How should the Seneschal select relevant members without pre-framing the problem?
- How are challenges assigned so they are targeted rather than performative?
- What exact event proves that debate changed the decision state?
- What stopping rules prevent both premature closure and wasteful repetition?
- Which initial council members provide the smallest useful set of strategic perspectives?
- How will humans compare the quality and actionability of experiment outputs?
