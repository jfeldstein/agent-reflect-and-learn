# agent-reflect-and-learn

Claude Code plugin that bundles the **daily-work-review** skill: a deliberate end-of-day retrospective backed by deterministic evidence collection.

## Install

Add this repository as a plugin source in Claude Code (local path or git URL), then enable **agent-reflect-and-learn**.

## Contents

- **Skill** `daily-work-review` — workflow, output contract, and quality bar (`skills/daily-work-review/SKILL.md`)
- **Scripts** — `collect_day_evidence.py`, `push_daily_review_artifacts.py`
- **Assets** — report template, rubric, examples

## Quick use

From the root of the repository you want to review (where `artifacts/` should live):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-work-review/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo . --out artifacts
```

After the skill produces `artifacts/YYYY-MM-DD-daily-review.md` and `artifacts/YYYY-MM-DD-improvement-actions.json`, push from the same repo root:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-work-review/scripts/push_daily_review_artifacts.py" --date YYYY-MM-DD --repo . --artifacts-dir artifacts
```

If you run these commands outside Claude Code, set `CLAUDE_PLUGIN_ROOT` to the filesystem path of this plugin’s root directory (the folder that contains `.claude-plugin/`).

## Tests

```bash
cd skills/daily-work-review && python3 -m unittest discover -s tests -v
```
