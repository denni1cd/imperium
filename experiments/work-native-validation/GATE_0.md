# Gate 0 — ChatGPT Work Runtime Validation

## Purpose

Validate the minimum native capabilities required to implement the Imperial Council inside ChatGPT Work before building a Skill, Workspace Agent, or custom orchestration layer.

## Gate 0A — Independent subagents and private context

**Status: PASS**

### Observed result

ChatGPT Work created four delegated agents/workstreams and supplied each with the same shared decision plus one distinct private fact. The returned analyses were consistent with only the shared question and the private fact supplied to that agent. No initial analysis demonstrated knowledge of another agent's private fact.

Work also reported that the agents were separate delegated workstreams, context was controlled per subagent, and the subagents ran independently before their results were combined.

### Conclusion

The minimum primitive for independent initial counsel has been demonstrated sufficiently to continue Work-native validation.

---

## Gate 0B — Full disclosure and consequential debate

**Status: PASS WITH LIMITATION**

### Observed result

Using four delegated agents A–D, Work successfully demonstrated:

- preserved independent initial proposals;
- controlled disclosure after the independent phase;
- delivery of all four complete initial proposals and all four private facts to the councillors;
- councillor-selected debate issues rather than centrally assigned objections;
- specific cross-agent challenge, support, reinforcement, concession, revision, and synthesis;
- coalition behavior in which multiple councillors supported the same argument against another position;
- consequential change in the decision state rather than four parallel summaries.

The clearest consequential changes were:

- A changed from internal validation to a conditional limited pilot after engaging B/C's customer-learning case and D's safety constraints;
- B, C, and D adopted A's architectural-isolation objection as a threshold condition;
- A strengthened D's safety case by requiring root-cause remediation and a sufficiently large validation corpus;
- the group converged toward a conditional fork: authorize the pilot only if technical isolation, supervised low-consequence use, standardized onboarding, and protected rework capacity are demonstrated; otherwise fall back to internal validation.

### Limitation discovered

The rebuttal round did not circulate the complete opening Council responses verbatim. Work preserved access to the original proposal packet but compressed the opening discussion before sending it into the rebuttal round.

This does not invalidate the demonstrated debate capability, but it raises a design question: the Council may not need an ever-growing verbatim transcript if it can preserve all material argument state faithfully.

---

## Gate 0C — Persistent councillor state with disposable workers

**Status: PASS WITH RECOMMENDATION REVERSAL NOT YET DEMONSTRATED**

### First attempt

The first Gate 0C test attempted to keep the same four runtime subagent processes alive across multiple debate rounds.

Work successfully created four independent councillors with distinct value matrices and produced behaviorally distinct Phase 1 proposals. Architect also completed one post-disclosure revision after incorporating Steward's capacity objection.

However, Work did not reliably carry all four same runtime subagent sessions through the full disclosure and multi-round debate sequence.

### Revised architecture

The first attempt showed that equating a councillor with a persistent runtime process was unnecessarily strong and a poor fit for the Work runtime.

The revised hypothesis is:

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

### Critical anti-drift rule

A fresh worker must not reinterpret the whole problem from scratch and silently produce a different answer.

It must treat the supplied current councillor state as the starting judgment and evaluate new material against that state.

A change in generated output is not a valid change in Council position unless the councillor can provide a causal bridge identifying:

1. what new argument, evidence, or synthesis changed the judgment;
2. which previous assumption or rationale it defeats or modifies;
3. why the change remains consistent with the councillor's persistent values.

The opposite failure must also be avoided: persistent state must not make councillors artificially stubborn. Rational mind-changing remains required behavior.

### Revised test result

A six-phase retest used 20 fresh disposable delegates and demonstrated:

- successful rehydration of each councillor from stored state;
- no unexplained recommendation drift when no new information was introduced;
- persistent behavioral influence from the value matrices;
- immutable original recommendations alongside evolving current rationale and constraints;
- preservation of concessions, safeguards, and refinements across fresh worker invocations;
- evidence-responsive updating after genuinely new evidence was introduced;
- no arbitrary reversion of prior refinements;
- no collapse into generic identical reasoning;
- coherent multi-round reasoning without persistent runtime sessions.

All four councillors happened to recommend C initially and retained C throughout the test. Their rationales and operating conditions evolved materially, but no recommendation reversal was warranted by the evidence presented.

Therefore the recommendation-level causal-bridge transition is **NOT DEMONSTRATED**, not failed. The test never exercised that path.

### Conclusion

Persistent councillor state plus disposable delegated workers is supported as the preferred Work-native architecture for continued testing.

One focused follow-up remains before Gate 0C is fully closed: introduce evidence that materially defeats one or more stored recommendations and verify that a fresh worker can change the recommendation through an explicit causal bridge without losing identity continuity.

See `GATE_0C_RESULT.md` for the detailed result.

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