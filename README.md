# agent-reflect-and-learn

Claude Code plugin that bundles the **agent-reflect-and-learn** skill: a deliberate end-of-day retrospective backed by deterministic evidence collection, plus the slash command **`/agent-reflect-and-learn`**. Also includes **wisdom-to-content**: turn learnings and insights into short- and medium-form social and blog copy.

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

Point the task at the repository (or worktree) you want reviewed so `--repo .` and `artifacts/` resolve correctly. That invokes the bundled command, which runs the full skill workflow for today’s date.

## Contents

Plugin root: `plugins/agent-reflect-and-learn/` (in this repo; same layout in the install cache after `plugin install`).

- **Command** `/agent-reflect-and-learn` — `commands/agent-reflect-and-learn.md`
- **Skill** `agent-reflect-and-learn` — workflow, output contract, and quality bar (`skills/agent-reflect-and-learn/SKILL.md`)
- **Skill** `wisdom-to-content` — learnings → social posts and blog drafts (`skills/wisdom-to-content/SKILL.md`)
- **Scripts** — `collect_day_evidence.py`, `push_daily_review_artifacts.py`
- **Assets** — report template, rubric, examples

## Quick use

From the root of the repository you want to review (where `artifacts/` should live):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo . --out artifacts
```

After the skill produces `artifacts/YYYY-MM-DD-daily-review.md` and `artifacts/YYYY-MM-DD-improvement-actions.json`, push from the same repo root:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/push_daily_review_artifacts.py" --date YYYY-MM-DD --repo . --artifacts-dir artifacts
```

If you run these commands outside Claude Code, set `CLAUDE_PLUGIN_ROOT` to the filesystem path of this plugin’s root directory (the folder that contains `.claude-plugin/`).

## Tests

```bash
cd plugins/agent-reflect-and-learn/skills/agent-reflect-and-learn && python3 -m unittest discover -s tests -v
```
