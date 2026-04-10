---
description: End-of-day evidence-based work review and tomorrow brief
allowed-tools: Read, Edit, Glob, Bash
---

Run the **agent-reflect-and-learn** skill end-to-end for **today’s local calendar date** in the active git repository (use the workspace root the user is working in unless they name another `--repo`).

1. Follow `skills/agent-reflect-and-learn/SKILL.md` in order: **if `.agent-reflect-and-learn/config.json` is missing or has no `artifactsPath`, ask the user where to store artifacts** (recommend default `artifacts`), then create the file with **`jq`** as in the skill. Collect evidence with the collector script, reconstruct the day, scan mistakes and friction, apply the rubric, then write the markdown report and improvement-actions JSON using the bundled template (paths under the configured artifacts directory).
2. Use `python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/..."` for collector and push steps as documented in the skill (collector/push read `artifactsPath` from config when `--out` / `--artifacts-dir` are omitted).
3. If the user gave a specific date (`YYYY-MM-DD`), use that instead of today.

Do not skip the evidence-collection step; prefer the evidence packet over memory.
