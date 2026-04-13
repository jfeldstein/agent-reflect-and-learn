# agent-reflect-and-learn

A manually invoked daily retrospective skill bundle.

## What it is

This asset is designed for explicit scheduled use, such as the end of each workday. It reviews the day's work and produces artifacts that make the next day's work sharper and faster.

## Package contents

- `SKILL.md` — orchestration-only; delegates to `agent-reflect-daily` (`disable-model-invocation`)
- `../../agents/agent-reflect-daily.md` — full retrospective workflow and output contract for the subagent
- `scripts/collect_day_evidence.py` — deterministic collector for git, `~/.claude` (plans, global history, **all** Code project `*.jsonl` transcripts touched that day, IDE `sessions`), `~/.cursor` (plans, **recursive** agent-transcript logs), and `--extra` paths
- `scripts/push_daily_review_artifacts.py` — stage dated `artifacts/*` files, commit if needed, `pull --rebase`, `push`
- `../../scripts/collect_day_evidence.sh` / `push_daily_review_artifacts.sh` — plugin-root entrypoints (no `CLAUDE_PLUGIN_ROOT`)
- `assets/daily-review-template.md` — fixed report structure
- `references/review-rubric.md` — decision rules for what becomes memory, a skill, a script, or a workflow fix
- `examples/` — place for example outputs

## Configuration

Per **reviewed** repository: `.agent-reflect-and-learn/config.json` with `{ "artifactsPath": "artifacts" }` (jq-friendly). First use: the **subagent** asks the user, then writes with `jq` (see `agents/agent-reflect-daily.md`). Scripts default to this path when `--out` / `--artifacts-dir` are omitted.

## Suggested use

At the end of the day: run **`/agent-reflect-and-learn`** (or the hook follow-up). The skill delegates to **`agent-reflect-daily`**, which runs the collector, reflection, and artifact writes.

For **manual** script runs from the reviewed repo root: prefer a **bash-safe** path (or the plugin-root `scripts/*.sh` wrappers) so an empty `CLAUDE_PLUGIN_ROOT` does not become `/skills/...`. If the variable is unset, the expansion below is relative to the **plugin root** unless you use an absolute path or the marketplace repo’s `scripts/collect_day_evidence.py` launcher.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}${CLAUDE_PLUGIN_ROOT:+/}skills/agent-reflect-and-learn/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo .
python3 "${CLAUDE_PLUGIN_ROOT}${CLAUDE_PLUGIN_ROOT:+/}skills/agent-reflect-and-learn/scripts/push_daily_review_artifacts.py" --date YYYY-MM-DD --repo .
```

When set, `CLAUDE_PLUGIN_ROOT` must be this plugin’s install path (directory containing `.claude-plugin/`).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Why this package shape

The collector removes repetitive mechanical work.
The skill keeps reasoning focused on mistakes, improvements, and tomorrow readiness.
The template keeps reports comparable across days.
The rubric prevents overreacting to noise and underreacting to durable patterns.