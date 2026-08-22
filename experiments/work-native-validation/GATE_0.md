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
- continued use of the same named delegated agents after disclosure;
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

The rebuttal round did **not** circulate the complete opening Council responses verbatim. Work preserved access to the original proposal packet but compressed the opening discussion before sending it into the rebuttal round.

This violates the current protocol requirement that, once the chamber opens, participating councillors should have access to the complete evolving deliberative record.

This is a concrete runtime behavior to address in instructions and retest. It does not invalidate the demonstrated cross-agent debate capability, but Gate 0B should not be treated as a clean pass until we know whether verbatim transcript circulation can be reliably enforced or whether controlled summarization must become an explicit, tested design choice.

### Conclusion

ChatGPT Work has demonstrated the core transition from independent counsel to genuine shared debate. The remaining question is transcript fidelity across rounds.

See `GATE_0B_RESULT.md` for the detailed observed result.

---

## Gate 0C — Multi-round identity/profile persistence

**Status: PENDING**

Test whether persistent strategic value profiles remain behaviorally distinct across multiple debate rounds, including after cross-member persuasion and partial convergence.

This test should also explicitly require verbatim circulation of the immediately preceding Council responses to determine whether the Gate 0B transcript limitation can be corrected by instruction.

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
3. sufficiently reliable identity/profile persistence and deliberative context sharing;
4. reliable debate closure and voting;
5. one definitive coherent final plan.

If a capability fails, document the specific limitation before adding custom orchestration infrastructure.