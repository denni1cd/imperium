# Gate 0 — ChatGPT Work Runtime Validation

## Purpose

Validate the minimum native capabilities required to implement the Imperial Council inside ChatGPT Work before building a Skill, Workspace Agent, or custom orchestration layer.

## Gate 0A — Independent subagents and private context

**Status: PASS**

ChatGPT Work created four delegated agents/workstreams and supplied each with the same shared decision plus one distinct private fact. The returned analyses were consistent with only the shared question and the private fact supplied to that agent. No initial analysis demonstrated knowledge of another agent's private fact.

Conclusion: the minimum primitive for independent initial counsel is demonstrated.

---

## Gate 0B — Full disclosure and consequential debate

**Status: PASS WITH LIMITATION**

Work demonstrated preserved independent initial proposals, controlled post-independence disclosure, councillor-selected debate issues, specific cross-agent challenge/support/revision/synthesis, coalition behavior, and consequential change in the decision state.

The clearest changes were:

- A changed from internal validation to a conditional limited pilot after engaging B/C's customer-learning case and D's safety constraints;
- B, C, and D adopted A's architectural-isolation objection as a threshold condition;
- A strengthened D's safety case by requiring root-cause remediation and a sufficiently large validation corpus;
- the group converged toward a conditional fork rather than four parallel summaries.

### Limitation discovered

The rebuttal round did not circulate the complete opening Council responses verbatim. Work preserved access to the original proposal packet but compressed the opening discussion before sending it into the rebuttal round.

This does not invalidate the demonstrated debate capability. It raises a design question: the Council may not need an ever-growing verbatim transcript if it can preserve all material argument state faithfully.

---

## Gate 0C — Persistent councillor state with disposable workers

**Status: PASS**

### Architectural decision under test

The initial attempt to preserve the same four runtime subagent processes across multiple rounds was unreliable and unnecessarily strong.

The revised architecture is:

> **A councillor is a persistent strategic identity and position state, not a persistent runtime process.**

The councillor preserves:

- immutable identity/profile and value matrix;
- immutable original independent proposal;
- current strategy;
- current rationale;
- accepted arguments;
- rejected arguments;
- unresolved concerns;
- concessions and revisions made;
- causal reason for the last material position change;
- immediately preceding councillor statement when useful.

The delegated worker may be disposable.

### Anti-drift and updateability rule

A fresh worker must treat the supplied current councillor state as the starting judgment rather than reinterpret the whole problem from scratch.

A change in generated output is not a valid change in Council position unless the councillor supplies a causal bridge identifying:

1. what new argument, evidence, or synthesis changed the judgment;
2. which previous assumption or rationale it defeats or modifies;
3. why the change remains consistent with the councillor's persistent values.

The opposite failure must also be avoided: persistent state must not make councillors artificially stubborn. Rational mind-changing is required behavior.

### Continuity retest

A six-phase retest used 20 fresh disposable delegates and demonstrated:

- successful rehydration from stored councillor state;
- no unexplained recommendation drift when no new information was introduced;
- persistent behavioral influence from the value matrices;
- immutable original recommendations alongside evolving current rationale and constraints;
- preservation of concessions, safeguards, and refinements across fresh worker invocations;
- evidence-responsive updating;
- no arbitrary reversion of prior refinements;
- no collapse into generic identical reasoning;
- coherent multi-round reasoning without persistent runtime sessions.

All four councillors happened to recommend C throughout that test, so recommendation reversal was initially **NOT DEMONSTRATED**, not failed.

### Recommendation reversal follow-up

A focused follow-up introduced new evidence that materially defeated the prior basis for C:

- pilot customers required live production data;
- legal/security review prohibited customer data in the existing architecture;
- the four-month multi-tenant rework became mandatory before any pilot;
- customer-success support disappeared, placing pilot support on the two product engineers;
- competitor timing moved from four months to at least twelve months.

All four councillors independently changed from C to B through explicit causal bridges:

- **Architect:** C → B because the pilot now forced the very architectural lock-in/rework it had sought to avoid;
- **Vanguard:** C → B because the competitive urgency that justified speed materially diminished;
- **Steward:** C → B because the pilot became operationally unexecutable with two engineers;
- **Castellan:** C → B because production-data exposure removed the pilot's containment and reversibility.

A second set of entirely fresh workers then rehydrated the updated states with no new evidence. All four preserved B without stochastic reversion.

### Conclusion

Gate 0C is fully demonstrated within the scope tested:

- persistent councillor state resists stochastic drift;
- disposable workers can preserve accumulated reasoning and concessions;
- persistent value differences remain behaviorally meaningful;
- material new evidence can cause genuine recommendation reversal;
- recommendation changes can be causally justified;
- subsequent fresh workers preserve the revised judgment.

Persistent councillor state plus disposable delegated workers is therefore the preferred Work-native architecture.

See `GATE_0C_RESULT.md` and `GATE_0C_REVERSAL_RESULT.md` for the detailed experiment records.

---

## Gate 0D — Debate closure and voting

**Status: PENDING**

Test:

- call for vote;
- unfinished-business check;
- majority decision on whether debate continues;
- strategy vote;
- runoff behavior;
- Seneschal procedural and final tie-breaking.

---

## Gate 0E — Definitive plan synthesis and fidelity review

**Status: PENDING**

Test whether the decided Council strategy can be converted into one coherent actionable plan, with surviving minority objections preserved without reopening the settled decision.

---

## Gate 0 exit rule

Proceed to packaging the behavior as an Imperial Council Skill and Workspace Agent only when Work-native execution has demonstrated:

1. independent delegated counsel with controlled private context;
2. post-independence disclosure and genuine cross-agent debate;
3. persistent strategic identity across disposable worker invocations without unexplained drift, while still permitting rational revision;
4. reliable debate closure and voting;
5. one definitive coherent final plan.

If a capability fails, document the specific limitation before adding custom orchestration infrastructure.