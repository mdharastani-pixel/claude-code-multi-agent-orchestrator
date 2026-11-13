# Tests

`check_skill.py` is a static check that runs in CI: both editions keep the required lines of the brief block, the tier table and the same sections, and the fixture still fails as planted.

The behaviour test needs Claude Code and is run by hand. `fixture/` is a tiny invoice library with planted bugs: float rounding, lost cents in instalments, and one test that contradicts the README rule.

| Case | Prompt | Expected |
|---|---|---|
| Easy | "How many test functions are in tests/fixture?" | answered directly, no agent |
| Medium | "Add an export module with tests and an API section to the fixture README" | two agents in one wave, separate files, both report ASSESSMENT |
| Hard | "Fix the failing billing tests", first agent started on `haiku` on purpose | agent changes nothing and returns ESCALATE or CLARIFY with a handover; restart on the requested model; independent review afterwards |

Copy the fixture before each run, because the agents change it.
