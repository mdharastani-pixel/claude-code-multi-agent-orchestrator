---
name: adaptive-multi-agent
description: Use when a task has several separable parts, when the user asks for multiple agents, an agent team or parallel work, when any subagent is about to be started, when a model or effort level (reasoning depth) must be chosen for an agent, when routine work would run on the largest model, when a subagent says its part needs a stronger model, or when the user wants to save tokens.
---

# Adaptive Multi-Agent

Goal: save tokens and maximize results. Every part runs on the cheapest model and the lowest effort that do it reliably, and nothing counts as done without a check.

Like an orchestra: the user talks only to the conductor (main session on Fable 5.2 or Opus 5.5). The conductor splits, assigns, integrates and verifies; the agents play the work. Both agree on model and effort: the conductor proposes them, the agent rates its own part and reports the model and effort it needs, the conductor applies them. Only the conductor can set model and effort, and only when starting an agent.

Local rules on model choice or the number of parallel agents (CLAUDE.md, other skills) take precedence. If a file `local.md` lies next to this file, read it first: its rules apply in addition and win.

## Short path

1. Small task (about three tool calls): do it yourself, no agent.
2. Otherwise: split into parts with separate files, give each agent a name, a `model`, an `effort` and the brief block.
3. Read each ASSESSMENT, restart only on ESCALATE, verify, report who ran on what.

## What holds technically (Claude Code, verified with 2.1.330)

- `model` in the Agent call: `haiku`, `sonnet`, `opus`, `fable`. The value in the call beats the agent definition, `CLAUDE_CODE_SUBAGENT_MODEL` and the main model. Without it the agent usually runs on the expensive main model.
- `effort` in the Agent call: `low`, `medium`, `high`, `xhigh`, `max`: how much the agent thinks before it acts. Each step up costs more thinking tokens. Without it the agent runs at its default effort.
- A running agent cannot change its model or effort. `SendMessage` continues it on both unchanged. Changing either always means a new agent with a handover.
- `subagent_type: "fork"` inherits the main model and effort and ignores `model` and `effort`.
- Several Agent calls in one message run concurrently.

## Flow: fixed order

The phases always run in this order. None is skipped; a small task just passes through them faster.

1. **State**: goal and acceptance checks in one to three sentences. Look at the real state (files, tests), do not assume it from notes.
2. **Do it or delegate**: up to about three tool calls, or when the brief would be longer than the work: do it yourself, no agent. Every agent start costs a fixed base of tokens (system context, reading in); delegating pays off only when the work would otherwise fill the conductor's context or can run in parallel.
3. **Plan**: parts with their own result and their own files, numbered and ordered in waves. First whatever blocks others (bugs, missing foundations), then the rest. Split mixed parts by kind of work (research first, then building), not by topic. No two agents write to the same file.
4. **Cast**: per part a name, a provisional tier and effort from the tables, `model` and `effort` always set, a brief built from the block below.
5. **Run in waves**: start all parts of a wave in one message (at most four at once). The next wave starts only after the previous one is evaluated: read the self-assessment, restart on `ESCALATE`, decide or ask the user on `CLARIFY`.
6. **Verify**: tests, sources, an independent reviewer for hard parts. Defects go back to phase 5 as a new wave.
7. **Report**: merge results, resolve contradictions yourself, table with agent and model.

Show the user the plan in short form before phase 5 (wave, agent, part, model, effort) and start without asking, unless a step is irreversible. A `fable` agent appears there with its reason in one sentence.

## Example

Task: "Add CSV export to the invoice tool, document it, and fix the failing rounding tests."

| Wave | Agent | Part | Score | Model | Effort |
|---|---|---|---|---|---|
| 1 | Violin 1 | export module with tests, new files only | 1+0+1+1+1 = 4 | `sonnet` | `medium` (2) |
| 1 | Harp | API section in the README | 0+0+1+1+1 = 3 | `haiku` | `low` (1) |
| 1 | Cello | rounding bug in money code | 1+2+1+2+2 = 8 | `opus` | `high` (5) |
| 2 | Timpani | independent review of the rounding fix | – | `sonnet` | `high` (reviewer) |

