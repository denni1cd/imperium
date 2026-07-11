# Project Status

## Stage

Imperium is in the **design and validation stage**.

Stages 1 and 2 are approved: the shared strategic value vocabulary, member profile contract, and fixed initial council are now versioned and encoded. The current focus is Stage 3: freezing the exact deliberation protocol.

The gated path to a first usable implementation is defined in [`STRATEGIC_PROJECT_PLAN.md`](STRATEGIC_PROJECT_PLAN.md).

## Confirmed Decisions

- Imperium is primarily a strategic planning and decision system.
- Actionable plans are the primary measure of success.
- `MANIFESTO.md` is the governing project document.
- `DECISIONS.md` preserves durable accepted decisions without overriding the manifesto.
- The approved version `1.0` vocabulary is Ambition, Urgency, Economy, Simplicity, Resilience, Optionality, Leverage, Adaptability, and Human Sustainability.
- Every member vector contains all nine approved identifiers exactly once and totals `1.0`.
- The approved version `1.0` fixed registry contains one non-advocating Seneschal and four advocates: Steward, Vanguard, Architect, and Castellan.
- Every approved profile includes doctrine, jurisdiction, vigilance, accepted sacrifices, evidence requirements, revision triggers, operating constraints, and a differentiation claim.
- The Seneschal coordinates and adjudicates but does not pre-frame the problem or submit an independent strategy.
- Presentation labels are optional metadata and must be removed during blinded profile-fidelity tests.
- Human Sustainability lacks a dedicated advocate and remains an explicit coverage risk to test.
- Values must materially affect reasoning, tradeoffs, objections, and recommendations while remaining subordinate to user intent, evidence, and constraints.
- Advocates independently interpret the original request before seeing other interpretations.
- Debate must challenge specific interpretations, assumptions, claims, risks, tradeoffs, or strategies.
- Changes caused by debate must be justified and beneficial or must clarify material uncertainty.
- Consensus is not required, and consequential minority objections must survive adjudication.
- User hard constraints and stated objectives outrank member values and doctrines.
- Evidence requests must result in research, user clarification, conditional planning under explicit uncertainty, or a justified pause.
- Advocacy, adjudication, authorization, and execution are separate forms of authority.
- Every deliberation must preserve an inspectable record showing what changed and why.
- Full deliberation must be compared with a direct adviser, an equivalent-budget self-critiquing adviser, and independent advisers without debate.

## Current Design Work

1. Convert the lifecycle outline into exact stage inputs, outputs, and allowed information.
2. Define claim and frame normalization.
3. Define challenge assignment and executable stopping rules.
4. Define stage-specific prompt contracts.
5. Finalize the experiment rubric, cases, repetitions, and success thresholds.

## Protocol Readiness Checklist

### Accepted foundation

- [x] Governing manifesto and actionable-plan objective
- [x] Independent interpretation before cross-member exposure
- [x] Seneschal prohibition against pre-framing and advocacy
- [x] Authority hierarchy between user intent, evidence, assumptions, and member values
- [x] Evidence-request resolution paths
- [x] Separation of advocacy, adjudication, authorization, and execution
- [x] Minimum actionable-plan contents
- [x] Required deliberation record
- [x] Equivalent-budget and independent-panel experimental baselines
- [x] Profile-fidelity evaluation requirement
- [x] Gated strategic roadmap to first usable implementation
- [x] Approved shared value vocabulary and configuration validation
- [x] Approved minimum council member profile contract
- [x] Approved fixed initial roster, value matrices, doctrines, counterweights, and known coverage risks

### Still required before full protocol implementation

- [ ] Exact stage inputs and outputs
- [ ] Claim and frame normalization method
- [ ] Challenge-assignment method
- [ ] Operational stopping rule
- [ ] Stage-specific prompt contracts
- [ ] Experiment problem set and frozen prompts
- [ ] Evaluation rubric, evaluator process, and repetition count
- [ ] Minimum improvement threshold required to justify Imperium

## Implementation Gate

Supporting code may enforce approved Stage 1 and Stage 2 decisions. Full offline orchestration should wait until the Stage 3 protocol contracts are explicit enough to simulate deterministically without a live model.

## Open Questions

- How should numeric value weights be translated into prompt instructions and observable behavior?
- What exact inputs and outputs belong to each lifecycle stage?
- How should claims and frames be normalized without erasing meaningful differences?
- How are challenges assigned so they are targeted rather than performative?
- What exact event proves that debate improved or clarified the decision state?
- What stopping rules prevent both premature closure and wasteful repetition?
- How will humans compare the quality and actionability of experiment outputs?
- What minimum repeatable advantage over the baselines justifies the council's additional complexity?
