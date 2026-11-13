---
name: adaptive-multi-agent
description: Use when a task has several separable parts, when the user asks for multiple agents, an agent team, parallel work or specialised subagents, when subagents should rate their own difficulty and pick or change their model, or when a subagent reports that its part is harder than expected, keeps failing, or needs a stronger model.
---

# Adaptive Multi-Agent

Goal: save tokens and maximize results. Every part runs on the cheapest model that does it reliably, and nothing counts as done without a check.

Like an orchestra: the user talks only to the conductor (main session on Fable 5.2 or Opus 5.5). The conductor splits, assigns, integrates and verifies; the agents play the work. Both agree on the model: the conductor proposes a tier, the agent rates its own part and reports the tier it needs, the conductor applies it. Only the conductor can set a model, and only when starting an agent.

Local rules on model choice or the number of parallel agents (CLAUDE.md, other skills) take precedence.

## What holds technically (Claude Code, verified with 2.1.323)

- `model` in the Agent call: `haiku`, `sonnet`, `opus`, `fable`. The value in the call beats the agent definition, `CLAUDE_CODE_SUBAGENT_MODEL` and the main model. Without it the agent usually runs on the expensive main model.
- A running agent cannot change its model. `SendMessage` continues it on the same model. Changing tier always means a new agent with a handover.
- `subagent_type: "fork"` inherits the main model and ignores `model`.
- Several Agent calls in one message run concurrently.

## Flow: fixed order

The phases always run in this order. None is skipped; a small task just passes through them faster.

1. **State**: goal and acceptance checks in one to three sentences. Look at the real state (files, tests), do not assume it from notes.
2. **Do it or delegate**: up to about three tool calls, or when the brief would be longer than the work: do it yourself, no agent. Every agent start costs a fixed base of tokens (system context, reading in); delegating pays off only when the work would otherwise fill the conductor's context or can run in parallel.
3. **Plan**: parts with their own result and their own files, numbered and ordered in waves. First whatever blocks others (bugs, missing foundations), then the rest. Split mixed parts by kind of work (research first, then building), not by topic. No two agents write to the same file.
4. **Cast**: per part a name, a provisional tier from the table, `model` always set, a brief built from the block below.
5. **Run in waves**: start all parts of a wave in one message (at most four at once). The next wave starts only after the previous one is evaluated: read the self-assessment, restart on `ESCALATE`, decide or ask the user on `CLARIFY`.
6. **Verify**: tests, sources, an independent reviewer for hard parts. Defects go back to phase 5 as a new wave.
7. **Report**: merge results, resolve contradictions yourself, table with agent and model.

Show the user the plan in short form before phase 5 (wave, agent, part, model) and start without asking, unless a step is irreversible.

## Tiers

0 to 2 points per criterion: size and complexity, uncertainty and missing context, dependencies, consequences of an error, verification needed.

| Sum | Tier | `model` |
|---|---|---|
| 0 to 3 | easy | `haiku` |
| 4 to 6 | medium | `sonnet` |
| 7 to 10 | hard | `opus` |
| `opus` demonstrably failed, or the core of the whole task | top | `fable` |

Always the cheapest model that reliably reaches the quality. "Important" or "urgent" does not raise the tier. Consequences of an error = 2 (money, customer data, production, irreversible): at least `sonnet` plus an independent review. If a part fits two tiers: split it, so the expensive piece stays small. If a model is not available: take the next available one below it and say so once in the report. Ask the user before starting a `fable` agent.

Conductor on Fable 5.2 or Opus 5.5: the main session is the most expensive tier. It plans, writes briefs, decides and spot-checks; reading, searching, counting and executing a finished plan are delegated. `fable` as an agent is the exception, not a replacement for `opus`. If `fable` is not available in the account, the ladder ends at `opus` and the conductor takes over above it.

## Names in the orchestra

