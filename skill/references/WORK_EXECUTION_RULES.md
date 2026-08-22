# ChatGPT Work Execution Rules

These rules define the minimum execution behavior required from ChatGPT Work before the Imperial Council is packaged as a reusable Skill or Workspace Agent.

## Independent phase

- Use actual delegated subagents/workstreams when available; do not simulate several councillors inside one monolithic answer.
- Give every councillor the same Sovereign request and shared factual context.
- Give each councillor only their own profile/private instructions.
- Do not expose one councillor's initial output to another until all initial outputs are complete.
- Preserve each initial proposal before disclosure.

## Disclosure boundary

- Open the chamber only after all initial proposals are complete.
- After disclosure, every councillor must receive every complete initial proposal and the complete shared context.
- Do not replace full proposals with Seneschal summaries.

## Debate phase

- Provide the complete evolving Council discussion to all participating councillors.
- Do not assign debate positions or force artificial disagreement.
- Let councillors decide what to challenge, support, defend, revise, or synthesize.
- Preserve changes of mind rather than resetting members to their initial proposal.
- Continue only while new material reasoning remains.

## Closure

- Allow any councillor to call for a vote.
- Distinguish unfinished material reasoning from repeated disagreement.
- Use majority/runoff rules and Seneschal tie-breaking as specified in the deliberation protocol.
- Always terminate a completed session in one decided strategy and coherent plan.

## Failure behavior

If Work cannot preserve a required information boundary or delegation behavior, record the limitation explicitly. Do not silently simulate the missing capability and report success.

Additional infrastructure is justified only after a concrete Work-native failure is demonstrated.