Cello finds that one test contradicts the written rounding rule and answers CLARIFY. The conductor decides the rule wins, puts that into the next brief, and Cello finishes. Timpani recomputes the amounts and reports a missing test. The conductor adds it, runs the tests and reports.

Weak version of the same job: three agents without `model` or `effort` (all on the main model at its default effort), the bug fix accepted on the author's word.

## Tiers

0 to 2 points per criterion: size and complexity, uncertainty and missing context, dependencies, consequences of an error, verification needed.

| Sum | Tier | `model` |
|---|---|---|
| 0 to 3 | easy | `haiku` |
| 4 to 6 | medium | `sonnet` |
| 7 to 10 | hard | `opus` |
| `opus` demonstrably failed, or the core of the whole task (see below) | top | `fable` |

Always the cheapest model that reliably reaches the quality. "Important" or "urgent" does not raise the tier. Consequences of an error = 2 (money, customer data, production, irreversible): at least `sonnet` plus an independent review. If a part fits two tiers: split it, so the expensive piece stays small. If a model is not available: take the next available one below it and say so once in the report.

`fable` is used without asking when the part really needs it: `opus` demonstrably failed on this part despite a good handover, or the part is the core everything else depends on, scores 9 or 10, and an error has consequences 2. Then one `fable` agent at a time, its part cut as small as possible, its reason in one sentence in the plan.

Effort comes from three of the five criteria: size and complexity + uncertainty + verification needed (0 to 6 thinking points).

| Thinking points | `effort` |
|---|---|
| 0 to 1 | `low` |
| 2 to 3 | `medium` |
| 4 to 5 | `high` |
| 6 | `xhigh` |
| last escalation step, or the user asks for it | `max` |

Model and effort are two separate levers: the model decides what an agent can do at all, the effort how carefully it works through it. Mechanical work (reading, counting, moving, formatting) stays at `low` on any model. Independent reviewers run at least at `high`.

Conductor on Fable 5.2 or Opus 5.5: the main session is the most expensive tier. It plans, writes briefs, decides and spot-checks; reading, searching, counting and executing a finished plan are delegated. `fable` as an agent is the exception, not a replacement for `opus`. If `fable` is not available in the account, the ladder ends at `opus` and the conductor takes over above it.

## Names in the orchestra

Every agent gets a name by role; several of the same kind are numbered (Violin 1, Violin 2). The name goes at the start of `description` ("Violin 1: CSV export"), into the brief ("You are Violin 1") and into the report, so the user sees who plays what. A restarted agent keeps its name and gets the new model next to it ("Cello, restarted on `opus` at `high`").

| Role | Name |
|---|---|
| Reading, searching, counting | Flute |
| Research, sources | Clarinet |
| Building, code, uploads | Violin |
| Writing, docs | Harp |
| Hard core, architecture, debugging | Cello |
| Independent review | Timpani |

## Brief block

Every brief contains: goal, what is already settled, exact files or folders (and what is off limits), expected result, acceptance checks. Plus, verbatim:

```
You are <name>. You run on the model: <haiku|sonnet|opus|fable> at effort: <low|medium|high|xhigh|max>.
You cannot change them yourself.
Step 1, before any change: read what you need and rate ONLY your own part,
not the project around it. Five criteria, 0-2 points each:
1 size and complexity, 2 uncertainty, 3 dependencies,
4 consequences if YOUR result is wrong, 5 verification needed.
Sum 0-3 = haiku, 4-6 = sonnet, 7-10 = opus.
Effort from criteria 1+2+5: 0-1 = low, 2-3 = medium, 4-5 = high, 6 = xhigh.
If the model or effort you need is above yours: change nothing, STATUS ESCALATE.
If you cannot satisfy two requirements at once: change nothing about them, STATUS CLARIFY.
If the same error remains after two attempts: STATUS ESCALATE.
Bugs or contradictions outside your part do not stop you: finish your work
and list them under "Side finding".

Your answer always starts with:
ASSESSMENT: <five scores> = <sum> -> needed: <model>, <effort>; I run on: <model>, <effort>
STATUS: DONE | ESCALATE | CLARIFY
DONE: result, changed files, how verified (command + output), what is only assumed
and not verified, side finding.
ESCALATE: goal, findings (file:line), what was tried and why it failed,
possible directions, open points, requested model and effort, the reason in one sentence.
CLARIFY: the two requirements (file:line), what each choice means, your recommendation.
Answer briefly: result and evidence only, no file contents, no retelling of the brief.
```

