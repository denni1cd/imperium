# Project Status

## Stage

Imperium is in the **design and validation stage**.

The current objective is to define a minimum viable deliberation protocol capable of testing whether structured disagreement produces better actionable plans than simpler alternatives.

## Confirmed Decisions

- Imperium is primarily a strategic planning and decision system.
- Actionable plans are the primary measure of success.
- `MANIFESTO.md` is the governing project document.
- `DECISIONS.md` preserves durable accepted decisions without overriding the manifesto.
- Council members use persistent strategic value matrices scored from `0.0` to `1.0`, with all values summing to `1.0`.
- Values must materially affect reasoning, tradeoffs, objections, and recommendations.
- Members independently interpret the original request before seeing other interpretations.
- The Seneschal coordinates and adjudicates but does not pre-frame the problem.
- Debate must challenge specific interpretations, assumptions, claims, risks, tradeoffs, or strategies.
- Changes caused by debate must be justified and beneficial or must clarify material uncertainty.
- Consensus is not required, and consequential minority objections must survive adjudication.
- The council should seek improved or hybrid strategies rather than merely vote among initial proposals.
- Council size and deliberation depth should remain proportional to the decision.
- User hard constraints and stated objectives outrank member values and doctrines.
- Evidence requests must result in research, user clarification, conditional planning under explicit uncertainty, or a justified pause.
- Advocacy, adjudication, authorization, and execution are separate forms of authority.
- Every deliberation must preserve an inspectable record showing what changed and why.
- The first experiments will use a fixed, user-approved roster.
- Full deliberation must be compared with a direct adviser, an equivalent-budget self-critiquing adviser, and independent advisers without debate.

## Current Design Work

1. Define the shared value vocabulary.
2. Finalize the council member profile format.
3. Convert the lifecycle outline into exact data contracts and prompts.
4. Define challenge assignment and executable stopping rules.
5. Select and configure the fixed initial council.
6. Finalize the experiment rubric, cases, repetitions, and success thresholds.

## Protocol Readiness Checklist

### Accepted foundation

- [x] Governing manifesto and actionable-plan objective
- [x] Independent interpretation before cross-member exposure
- [x] Seneschal prohibition against pre-framing
- [x] Authority hierarchy between user intent, evidence, assumptions, and member values
- [x] Evidence-request resolution paths
- [x] Separation of advocacy, adjudication, authorization, and execution
- [x] Minimum actionable-plan contents
- [x] Required deliberation record
- [x] Equivalent-budget and independent-panel experimental baselines
- [x] Profile-fidelity evaluation requirement

### Still required before implementation

- [ ] Approved shared value vocabulary and definitions
- [ ] Approved minimum council member profile contract
- [ ] Initial member value matrices and doctrines
- [ ] Exact stage inputs and outputs
- [ ] Claim and frame normalization method
- [ ] Challenge-assignment method
- [ ] Operational stopping rule
- [ ] Experiment problem set and frozen prompts
- [ ] Evaluation rubric, evaluator process, and repetition count
- [ ] Minimum improvement threshold required to justify Imperium

## Implementation Gate

Substantial implementation should not begin until the unresolved checklist items are clear enough to test as a coherent protocol.

## Open Questions

- Which values belong in the shared vocabulary?
- How many values provide useful differentiation without creating noise?
- How should numeric values be translated into model instructions?
- Which profile fields are essential beyond the value matrix?
- How are challenges assigned so they are targeted rather than performative?
- What exact event proves that debate improved or clarified the decision state?
- What stopping rules prevent both premature closure and wasteful repetition?
- Which initial council members provide the smallest useful set of strategic perspectives?
- How will humans compare the quality and actionability of experiment outputs?
- What minimum repeatable advantage over the baselines justifies the council's additional complexity?