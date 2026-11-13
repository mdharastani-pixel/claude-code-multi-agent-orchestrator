# adaptive-multi-agent

**Save tokens. Maximize results.** A Claude Code skill that turns your main session into a conductor: it splits the task, hands each part to a named subagent, and puts every part on the cheapest model that does it reliably (Haiku, Sonnet, Opus or Fable).

Most multi-agent setups pick the model up front and hope. Here the agents take part in the decision: each one rates its own part first and tells the conductor which model it really needs. Too hard for its model? It changes nothing and hands over. Easier than expected? The next similar part runs one tier lower.

One Markdown file. No scripts, no dependencies, no API keys.

## What it looks like

Plan the conductor shows before it starts (from a real test run on a small billing library):

| Wave | Agent | Part | Model |
|---|---|---|---|
| 1 | Violin 1 | CSV export module with tests | `sonnet` |
| 1 | Harp | API section in the README | `haiku` |
| 1 | Cello | Fix rounding bugs in invoice code | `haiku` → restarted on `opus` |
| 2 | Timpani | Independent review of the fix | `sonnet` |

What an agent sends back when the part is above its model:

```
ASSESSMENT: size 1, uncertainty 2, dependencies 1, consequences 2, verification 1 = 7 -> needed: opus; I run on: haiku
STATUS: ESCALATE
Goal: ... Findings: billing.py:6 round() on binary floats ... Attempts: none, nothing changed ...
```

## Install

```bash
mkdir -p ~/.claude/skills/adaptive-multi-agent
curl -fsSL https://raw.githubusercontent.com/mdharastani-pixel/adaptive-multi-agent/main/SKILL.md \
  -o ~/.claude/skills/adaptive-multi-agent/SKILL.md
```

Deutsche Fassung: replace `main/SKILL.md` with `main/de/SKILL.md`.

Claude Code picks the skill up in the running session.

## Use

```
/adaptive-multi-agent Build the CSV export and document the API
```

Or just say it: "use an agent team for this", "arbeite mit mehreren Agenten".

## How it works

**1. Fixed order, GSD style.** State → do it or delegate → plan → cast → run in waves → verify → report. Blocking work goes first. The next wave starts only after the previous one is evaluated. Small tasks are done directly, without any agent.

**2. Agents rate their own part.** Five criteria, 0-2 points each: size and complexity, uncertainty, dependencies, consequences of an error, verification needed.

| Score | Tier | `model` |
|---|---|---|
| 0-3 | easy | `haiku` |
| 4-6 | medium | `sonnet` |
| 7-10 | hard | `opus` |
| `opus` failed, or the core of the whole task | top | `fable` |

**3. Three possible answers.** `DONE` with evidence. `ESCALATE` with a handover block, so the stronger agent does not read everything again. `CLARIFY` when two requirements contradict each other, because that needs a decision and not a bigger model.

**4. Names.** Flute reads, Clarinet researches, Violin builds, Harp writes, Cello solves the hard core, Timpani reviews. You always see who plays what, and on which model.

**5. Nothing is done without a check.** The conductor runs the tests itself. Hard or risky parts get an independent reviewer that sees the result but not the author's reasoning.

**6. Token rules.** The conductor does not read what an agent can read. Briefs name paths instead of pasting contents. Restarts happen only on escalation, never to downgrade. At most two escalations per part.

## Tested

Run with Claude Code 2.1.323, conductor on Fable 5.2, on a small invoice library with planted bugs.

| Case | What happened |
|---|---|
| Easy lookup | done directly, no agent started |
| Medium, two parts | ran in parallel in separate files on `sonnet` and `haiku`; the `sonnet` agent reported that `haiku` would have been enough |
| Hard, started too low on purpose | `haiku` agent scored 7, changed nothing, returned a handover; restarted on `opus`, all tests green |
| Independent review | `sonnet` reviewer recomputed 3,000 random invoices, found the math correct and one missing test |

Testing also found weak spots in the first draft (an agent escalating over bugs outside its part, a missing assessment line). Both are fixed in the brief block. The orchestra names and the fixed phase order were added after these runs.

## Limits

- A running subagent cannot change its own model. "Switching" always means a new agent with a handover.
- `SendMessage` continues an agent on the same model.
- `subagent_type: "fork"` inherits the main model and ignores `model`.
- Only Claude models. The skill does not call other providers.
- The self-assessment is a signal, not proof. That is why the check is a separate step.

## Safety

The skill is plain instructions in one Markdown file. No scripts, no network calls, no credentials, no telemetry. Read it before you install it; it takes two minutes.

## Keywords

Claude Code skill, SKILL.md, agent skills, subagents, multi-agent orchestration, orchestrator and workers, conductor, model routing, model selection, Haiku, Sonnet, Opus, Fable, escalation, handover, token saving, cost optimization, GSD workflow.

## Deutsch

Ein Skill für Claude Code. Du sprichst nur mit dem Dirigenten (Fable 5.2 oder Opus 5.5). Er zerlegt die Aufgabe, gibt jedem Agenten einen Namen und stimmt mit ihm das Modell ab: Jeder Agent schätzt seine Teilaufgabe selbst ein und meldet, welches Modell er braucht. So läuft nur der schwere Teil auf dem teuren Modell. Die deutsche Fassung liegt in [`de/SKILL.md`](de/SKILL.md).

## License

MIT