## Escalation and downgrade

- **Agent reports ESCALATE**: start a new agent on the requested model and effort, at most one step above the need. The brief carries the ESCALATE block as handover, so nothing is read twice. If the first agent left files half changed: settle the state first.
- **Effort or model?** The model was capable but worked too shallowly (missed a case, skipped a check, logic half right): restart on the same model one effort step higher, that is cheaper than a bigger model. It lacked capability (did not understand the code, same error at `high`): one tier higher, effort at least `high`. Both count as an escalation.
- **Agent reports CLARIFY**: a contradiction in the requirements needs a decision, not a stronger model. The conductor decides or asks the user; the decision goes into the next brief.
- **Cross-check an escalation**: if the reported score does not fit the part (say, high "consequences" for a pure description), do not start higher; sharpen the brief instead.
- **At most two escalations** per part. If the higher tier fails too, the part is usually cut wrong, not the model too weak: split it again. After that the conductor takes over or asks the user. Never repeat the same brief unchanged on the same model.
- **Finished agents get no new task.** `SendMessage` only for unfinished or missing things. A message reaches a running agent only when it pauses: everything it needs belongs in the first brief.
- **ASSESSMENT line missing**: ask for just that line via `SendMessage`, do not restart.
- **Agent reports a lower tier or effort**: let it finish, do not restart. Lower the tier for the next similar parts.
- The report says "restarted on `opus`", never "switched model".

## Long tasks: state in a file

With more than two waves, or when the work may outlive a session, the conductor keeps a state file `.orchestra/<task>.md` in the project: goal and acceptance checks, plan with waves, per part the agent, model, effort and status, decisions from CLARIFY, escalations. It updates the file after every wave. After an interruption or context compaction it reads this file first and continues from there. Agents write large results to files and report only the path.

## Saving tokens

- The conductor does not read files an agent can read. It receives conclusions, not excerpts.
- Briefs name paths instead of pasting contents. Handovers are the ESCALATE block, not the whole history.
- Every restart pays for reading in again: restart only on ESCALATE, never to downgrade.
- One agent with a clear brief is cheaper than two with overlapping ones. No agent "just to be safe".
- Effort costs too: every step up means more thinking tokens. `low` for mechanical work, `max` only on the last escalation step.
- The independent reviewer runs only for hard or high-consequence parts; otherwise the test run is enough.

## Verification

A self-assessment or "DONE" is not proof. The conductor runs the tests, reads the output or checks sources itself. It compares the changed files with the allowed ones (in Git: `git diff --name-only`). For hard or high-consequence parts an **independent agent** reviews (freshly started, not the author, at least `sonnet`): it gets the goal, the acceptance checks and the result, not the author's reasoning, and is told to attack assumptions and hunt for failure cases.

## Report

| Agent | Part | Provisional | Self-assessment | Ran on (model, effort) | Check |
|---|---|---|---|---|---|

Plus: the result, what was checked and how, what is open. The report ends with one line: "Not checked: ..." (or "Not checked: nothing").

## Excuses and what to do instead

| Excuse | Right |
|---|---|
| "I'll leave `model` out, the default is fine" | always set it; the default is the expensive main model |
| "I'll leave `effort` out" | always set it; routine at the default effort burns thinking tokens |
| "Opus for everything, to be safe" | tier from the score; safety comes from the check, not the model |
| "`max` effort everywhere, to be safe" | effort from the thinking points; `max` only on the last escalation step |
| "It is important, so `fable`" | `fable` only by its rule: `opus` failed, or the 9-10 core with consequences 2 |
| "I'll just message the agent to think harder" | a running agent keeps its model; new agent with handover |
| "Delegating is cleaner" for a three-call job | do it yourself; every agent start costs a fixed base |
| "They won't collide" with two agents on one file | separate files per agent, or run in sequence |
| "The reviewer should know why the author did it" | goal, checks and result only |
| "One more escalation will do it" (the third) | the part is cut wrong: split it, take over or ask |
| "The agent said DONE" | run the check yourself |
