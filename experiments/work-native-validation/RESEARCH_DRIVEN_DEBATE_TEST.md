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

## Observed result — August 22, 2026

**Research-driven deliberation: PASS WITH PROCEDURAL LIMITATION**

The Council independently generated materially different researched strategies without assigned research lanes:

- Architect: Treasury-core diversified barbell with staged SPY/GLD exposure;
- Vanguard: Treasury core plus concentrated NVIDIA earnings catalyst and gold;
- Steward: 100% short-duration Treasury exposure;
- Castellan: direct Treasury bill plus a small defined-risk SPY call spread subject to a strict price condition.

The strongest demonstrated education chain was:

1. Castellan proposed a defined-risk SPY vertical at a maximum $10 debit.
2. Architect and Steward challenged whether the condition was executable and whether capped downside established positive expected value.
3. Castellan researched the option chain during the live debate.
4. The available last-sale proxy implied approximately $13.02 rather than $10 and did not establish a positive edge.
5. The option strategy lost support; Architect revised away from unsupported risky sleeves, and Castellan later abandoned the option sleeve.

This demonstrates behavior materially different from four researched recommendations followed by summarization: new evidence was generated in response to a live challenge and changed the viable strategy set.

### Procedural limitation discovered

The first strategic ballot was 2–1–1. The orchestration layer incorrectly declared 2 of 4 votes a winning majority despite the protocol requiring more than 50%.

This is a protocol-enforcement failure, not a deliberative-reasoning failure. It directly motivated the addition of the independent **Rules Lawyer** gate guardian to the deliberation protocol.

The Rules Lawyer must validate vote arithmetic and required stage completion before the Council advances.

## Objective-design lesson

The initial investment request used the phrase "maximum reasonable expected profit while minimizing risk of substantial or permanent capital loss."

On a three-month horizon, "minimizing risk" can make short Treasury exposure a near-dominant solution because the risk objective is underspecified and can be interpreted as lexicographically prior to return.

A better follow-up test should preserve the open research space while supplying a finite risk budget rather than asking the Council to minimize risk without limit.

Recommended Sovereign framing:

> I have a hypothetical $20,000 to invest for three months. Maximize reasonable expected profit. I am comfortable accepting a plausible temporary loss of up to roughly 5% ($1,000) in pursuit of higher returns, but I want to avoid strategies with a meaningful likelihood of losing more than 10% ($2,000). Research whatever opportunities and strategies you believe are appropriate.

This does not prescribe asset classes, research lanes, or candidate strategies. It defines how much risk the Council may reasonably spend while leaving the strategy open-ended.

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
- Did the Rules Lawyer prevent advancement through any incomplete or invalid protocol gate?

Decision-quality review should separately assess whether the final Council output is factually grounded, risk-aware, internally coherent, actionable, and superior to the initial proposals.

## Implementation rule

This remains an experiment. Do not add infrastructure unless testing exposes a specific Work-native limitation that instructions and lightweight state cannot solve.
