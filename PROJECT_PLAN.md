# Imperial Council — Initial Implementation Plan

## 1. Objective

Build the smallest implementation capable of testing the Imperial Council's central hypothesis:

> Several independently reasoning strategic advisers with persistent value differences, full post-independence visibility into one another's proposals, consequential debate, and a definitive decision process can produce better actionable plans than a single capable adviser.

The initial implementation will run **inside ChatGPT Work**.

It will **not** begin as an API orchestration service.

The repository will contain the durable instructions, Council profiles, protocol, evaluation cases, and supporting artifacts used to configure and test the Council in ChatGPT Work.

---

## 2. What We Are Building

### User-facing product

**Imperial Council**

### Initial ChatGPT packaging

**Imperial Council Workspace Agent**

The Workspace Agent is the user-facing entry point in ChatGPT Work. The Sovereign manually invokes it when a problem merits Council deliberation.

### Core behavior package

**Imperial Council Skill**

The Skill contains the reusable deliberation procedure, information-boundary rules, debate rules, voting rules, final-plan requirements, and references to the persistent Council member profiles.

### Supporting files

Persistent member profiles, value vocabulary, protocol references, output contract, and evaluation cases live in the repository and are attached to or incorporated into the Workspace Agent/Skill as appropriate.

### What this is not in v1

The initial implementation is not:

- a standalone web application;
- an API service;
- a custom MCP server;
- a database-backed agent platform;
- a plugin requiring an external app;
- or a custom orchestration engine.

A plugin may later be used as the installation/distribution container for the Imperial Council Skill. An app or MCP service should be added only if a Work-native implementation demonstrates a concrete limitation that cannot be solved reliably with instructions, files, Skills, or native Work delegation.

---

## 3. Primary Architecture

The target v1 architecture is intentionally thin:

```text
Sovereign
   |
   | explicitly invokes
   v
Imperial Council Workspace Agent
   |
   | uses
   v
Imperial Council Skill
   |
   +-- Council protocol
   +-- value vocabulary
   +-- persistent member profiles
   +-- final output contract
   +-- evaluation rules
   |
   | delegates independent reasoning and debate work
   v
ChatGPT Work native execution/delegation
   |
   v
One definitive Council decision + coherent action plan
```

The most important technical question is not how to build an orchestration framework. It is whether ChatGPT Work can reliably execute the required information boundaries and multi-member deliberation using native capabilities.

That must be tested before additional infrastructure is justified.

---

## 4. Required Deliberation Lifecycle

The initial Skill must enforce this lifecycle.

### Phase 1 — Sovereign Invocation

The user explicitly invokes the Imperial Council.

There is no automatic Council-routing decision in v1.

### Phase 2 — Independent Counsel

Every participating councillor receives:

- the Sovereign's original request;
- the same shared factual context;
- their own persistent Council profile.

They must not receive another councillor's interpretation, proposal, or recommendation during this phase.

Each councillor produces a complete initial strategic proposal.

### Phase 3 — Full Disclosure

Only after every initial proposal is complete, each participating councillor receives:

- every other councillor's complete proposal;
- the original shared context;
- the evolving Council transcript from this point forward.

No Seneschal summary may substitute for the full proposals.

### Phase 4 — Council Opening

Each councillor decides for themselves what deserves engagement.

They may:

- challenge another member;
- defend another member;
- support a position they independently reached;
- attack an assumption shared by several members;
- extend another proposal;
- distinguish between parts of a proposal;
- concede a point;
- revise their own strategy;
- or propose a synthesis.

The Seneschal does not pre-select the debate agenda.

### Phase 5 — Open Debate

All participating councillors can see the complete deliberative record available to the Council after the disclosure boundary opens.

Debate continues while new material reasoning is being contributed.

The system should favor natural argument over rigid machine-like contention forms.

Structured records may describe the debate after it occurs, but they must not constrain what councillors are allowed to argue.

### Phase 6 — Call for Vote

Any councillor may call for a vote when they believe additional debate is no longer materially improving the strategy.

Every member then receives one opportunity to identify unfinished material reasoning.

Repeated preference or repeated disagreement is not sufficient.

If no unfinished material reasoning is identified, debate closes.

If unfinished material reasoning is claimed, the Council votes by simple majority on whether another exchange is warranted. The Seneschal breaks a procedural tie.

### Phase 7 — Strategic Decision

Debate may terminate through:

- convergence;
- synthesis;
- or vote.

If a strategy vote is required:

- councillors vote on surviving strategies, not necessarily their original proposals;
- a strategy requires a majority;
- runoffs eliminate lower-supported alternatives if necessary;
- the Seneschal breaks a final tie based on the complete deliberative record.

### Phase 8 — Unified Plan

The Seneschal translates the decided strategy into one coherent final plan.

The final output must contain:

