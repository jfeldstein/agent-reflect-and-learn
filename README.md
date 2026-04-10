# agent-reflect-and-learn

Claude Code / Cursor plugin that bundles the **agent-reflect-and-learn** skill (orchestration-only, `disable-model-invocation`) and the **`agent-reflect-daily`** subagent for the full retrospective, plus the slash command **`/agent-reflect-and-learn`**. In Cursor, a **stop** hook can nudge the same skill → subagent flow. Also includes **wisdom-to-content**: learnings → social posts and blog drafts.

## Install (Claude Code)

This repository is a **plugin marketplace** (catalog). Add it, then install the plugin:

```text
/plugin marketplace add jfeldstein/agent-reflect-and-learn
/plugin install agent-reflect-and-learn@agent-reflect-and-learn-plugins
/reload-plugins
```

You can also add a **local clone** while developing:

```text
/plugin marketplace add /path/to/agent-reflect-and-learn
/plugin install agent-reflect-and-learn@agent-reflect-and-learn-plugins
/reload-plugins
```

## Daily scheduled task

Configure a **daily** scheduled task in Claude Code whose prompt is simply:

```text
run /agent-reflect-and-learn
```

Point the task at the repository (or worktree) you want reviewed so `--repo .` and your configured artifacts directory resolve correctly. On first use in that repo, the **subagent** asks where to store artifacts and writes `.agent-reflect-and-learn/config.json` (default `artifactsPath`: `artifacts`).

## Contents

Plugin root: `plugins/agent-reflect-and-learn/` (in this repo; same layout in the install cache after `plugin install`).

- **Command** `/agent-reflect-and-learn` — `commands/agent-reflect-and-learn.md`
- **Skill** `agent-reflect-and-learn` — hook/slash/schedule entrypoint; delegates to the subagent (`skills/agent-reflect-and-learn/SKILL.md`)
- **Agent** `agent-reflect-daily` — evidence, reflection, artifacts, push (`agents/agent-reflect-daily.md`)
- **Skill** `wisdom-to-content` — learnings → social posts and blog drafts (`skills/wisdom-to-content/SKILL.md`)
- **Hooks** (Cursor) — `hooks/hooks.json` + `hooks/agent-reflect-and-learn-stop.mjs`
- **Scripts** — `collect_day_evidence.py`, `push_daily_review_artifacts.py`
- **Assets** — report template, rubric, examples

## Configuration (per reviewed repository)

Under the **target repo** root (`--repo`), the plugin reads `.agent-reflect-and-learn/config.json`:

```json
{ "artifactsPath": "artifacts" }
```

Relative paths are resolved against that repo root. Create or edit with **`jq`** (see `agents/agent-reflect-daily.md`). The collector and push scripts use this when `--out` / `--artifacts-dir` are omitted. First run: the subagent asks where to put artifacts if the file is missing.

## Quick use

From the root of the repository you want to review, after config exists (or use `--out` / `--artifacts-dir` to override):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo .
```

After the retrospective run produces `YYYY-MM-DD-daily-review.md` and `YYYY-MM-DD-improvement-actions.json` under your artifacts directory, push from the same repo root:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/push_daily_review_artifacts.py" --date YYYY-MM-DD --repo .
```

If you run these commands outside Claude Code, set `CLAUDE_PLUGIN_ROOT` to the filesystem path of this plugin’s root directory (the folder that contains `.claude-plugin/`).

## Tests

```bash
cd plugins/agent-reflect-and-learn/skills/agent-reflect-and-learn && python3 -m unittest discover -s tests -v
```
