# Gate 0 — ChatGPT Work Runtime Validation

## Purpose

Validate the minimum native capabilities required to implement the Imperial Council inside ChatGPT Work before building a Skill, Workspace Agent, or custom orchestration layer.

## Gate 0A — Independent subagents and private context

**Status: PASS**

### Test

ChatGPT Work was instructed to create four actual independent subagents/workstreams. All four received the same fictional strategic decision and exactly one unique private fact.

The private facts covered:

- four months of architectural rework for public deployment;
- a competitor expected to launch in four months;
- only two engineers available for five months;
- three severe hallucination incidents in the last 100 uses.

Each agent independently returned a recommendation, reasoning, and the fact it had been given.

### Observed result

The four outputs were materially consistent with only the shared question plus the private fact supplied to that agent:

- the architecture agent reasoned from deployment rework;
- the competitive agent reasoned from market timing;
- the capacity agent reasoned from engineering constraints;
- the reliability agent reasoned from hallucination risk.

No returned initial analysis demonstrated knowledge of another agent's private fact.

Work also explicitly reported that:

- actual separate subagents/workstreams were used;
- no subagent could see another subagent's private fact during initial analysis;
- context was explicitly controlled per subagent;
- the subagents ran independently before results were combined.

### Conclusion

The minimum primitive for independent initial counsel has been demonstrated sufficiently to continue Work-native validation.

This does not yet prove the full Imperial Council runtime. Cross-agent disclosure, debate, persistence, and closure remain to be tested.

---

## Gate 0B — Full disclosure and consequential debate

**Status: PENDING**

### Objective

Using the same fictional decision, test whether Work can:

1. preserve four isolated initial proposals;
2. reveal all complete proposals and all facts to all four subagents only after independence;
3. let each agent choose its own debate targets;
4. support direct challenge, defense, reinforcement, concession, revision, and synthesis;
5. provide the complete evolving discussion to all participants;
6. produce observable changes in the decision state rather than four parallel summaries.

### Pass criteria

Gate 0B passes if the transcript demonstrates specific cross-agent engagement and at least one consequential outcome such as defense, refinement, concession, revision, combination, or materially strengthened reasoning.

Agreement is allowed. Forced disagreement is not required.

Gate 0B fails if Work merely summarizes four views, simulates cross-talk without using the delegated agents, loses the original independent proposals, or cannot provide the necessary shared post-disclosure context.

---

## Remaining Gate 0 work

After Gate 0B:

- **Gate 0C:** multi-round identity/profile persistence;
- **Gate 0D:** call-for-vote, procedural closure, majority/runoff behavior, and Seneschal tie-breaking;
- **Gate 0E:** synthesis of the decided result into one coherent actionable plan plus fidelity review.

Only after these primitives are demonstrated should the project package the behavior as the Imperial Council Skill and Workspace Agent.
