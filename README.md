# adaptive-multi-agent

**Claude Code skill for multi-agent orchestration with adaptive model routing (Haiku / Sonnet / Opus / Fable) to save tokens.**

A Claude Code skill. The main session acts as a conductor (built for Claude Fable 5.2 or Opus 5.5): it splits a task, hands the parts to subagents, and agrees the model with each of them. Every subagent rates its own part and reports which model it needs. The conductor starts or restarts agents on the cheapest model that does the job reliably.

Ein Claude-Code-Skill. Die Hauptsitzung arbeitet als Dirigent (gebaut für Claude Fable 5.2 oder Opus 5.5): Sie zerlegt die Aufgabe, gibt die Teile an Agenten und stimmt mit jedem das Modell ab. Jeder Agent schätzt seine Teilaufgabe selbst ein und meldet, welches Modell er braucht. Das spart Token, weil nur der schwere Teil auf dem teuren Modell läuft.

## Install

```bash
mkdir -p ~/.claude/skills/adaptive-multi-agent
curl -fsSL https://raw.githubusercontent.com/mdharastani-pixel/adaptive-multi-agent/main/SKILL.md \
  -o ~/.claude/skills/adaptive-multi-agent/SKILL.md
```

Claude Code picks it up in the running session. Tested with Claude Code 2.1.323.

## Use

```
/adaptive-multi-agent Baue den CSV-Export und dokumentiere die API
```

Or just ask for it: "arbeite mit mehreren Agenten", "use an agent team for this".

## How it works

| Score (5 criteria, 0-2 each) | Tier | `model` |
|---|---|---|
| 0-3 | easy | `haiku` |
| 4-6 | medium | `sonnet` |
| 7-10 | hard | `opus` |
| `opus` failed, or the core of the whole task | top | `fable` |

- Every agent gets an orchestra name by role (Flöte reads, Geige builds, Cello solves the hard core, Pauke reviews), so you can see who plays what.
- The conductor picks a provisional model. The agent rates its own part first and answers with `EINSCHÄTZUNG` and `STATUS`.
- If the task needs a stronger model, the agent changes nothing and returns an `ESKALATION` block. The conductor starts a new agent on the stronger model with that block as handover.
- If two requirements contradict each other, the agent returns `KLÄRUNG`. That needs a decision, not a bigger model.
- Results are checked with tests or sources. Hard or risky parts get an independent reviewer agent.

## Keywords

Claude Code skill, SKILL.md, agent skills, subagents, multi-agent orchestration, orchestrator and workers, model routing, model selection, Haiku, Sonnet, Opus, Fable, escalation, handover, token saving, cost optimization.

## Limits

- A running subagent cannot change its own model. "Switching" always means a new agent with a handover.
- `SendMessage` continues an agent on the same model.
- `subagent_type: "fork"` inherits the main model and ignores `model`.
- The skill text is German. Claude follows it in any language.

## Safety

The skill is one Markdown file with instructions. It has no scripts, no network calls, no credentials and no file paths from the author's machine. Installing it gives nobody access to your data, and publishing it gives nobody access to the author's.

## License

MIT
