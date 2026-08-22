# Gate 0B — Full Disclosure and Consequential Debate Test

This is a capability test of ChatGPT Work. Use actual separate subagents/workstreams. Do not simulate four personas inside a single response. If the required delegation or context-sharing behavior is unavailable, say so and mark the relevant capability FAIL.

## Shared decision

A fictional company, Northstar Systems, has built a promising internal AI planning product. Leadership must choose among:

- **Option A — Commercial Launch:** launch publicly within 60 days.
- **Option B — Internal Validation:** keep it internal for six more months.
- **Option C — Limited Pilot:** run a three-month paid pilot with five selected customers before deciding on broad launch.

## Phase 1 — Independent subagents

Create four actual independent subagents/workstreams: A, B, C, and D.

Give every agent the shared decision above and exactly one private fact:

- **Agent A:** Public deployment would require approximately four months of architectural rework.
- **Agent B:** A well-funded competitor is expected to announce a similar commercial product in approximately four months.
- **Agent C:** Northstar currently has only two engineers available to support this product for the next five months.
- **Agent D:** The product has experienced three severe hallucination incidents during the last 100 internal planning sessions.

During this phase, no agent may see another agent's private fact or another agent's analysis.

Ask each agent for:

1. recommendation;
2. reasoning;
3. important risks or assumptions;
4. the fact it was given.

Preserve all four complete initial proposals before continuing.

## Phase 2 — Open the chamber

Only after all four initial proposals are complete, give **every one of the same four subagents**:

- all four complete initial proposals, not summaries;
- all four private facts;
- the original shared decision.

Tell each agent that the independent phase is over and they are now participating in a shared Council discussion.

## Phase 3 — Opening Council

Ask each subagent to read all four complete proposals and address the Council.

Do not assign debate topics, sides, or opponents.

Each agent must decide for itself what deserves engagement. It may:

- challenge another agent's reasoning;
- support or defend another agent;
- strengthen an argument it did not originate;
- distinguish between parts of another proposal;
- expose a shared assumption;
- concede a point;
- revise its own recommendation;
- or propose a synthesis.

Require agents to refer to specific arguments made by other agents rather than merely restating their own proposal.

Preserve all four opening Council responses.

## Phase 4 — Rebuttal round

Give every subagent:

- all four initial proposals;
- all four opening Council responses;
- all four facts;
- the complete Council discussion so far.

Ask each to respond again only if it has something material to add.

A material contribution includes:

- answering a challenge directed at its position;
- challenging a consequential argument that remains unanswered;
- defending another agent against a criticism;
- changing or refining its own position;
- strengthening a proposal with new reasoning;
- or proposing a better synthesis.

Mere repetition or generic agreement is not useful.

Do not force disagreement. Agents may agree or form temporary alliances around particular arguments.

## Phase 5 — Capability report

Do not vote or produce a final Northstar plan yet. This test ends after the rebuttal round.

Return the complete initial proposals, opening Council responses, and rebuttal responses, then provide this report:

| Capability | PASS / FAIL | Evidence |
|---|---|---|
| Four actual independent subagents/workstreams were used | | |
| Initial private context remained isolated | | |
| The same subagents received all complete proposals after disclosure | | |
| Each subagent could reason over the other agents' actual proposals | | |
| Agents selected their own debate issues | | |
| Agents directly challenged specific arguments | | |
| Agents could support or defend another agent | | |
| The rebuttal round used the complete prior Council discussion | | |
| At least one argument was defended, refined, conceded, revised, combined, or materially strengthened | | |
| The discussion was meaningfully different from four parallel summaries | | |

Finally answer explicitly:

1. Were the same four actual delegated subagents used before and after disclosure?
2. During Phase 1, could any subagent access another subagent's private fact or proposal?
3. After Phase 2, could every subagent access every complete proposal and all shared facts?
4. Did any subagent directly change, refine, defend, or challenge a position because of another subagent's argument? Cite the clearest examples.
5. Based on this test, can ChatGPT Work support the Imperial Council transition from independent counsel to genuine shared debate?

Do not claim a capability that was not actually exercised during this run.