Every agent gets a name by role; several of the same kind are numbered (Violin 1, Violin 2). The name goes at the start of `description` ("Violin 1: CSV export"), into the brief ("You are Violin 1") and into the report, so the user sees who plays what. A restarted agent keeps its name and gets the new model next to it ("Cello, restarted on `opus`").

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
You are <name>. You run on the model: <haiku|sonnet|opus|fable>. You cannot change it yourself.
Step 1, before any change: read what you need and rate ONLY your own part,
not the project around it. Five criteria, 0-2 points each:
1 size and complexity, 2 uncertainty, 3 dependencies,
4 consequences if YOUR result is wrong, 5 verification needed.
Sum 0-3 = haiku, 4-6 = sonnet, 7-10 = opus.
If the tier you need is above your model: change nothing, STATUS ESCALATE.
If you cannot satisfy two requirements at once: change nothing about them, STATUS CLARIFY.
If the same error remains after two attempts: STATUS ESCALATE.
Bugs or contradictions outside your part do not stop you: finish your work
and list them under "Side finding".

Your answer always starts with:
ASSESSMENT: <five scores> = <sum> -> needed: <model>; I run on: <model>
STATUS: DONE | ESCALATE | CLARIFY
DONE: result, changed files, how verified (command + output), what is only assumed
and not verified, side finding.
ESCALATE: goal, findings (file:line), what was tried and why it failed,
possible directions, open points, requested model and the reason in one sentence.
CLARIFY: the two requirements (file:line), what each choice means, your recommendation.
Answer briefly: result and evidence only, no file contents, no retelling of the brief.
```

## Escalation and downgrade

- **Agent reports ESCALATE**: start a new agent on the requested model, at most one tier above the need per step. The brief carries the ESCALATE block as handover, so nothing is read twice. If the first agent left files half changed: settle the state first.
- **Agent reports CLARIFY**: a contradiction in the requirements needs a decision, not a stronger model. The conductor decides or asks the user; the decision goes into the next brief.
- **Cross-check an escalation**: if the reported score does not fit the part (say, high "consequences" for a pure description), do not start higher; sharpen the brief instead.
- **At most two escalations** per part. If the higher tier fails too, the part is usually cut wrong, not the model too weak: split it again. After that the conductor takes over or asks the user. Never repeat the same brief unchanged on the same model.
- **Finished agents get no new task.** `SendMessage` only for unfinished or missing things. A message reaches a running agent only when it pauses: everything it needs belongs in the first brief.
- **ASSESSMENT line missing**: ask for just that line via `SendMessage`, do not restart.
- **Agent reports a lower tier**: let it finish, do not restart. Lower the tier for the next similar parts.
- The report says "restarted on `opus`", never "switched model".

## Long tasks: state in a file

With more than two waves, or when the work may outlive a session, the conductor keeps a state file `.orchestra/<task>.md` in the project: goal and acceptance checks, plan with waves, per part the agent, model and status, decisions from CLARIFY, escalations. It updates the file after every wave. After an interruption or context compaction it reads this file first and continues from there. Agents write large results to files and report only the path.

## Saving tokens

- The conductor does not read files an agent can read. It receives conclusions, not excerpts.
- Briefs name paths instead of pasting contents. Handovers are the ESCALATE block, not the whole history.
- Every restart pays for reading in again: restart only on ESCALATE, never to downgrade.
- One agent with a clear brief is cheaper than two with overlapping ones. No agent "just to be safe".
- The independent reviewer runs only for hard or high-consequence parts; otherwise the test run is enough.

## Verification

A self-assessment or "DONE" is not proof. The conductor runs the tests, reads the output or checks sources itself. It compares the changed files with the allowed ones (in Git: `git diff --name-only`). For hard or high-consequence parts an **independent agent** reviews (freshly started, not the author, at least `sonnet`): it gets the goal, the acceptance checks and the result, not the author's reasoning, and is told to attack assumptions and hunt for failure cases.

## Report

| Agent | Part | Provisional | Self-assessment | Ran on | Check |
|---|---|---|---|---|---|

Plus: the result, what was checked and how, what is open.

## Common mistakes

| Mistake | Right |
|---|---|
| `model` left out | always set it |
| Everything on the strongest model, "to be safe" | tier from the score |
| "Upgrading" an agent via `SendMessage` | new agent with handover |
| Small task delegated | do it yourself |
| Two agents on the same file | separate files per agent, or run in sequence |
| Reviewer gets the author's reasoning | goal, checks and result only |
| Third escalation | conductor takes over or asks |
