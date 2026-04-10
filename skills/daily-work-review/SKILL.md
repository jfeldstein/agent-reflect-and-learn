---
name: daily-work-review
description: Run on an explicit daily schedule to review the day's work, extract mistakes and reusable learnings, convert repeated prose work into rules or scripts, summarize debugging sessions, and produce a sharp starting brief for tomorrow. Use when the user says daily review, end-of-day review, wrap up the day, daily retro, prepare tomorrow, or explicitly invokes daily-work-review.
---

# Daily Work Review

## Purpose
This skill performs a deliberate end-of-day retrospective so the next day's work starts from cleaner state, sharper memory, and lower repeated error rate.

It is not for automatic background invocation. It is for explicit, scheduled use, typically once per workday.

## What success looks like
By the end of the run, produce all of the following:

1. A concise record of what was actually shipped, decided, tested, learned, and left unresolved.
2. A ranked list of mistakes, friction points, and repeated failure patterns.
3. Concrete improvement candidates split into:
   - rule / memory update
   - new skill candidate
   - deterministic script candidate
   - workflow / naming / packaging fix
4. A debugging summary for any nontrivial debugging session.
5. A tomorrow-start brief that reduces warm-up and avoids reopening solved questions.
6. Optional shareable nuggets if the day produced a clear insight worth posting.

## Required workflow
Follow this workflow in order.

### 1) Collect evidence first
Do not begin with freeform reflection.

Start by running the deterministic collector:

Run from the target git repo root (the workspace you are reviewing). With this plugin installed, `CLAUDE_PLUGIN_ROOT` points at the plugin directory:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-work-review/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo . --out artifacts
```

If needed, include extra notes or paths:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-work-review/scripts/collect_day_evidence.py" --date YYYY-MM-DD --repo . --out artifacts --extra notes/today.md docs/plan.md
```

Use the generated evidence packet as the factual base. Prefer evidence over memory.

**Evidence sources (deterministic collector)**

| Source | What it captures |
|--------|------------------|
| Git (`--repo`) | status, diffs, same-day log, files touched |
| `~/.claude/plans` | Claude Code plan files modified on the target date |
| `~/.claude/history.jsonl` | Lines whose JSON mentions the target date |
| `~/.claude/projects/<repo-slug>/*.jsonl` | Per-worktree Claude Code session transcripts for that repo (mtime on target date) |
| `~/.claude/sessions/*.json` | Claude IDE session blobs (mtime on target date) |
| `~/.cursor/plans` | Cursor plan files modified on the target date |
| `~/.cursor/projects/*/agent-transcripts` | Cursor agent transcripts (`.jsonl`/`.json`, mtime on target date) |
| `--extra …` | Additional paths you pass in |

Same-day matching uses the file **mtime calendar day** in local time (except `history.jsonl`, which uses substring match on `YYYY-MM-DD` inside each line’s JSON).

**Noise control:** By default, Claude project `*.jsonl` and Cursor agent `*.jsonl` snippets **drop lines containing** `<scheduled-task` (scheduled automation replays). Full capture: `--no-exclude-scheduled-task-lines`.

### 2) Reconstruct the day
From the evidence packet, reconstruct:
- work started
- work completed
- work abandoned
- major branch points / decisions
- tests run / not run
- bugs investigated
- files repeatedly touched
- open loops carried into tomorrow

### 3) Scan for mistakes and friction
Look for:
- repeated re-explanation
- repeated failed commands
- wrong assumptions that caused rework
- hidden dependencies discovered late
- debugging thrash
- avoidable context loss
- prose instructions that should be scripts
- vague or weak skill names / descriptions
- scattered notes that should have been consolidated

For each issue, capture:
- symptom
- root cause
- recurrence likelihood
- smallest durable fix

### 4) Promote the right kind of fix
Use this decision rule:

- Put it in **memory/rules** if the lesson is stable, general, and should affect future behavior.
- Make it a **new skill** if the lesson is reusable, multi-step, non-obvious, and likely to recur.
- Make it a **script** if the step is mechanical, deterministic, repetitive, or mostly data collection / formatting.
- Make it a **workflow fix** if the issue is mainly naming, file placement, scheduling, or packaging.

Do not inflate minor annoyances into permanent rules.
Do not keep re-describing deterministic work in prose if a script can do it.

### 5) Summarize debugging cleanly
If the day included debugging, produce a compact debugging note with:
- target symptom
- actual root cause
- misleading clues / false leads
- decisive observation that broke the case open
- permanent prevention or detection step
- whether this deserves a debugging skill or playbook update

### 6) Build tomorrow's starting brief
Produce a brief that the next session can read in under 2 minutes. Include:
- exact current state
- first 1 to 3 next actions
- known traps
- files to open first
- commands to rerun first
- decisions already made and not to revisit without new evidence

### 7) Extract optional publishable insight
Only do this when the day produced a real insight.

Generate at most:
- 3 one-line nuggets
- 1 short LinkedIn-style post draft
- 1 short X / thread hook set

Favor insights that are:
- specific
- surprising
- transferable
- grounded in observed work

Do not publish fluff. Skip this section if the material is weak.

## Output contract
Write the final report to:

`artifacts/YYYY-MM-DD-daily-review.md`

Use the template in `assets/daily-review-template.md`.

Also write a machine-friendly action file:

`artifacts/YYYY-MM-DD-improvement-actions.json`

That JSON must contain arrays for:
- `memory_updates`
- `skill_candidates`
- `script_candidates`
- `workflow_fixes`
- `tomorrow_actions`

### 8) Push artifacts to the remote
After both the evidence packet and the two review outputs exist under `artifacts/`, run from the knowledge-base repo root (same cwd as `--out artifacts`):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/daily-work-review/scripts/push_daily_review_artifacts.py" --date YYYY-MM-DD --repo . --artifacts-dir artifacts
```

This stages the dated files (`*-evidence.md`, `*-evidence.json`, `*-daily-review.md`, `*-improvement-actions.json`), commits if there is a staged change, then `git pull --rebase` (non-interactive: set `EDITOR=true` in the script’s environment) and `git push`. Use `--dry-run` to print what would run. Exits with an error if none of the four files exist.

## Quality bar
The review is good only if it changes tomorrow.

Reject vague conclusions like:
- be more careful
- plan better
- communicate more clearly

Prefer concrete outcomes like:
- add a collector script for git + session history
- rename skill so activation is obvious
- create a troubleshooting playbook for hydration mismatches
- pin exact command sequence in a reusable asset

## Guardrails
- Prefer evidence over recollection.
- Prefer one durable fix over many weak reminders.
- Prefer scripts for mechanical steps.
- Keep the final tomorrow brief short.
- Keep publishable content optional and low-volume.
