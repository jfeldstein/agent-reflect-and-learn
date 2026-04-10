# agent-reflect-and-learn

A manually invoked daily retrospective skill bundle.

## What it is
This asset is designed for explicit scheduled use, such as the end of each workday. It reviews the day's work and produces artifacts that make the next day's work sharper and faster.

## Package contents
- `SKILL.md` — the workflow and output contract
- `scripts/collect_day_evidence.py` — deterministic collector for git, `~/.claude` (plans, global history, **all** Code project `*.jsonl` transcripts touched that day, IDE `sessions`), `~/.cursor` (plans, **recursive** agent-transcript logs), and `--extra` paths
- `scripts/push_daily_review_artifacts.py` — stage dated `artifacts/*` files, commit if needed, `pull --rebase`, `push`
- `assets/daily-review-template.md` — fixed report structure
- `references/review-rubric.md` — decision rules for what becomes memory, a skill, a script, or a workflow fix
- `examples/` — place for example outputs

## Suggested use
At the end of the day:

From the root of the repository you are reviewing:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo . --out artifacts
```

Then run the skill explicitly with the evidence packet and template to produce:
- `artifacts/YYYY-MM-DD-daily-review.md`
- `artifacts/YYYY-MM-DD-improvement-actions.json`

Finally push those files (and the evidence pair) from the repo root:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/agent-reflect-and-learn/scripts/push_daily_review_artifacts.py" --date YYYY-MM-DD --repo . --artifacts-dir artifacts
```

When invoking the scripts manually outside Claude Code, set `CLAUDE_PLUGIN_ROOT` to this plugin’s install path (directory containing `.claude-plugin/`).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Why this package shape
The collector removes repetitive mechanical work.
The skill keeps reasoning focused on mistakes, improvements, and tomorrow readiness.
The template keeps reports comparable across days.
The rubric prevents overreacting to noise and underreacting to durable patterns.
