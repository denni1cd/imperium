# Imperial Council

The Imperial Council is a strategic deliberation system designed to improve judgment through independent counsel, full post-independence disclosure, consequential debate, voting when necessary, and one definitive actionable plan.

The governing document is [MANIFESTO.md](MANIFESTO.md). Implementation decisions must remain subordinate to it.

## Current stage

The project is in design and runtime validation.

The initial operating environment is **ChatGPT Work**. The project is intentionally instruction-first and does not yet contain an API orchestration engine, database, MCP service, or standalone application.

## Current implementation hypothesis

The first release should be a Work-native Imperial Council workflow, eventually packaged as a Workspace Agent and reusable Skill if native Work delegation proves sufficient.

Before that packaging work begins, Gate 0 validates that Work can provide the required primitives:

1. isolated initial subagent reasoning;
2. controlled full proposal disclosure;
3. genuine cross-agent debate;
4. persistent strategic identities;
5. call-for-vote and definitive closure;
6. one coherent final plan.

## Repository map

- `MANIFESTO.md` — governing principles and accepted Council rules.
- `PROJECT_PLAN.md` — implementation sequence and decision gates.
- `skill/` — eventual Work Skill and its durable protocol references.
- `council/` — persistent Council member profiles after the shared value vocabulary is approved.
- `evals/` — comparative evaluation design and cases.
- `experiments/work-native-validation/` — Gate 0 runtime experiments and results.

## Current evidence

Gate 0A has passed: ChatGPT Work successfully created four separately reported subagents, supplied each with shared context plus one private fact, and returned initial analyses with no observed cross-agent fact leakage.

The next test is Gate 0B: full disclosure followed by natural cross-agent debate.
