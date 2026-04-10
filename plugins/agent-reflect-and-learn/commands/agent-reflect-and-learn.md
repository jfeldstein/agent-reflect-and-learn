---
description: End-of-day evidence-based work review and tomorrow brief
allowed-tools: Read, Edit, Glob, Bash
---

Run the **agent-reflect-and-learn** skill for **today’s local calendar date** in the active git repository (workspace root unless the user names another `--repo`).

1. The skill is **orchestration-only**: follow `skills/agent-reflect-and-learn/SKILL.md` by delegating the full workflow to the **`agent-reflect-daily`** subagent (`agents/agent-reflect-daily.md`). Do not run the collector, write review files, or push from the parent agent—only spawn the subagent and return its result.
2. If the user gave a specific date (`YYYY-MM-DD`), pass that to the subagent context so collector and outputs use that date.
3. Subagent uses `python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/..."` for collector and push per `agents/agent-reflect-daily.md`.

Do not skip the evidence-collection step inside the subagent; prefer the evidence packet over memory.
