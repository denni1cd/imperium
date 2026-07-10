# Experiment Plan

## Status

**Open design item.** This document defines the validation required before Imperium expands beyond a minimum viable deliberation protocol.

## Central Hypothesis

A controlled council with persistent strategic values, independent interpretation, and consequential debate will produce better actionable plans than either a single capable adviser, a single adviser using structured self-critique, or several independent advisers whose outputs are merely aggregated.

## Experimental Conditions

### A1. Direct Single Adviser

One capable model receives the request and produces its best strategic recommendation and actionable plan in a single pass.

### A2. Equivalent-Budget Single Adviser

One capable model receives approximately the same total inference budget as the full council condition. It may use structured problem framing, self-critique, revision, and plan refinement, but it remains one strategic perspective without persistent council-member profiles.

This condition tests whether additional reasoning budget alone explains any improvement.

### B. Independent Advisory Panel

Several value-profiled members independently interpret the request and propose strategies. The Seneschal adjudicates their submissions without member-to-member debate.

This condition tests whether multiple persistent perspectives add value without debate.

### C. Full Imperium Deliberation

The same members use the complete minimum protocol:

1. independent interpretation;
2. frame comparison and targeted challenge;
3. evidence resolution where required;
4. independent strategy development;
5. proposal challenge;
6. revision with explicit reasons for change;
7. Seneschal adjudication;
8. actionable final plan.

This condition tests whether consequential debate adds value beyond independent diversity and additional inference.

## Experimental Controls

For each test set, freeze and record wherever practical:

- exact model provider, family, and version;
- model parameters and reasoning settings;
- the original request and factual context;
- user goals, constraints, and prohibitions;
- council profiles and value matrices;
- system and stage prompts;
- research and tool access;
- output contracts and maximum plan length;
- evaluation rubric;
- run order or randomized presentation order.

The first experiments should avoid changing both model family and deliberation protocol simultaneously.

Conditions B and C should use the same council members. Conditions A2 and C should receive approximately comparable total reasoning opportunity, while acknowledging that exact token equivalence may not always be possible.

## Repeated Runs

A single impressive output is not evidence of a reliable protocol.

Each condition should be run multiple times per problem using recorded settings. The experiment must track:

- average quality;
- variance between runs;
- frequency of serious failure;
- stability of member perspectives;
- consistency of final recommendations when facts do not change.

The number of repeats remains an open design decision, but it must be selected before examining the final results.

## Test Problem Set

The test set should include strategic decisions with:

- multiple legitimate objectives;
- meaningful tradeoffs;
- uncertain assumptions;
- more than one plausible strategy;
- enough consequence that an actionable plan matters;
- no single objectively obvious answer.

Candidate categories include personal project selection, organizational prioritization, product strategy, resource allocation, risk response, and technology adoption.

Final cases, expected decision context, and evaluation criteria must be recorded before results are generated. Cases should include situations where human sustainability, stakeholder effects, long-term leverage, cost, speed, and downside risk matter in different combinations.

## Evaluation Dimensions

### Strategic Quality

- strength of problem interpretation;
- important opportunities and risks identified;
- assumptions exposed;
- quality of tradeoff analysis;
- coherence of the selected strategy;
- preservation of consequential objections;
- alignment with the user's actual objective and constraints.

### Actionability

Every final plan should be assessed for:

- a clear decision and objective;
- an immediate next action;
- useful sequencing;
- ownership or responsibility where relevant;
- dependencies and prerequisites;
- checkpoints or milestones;
- principal risks and mitigations;
- measurable decision triggers;
- assumptions that must remain true;
- conditions for revision, exit, or abandonment.

### Debate Contribution

- material changes caused by challenges;
- reasoning and evidence supporting those changes;
- concessions and refinements;
- resolved evidence requests;
- improved or hybrid strategies created;
- beneficial difference from simple aggregation;
- harmful or pressure-driven changes avoided;
- preserved unresolved objections that remain decision-relevant.

### Profile Fidelity

The experiment must separately test whether council members behave as persistent strategic perspectives.

Measure:

- consistency of the same member across different problems;
- distinguishability between different members without names or thematic tone;
- correspondence between recommendations and value matrices;
- whether changing a value weight predictably changes interpretation or tradeoffs;
- whether members remain evidence-responsive rather than rigid caricatures;
- whether two nominally different profiles repeatedly produce redundant reasoning.

A strong final plan does not validate the profile system if the members are inconsistent or interchangeable.

### Efficiency

- number of model calls;
- token consumption;
- repeated or non-contributing debate;
- improvement gained per additional deliberation cost;
- comparison with the equivalent-budget single adviser.

Efficiency is not the primary measure, but added cost must produce enough strategic value to justify itself.

## Evaluation Method

Use blinded human comparison whenever possible. Evaluators should see the resulting plans without knowing which condition produced them.

Evaluators should both:

1. score each output against the defined dimensions;
2. rank competing outputs for the same problem.

The primary comparison is whether condition C produces more strategically valuable and actionable plans than A1, A2, and B.

Condition B isolates the value of debate from diverse independent perspectives. Condition A2 isolates the value of the council from additional reasoning budget and structured revision.

## Required Experiment Record

Preserve:

- all frozen prompts and profiles;
- model and parameter information;
- original test cases and context;
- raw outputs from every condition and repeat;
- structured deliberation records for condition C;
- token and model-call measurements;
- evaluator instructions;
- blinded scores and rankings;
- disagreements between evaluators;
- analysis scripts or calculations used;
- conclusions, limitations, and protocol changes.

## Success Standard

Imperium should not advance to a larger architecture merely because some council outputs are impressive.

The protocol is promising only when full deliberation shows repeatable improvement over all three baselines, and the improvement is substantial enough to justify its additional cost and complexity.

Profile fidelity must also be demonstrated. Better output alone is insufficient if council members do not maintain distinct, persistent, value-driven reasoning.

## Failure Interpretation

- If B beats A1 but C does not beat B, value-profiled diversity may work while the debate protocol does not.
- If A2 matches C, additional structured reasoning may provide the benefit without a council.
- If C produces more discussion but no better plan, the process is theatrical or poorly targeted.
- If C improves insight but reduces actionability, adjudication and plan synthesis need revision.
- If members are not distinguishable or stable, the profile design has failed even if some outputs are strong.
- If results vary primarily by model rather than protocol, the experiment needs stronger controls.
- If no condition reliably outperforms A1, the council premise requires reconsideration.

## Open Questions

- How many test problems are required for the first meaningful signal?
- How many repeated runs per condition are required?
- Who will perform blinded evaluation?
- What scoring scale and weighting should the rubric use?
- How should evaluator disagreement be resolved or reported?
- What minimum improvement justifies the council's additional cost?
- How closely must A2 and C match in inference budget?
- Which profile-fidelity tests can be automated reliably?