1. Council decision;
2. strategic rationale;
3. sequenced action plan;
4. critical assumptions and tradeoffs;
5. decision/change triggers;
6. meaningful minority objections.

The final result must not simply return several competing member recommendations to the Sovereign.

### Phase 9 — Fidelity Review

Council members may identify concrete inconsistencies between the plan and the strategy actually decided.

This is quality control, not another opportunity to reopen a settled strategic vote.

---

## 5. Initial Repository Structure

The repository should remain documentation- and instruction-first until Work-native execution has been validated.

Target structure:

```text
imperium/
|
|-- MANIFESTO.md
|-- PROJECT_PLAN.md
|-- README.md
|
|-- skill/
|   |-- SKILL.md
|   |
|   `-- references/
|       |-- DELIBERATION_PROTOCOL.md
|       |-- VALUE_VOCABULARY.md
|       |-- COUNCIL_PROFILES.md
|       |-- OUTPUT_CONTRACT.md
|       `-- WORK_EXECUTION_RULES.md
|
|-- council/
|   |-- steward.md
|   |-- vanguard.md
|   |-- architect.md
|   `-- castellan.md
|
|-- evals/
|   |-- README.md
|   |-- rubric.md
|   |
|   |-- cases/
|   `-- results/
|
`-- experiments/
    `-- work-native-validation/
```

This structure is provisional until the first Work-native validation gate is complete.

Do not create runtime code simply to make the repository look like an application.

---

## 6. Implementation Sequence

## Gate 0 — Validate ChatGPT Work as the Runtime

Before writing substantial orchestration code, run focused experiments inside ChatGPT Work.

We need evidence that Work can support the central protocol.

### Experiment 0.1 — Independent contexts

Ask Work to produce four separately delegated initial analyses using four distinct Council profiles.

Verify:

- each receives the same Sovereign request and shared context;
- each receives only its own profile;
- each completes its initial proposal before cross-member disclosure;
- no initial proposal appears to be anchored on another member's answer.

### Experiment 0.2 — Full proposal disclosure

After the initial round, provide every member with every complete proposal.

Verify that members can:

- accurately understand other proposals;
- discover their own debate issues rather than being assigned them;
- challenge and defend specific reasoning;
- support another member without abandoning unrelated disagreements.

### Experiment 0.3 — Multi-round identity persistence

Run at least two debate exchanges.

Verify that:

- each member continues to reason from its persistent value profile;
- members remember their own earlier position;
- concessions and revisions remain consistent in later turns;
- the transcript is visible consistently after the chamber opens.

### Experiment 0.4 — Call for vote

Force a case with unresolved disagreement.

Verify that:

- a councillor can call for a vote;
- repeated arguments do not automatically extend debate;
- genuinely new material reasoning can earn another exchange;
- a majority can close debate;
- a strategy vote and runoff can be completed correctly;
- the Seneschal can break a tie when required.

### Experiment 0.5 — Definitive plan synthesis

Verify that the final output is one coherent actionable plan representing the decided Council strategy rather than a summary of all positions.

### Gate 0 exit criteria

Proceed with a Work-native Skill implementation only if these experiments demonstrate that native Work execution is sufficiently reliable to test the Council hypothesis.

If a failure occurs, document the specific limitation before designing infrastructure to solve it.

---

## Gate 1 — Define the Strategic Value Vocabulary

Create a small common vocabulary of strategic values from which member matrices are built.

Requirements:

- values must be behaviorally distinguishable;
- values must represent real strategic tradeoffs;
- all member weights sum to `1.0`;
- values must affect reasoning, not merely voice;
- universal epistemic requirements must not be encoded as competing values.

Deliverable:

`skill/references/VALUE_VOCABULARY.md`

---

## Gate 2 — Define the Initial Council

Create the initial four persistent Council member profiles.

Current working structure:

- **Steward** — practicality, efficiency, sustainable execution;
- **Vanguard** — opportunity, initiative, ambition, speed;
- **Architect** — systemic thinking, long-term coherence, optionality;
- **Castellan** — risk, resilience, downside protection.

These names and matrices remain subject to explicit design review before being treated as final.

Each profile should contain only information that changes reasoning:

- mandate;
- value matrix;
- strategic instincts;
- characteristic blind spots;
- risk tolerance;
- temporal orientation;
- evidence/update rules;
- concise communication tendencies where useful.

Avoid elaborate character lore.

Deliverables:

`council/*.md`

---

## Gate 3 — Write the Deliberation Protocol

Convert the accepted lifecycle into a precise, inspectable protocol.

The protocol must clearly separate:

- private independent reasoning;
- full disclosure;
- open debate;
- call-for-vote behavior;
- strategic voting;
- final-plan synthesis;
- fidelity review.

The protocol should specify information visibility at each stage.

