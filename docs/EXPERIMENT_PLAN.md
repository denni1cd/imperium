# Experiment Plan

## Status

**Open design item.** This document defines the validation required before Imperium expands beyond a minimum viable deliberation protocol.

## Central Hypothesis

A controlled council with persistent strategic values, independent interpretation, and consequential debate will produce better actionable plans than either a single capable adviser or several independent advisers whose outputs are merely aggregated.

## Experimental Conditions

### A. Single Strategic Adviser

One capable model receives the request and produces its best strategic recommendation and actionable plan.

### B. Independent Advisory Panel

Several value-profiled members independently interpret the request and propose strategies. The Seneschal adjudicates their submissions without member-to-member debate.

### C. Full Imperium Deliberation

The same members use the complete minimum protocol:

1. independent interpretation;
2. frame comparison and targeted challenge;
3. independent strategy development;
4. proposal challenge;
5. revision;
6. Seneschal adjudication;
7. actionable final plan.

## Experimental Controls

Where practical, conditions should use:

- the same underlying model or equivalent model capability;
- the same original request and factual context;
- the same user constraints;
- equivalent output expectations;
- comparable access to research or tools;
- blinded evaluation order.

The first experiments should avoid changing both model family and deliberation protocol simultaneously.

## Test Problem Set

The test set should include strategic decisions with:

- multiple legitimate objectives;
- meaningful tradeoffs;
- uncertain assumptions;
- more than one plausible strategy;
- enough consequence that an actionable plan matters;
- no single objectively obvious answer.

Candidate categories include personal project selection, organizational prioritization, product strategy, resource allocation, risk response, and technology adoption. Final cases should be recorded before results are generated.

## Evaluation Dimensions

### Strategic Quality

- strength of problem interpretation;
- important opportunities and risks identified;
- assumptions exposed;
- quality of tradeoff analysis;
- coherence of the selected strategy;
- preservation of consequential objections.

### Actionability

- clarity of next steps;
- useful sequencing;
- ownership or responsibility where relevant;
- dependencies and prerequisites;
- measurable decision triggers;
- conditions for revision or exit.

### Debate Contribution

- material changes caused by challenges;
- concessions and refinements;
- improved or hybrid strategies created;
- evidence that the final decision differs beneficially from simple aggregation.

### Efficiency

- number of model calls;
- token consumption;
- repeated or non-contributing debate;
- improvement gained per additional deliberation cost.

## Evaluation Method

Use blinded human comparison whenever possible. Evaluators should see the resulting plans without knowing which condition produced them.

The primary comparison is whether condition C produces more strategically valuable and actionable plans than conditions A and B.

Condition B is essential: it tests whether debate itself adds value beyond collecting diverse independent perspectives.

## Success Standard

Imperium should not advance to a larger architecture merely because some council outputs are impressive.

The protocol is promising only when full deliberation shows repeatable improvement over both baselines, and the improvement is substantial enough to justify its additional cost and complexity.

## Failure Interpretation

- If B beats A but C does not beat B, value-profiled diversity may work while the debate protocol does not.
- If C produces more discussion but no better plan, the process is theatrical or poorly targeted.
- If C improves insight but reduces actionability, adjudication and plan synthesis need revision.
- If results vary primarily by model rather than protocol, the experiment needs stronger controls.
- If no condition reliably outperforms A, the council premise requires reconsideration.

## Open Questions

- How many test problems are required for the first meaningful signal?
- Who will perform blinded evaluation?
- Should evaluators rank outputs, score dimensions, or both?
- How should variance across repeated runs be handled?
- What minimum improvement justifies the council's additional cost?
- Which experiment artifacts must be preserved for later inspection?
