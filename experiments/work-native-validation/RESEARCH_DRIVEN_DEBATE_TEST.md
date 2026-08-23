# Research-Driven Debate Test

## Purpose

Test whether the Imperial Council can improve a decision by expanding the information set through independent research, then educating itself through consequential debate.

This is intentionally different from earlier tests that supplied a bounded fact set and predefined options.

## Hypothesis

A stronger Council should be able to:

1. receive an open-ended Sovereign objective rather than a fixed menu of strategies;
2. independently discover different relevant opportunities, facts, risks, and constraints;
3. preserve the evidence behind each councillor's position;
4. disclose that evidence after independent counsel;
5. challenge factual premises and request additional research during debate;
6. revise positions when another councillor introduces stronger evidence;
7. generate strategies or hybrids that were not pre-specified by the Sovereign;
8. produce a materially better final decision than the initial independent proposals.

## Minimal scaffolding

Do not add runtime code or custom orchestration infrastructure for this test.

Use the existing persistent-councillor-state / disposable-worker architecture, with one addition: evidence state.

Each councillor state should retain:

- immutable profile and value matrix;
- immutable original proposal;
- current recommendation;
- current rationale;
- accepted arguments;
- rejected arguments;
- unresolved concerns;
- concessions and revisions;
- causal reason for material position changes;
- evidence relied upon, including source and confidence where available;
- disputed factual claims;
- open research questions.

Research must not be centrally partitioned by the Seneschal. Councillors choose what to investigate according to their own judgment and values.

Research may continue during debate when a new claim, challenge, or uncertainty warrants it.

## Debate requirement

The test should specifically look for an education process:

- one councillor introduces information another did not have;
- another councillor challenges or verifies it;
- further research changes or strengthens the factual record;
- at least one argument, proposal, or operating condition changes as a consequence.

A research summary alone is not sufficient. The information must participate in the deliberation.

## Evaluation

Evaluate both process quality and decision quality.

Process questions include:

- Did councillors discover meaningfully different information independently?
- Did new evidence enter the Council through councillors rather than only through the Seneschal?
- Were factual claims challenged or verified?
- Did research occur during debate in response to a live disagreement?
- Did councillors teach one another information that changed the decision state?
- Did the Council create strategies not provided in advance?
- Did persistent state preserve both reasoning continuity and evidence lineage?

Decision-quality review should separately assess whether the final Council output is factually grounded, risk-aware, internally coherent, actionable, and superior to the initial proposals.

## Implementation rule

This remains an experiment. Do not add infrastructure unless the test exposes a specific Work-native limitation that instructions and lightweight state cannot solve.