Deliverable:

`skill/references/DELIBERATION_PROTOCOL.md`

---

## Gate 4 — Build the Imperial Council Skill

Create the Work-compatible Skill that instructs ChatGPT how to run a Council session.

The Skill should primarily reference the protocol and member files rather than duplicating them.

It should include:

- invocation intent;
- role of the Sovereign;
- role of the Seneschal;
- delegation rules;
- information-boundary rules;
- debate rules;
- stopping and voting rules;
- final output requirements;
- failure behavior when Work cannot preserve a required boundary.

Deliverable:

`skill/SKILL.md`

---

## Gate 5 — Configure the Workspace Agent

Create the user-facing **Imperial Council Workspace Agent** in ChatGPT Work.

Initial configuration principles:

- manually invoked by the Sovereign;
- uses the Imperial Council Skill;
- includes only necessary supporting files;
- no external apps required initially;
- no custom MCP required initially;
- no API trigger required;
- no scheduled execution;
- no autonomous action authority;
- no broad persistent memory requirement until memory behavior has been specifically evaluated for cross-session contamination or anchoring.

The Workspace Agent should present the Council as a strategic deliberation environment, not an execution bot.

---

## Gate 6 — Evaluation Harness

Create repeatable evaluation cases that can be run in three conditions:

### A — Single Adviser

One capable model receives the request and produces the best strategy it can.

### B — Independent Panel

The same Council members independently analyze the request, but do not debate.

A neutral synthesis produces the final result.

### C — Imperial Council

The full protocol runs:

- independent counsel;
- full disclosure;
- open debate;
- decision closure;
- final coherent plan.

Evaluate outputs blindly where practical.

Primary question:

> Does the full Council produce a materially better strategic plan?

Diagnostic measures may include:

- diversity of initial interpretations;
- value-matrix influence;
- specificity of cross-member engagement;
- concessions and revisions;
- new hybrid strategies;
- meaningful unresolved dissent;
- successful debate termination;
- plan coherence;
- plan actionability.

These diagnostics must not become proxies for the real objective.

---

## 7. Technical Decision Rules

The following rules govern implementation choices.

### Native Work before custom code

If ChatGPT Work can perform a function reliably through instructions, Skills, files, or native delegation, use that capability first.

### Code only when it solves an observed failure

Do not add a Python orchestration engine, database, MCP service, web server, or application framework because such components are conventional in agent systems.

Add them only when a documented Work-native limitation requires them.

### Full proposals before summaries

No optimization may replace full post-independence proposal visibility unless evaluation demonstrates that a reduced representation preserves or improves debate quality.

### Natural debate before rigid schemas

Do not force councillors into mechanical challenge-ticket interactions merely because structured data is easier to inspect.

Record structure may follow natural argument; it should not flatten the argument itself.

### Definitive outcome

Every completed Council session must end with one official Council decision and one coherent action plan.

### Dissent survives, indecision does not

Meaningful minority objections remain visible in the final judgment, but unresolved alternatives are not handed back to the Sovereign as if the Council never decided.

---

## 8. Known Open Questions

These questions should remain open until tested rather than prematurely converted into implementation requirements.

1. Can ChatGPT Work reliably maintain four isolated initial member contexts within one Council run?
2. Can native Work delegation preserve named Council identities across multiple debate rounds?
3. Can each delegated member receive the complete proposals and later transcript without undesirable summarization or truncation?
4. How much transcript growth degrades debate quality or causes context compression?
5. Should the Seneschal itself be a distinct delegated agent or the controlling Workspace Agent role?
6. Should the four initial Council profiles remain fixed for all early evaluation cases or should membership eventually be selected by the Sovereign?
7. What exact shared value vocabulary produces the strongest useful cognitive diversity?
8. How should evaluation score strategic quality without rewarding verbosity or theatrical disagreement?

None of these questions justifies additional infrastructure until evidence shows that it is needed.

---

## 9. Initial Definition of Done

The first meaningful release is complete when the following are true:

- the Imperial Council Workspace Agent can be manually invoked in ChatGPT Work;
- four persistent member profiles produce meaningfully different independent analyses;
- the initial analyses are formed before cross-member disclosure;
- every member can then inspect every full proposal;
- members initiate their own challenges, defenses, alliances, and syntheses;
- debate can alter positions;
- debate terminates when no new material reasoning remains;
- unresolved disagreement can be closed through voting;
- the Seneschal can break ties and produce a definitive outcome;
- the final output is one coherent actionable plan with surviving minority objections;
- the full process can be compared against Single Adviser and Independent Panel baselines;
- and early evaluation provides evidence about whether the Council improves strategic judgment.

Only after this definition of done is met should the project consider broader packaging, external apps, MCP infrastructure, persistence services, execution capabilities, or additional permanent Council members.
