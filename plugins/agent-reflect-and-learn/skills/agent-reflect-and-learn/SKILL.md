---
name: agent-reflect-and-learn
description: Orchestrate the end-of-day retrospective by delegating the full workflow to `agent-reflect-daily`.
disable-model-invocation: true
---

# Agent reflect and learn

## Trigger

Use when the Cursor **stop** hook follow-up fires, the user runs `/agent-reflect-and-learn`, a scheduled task requests a daily review, or the user explicitly asks for a daily retrospective, end-of-day wrap-up, or tomorrow brief for a repo.

## Workflow

1. Call `agent-reflect-daily`.
2. Return the subagent result to the user.

## Guardrails

- Keep this skill **orchestration-only**.
- Do not collect evidence, write review files, or run collector/push scripts in the parent flow.
- Do not bypass the subagent.

## Reference

Detailed steps, commands, evidence sources, output contract, and quality bar live in `agents/agent-reflect-daily.md` (subagent). Scripts and templates remain under this skill directory:

- `scripts/collect_day_evidence.py`
- `scripts/push_daily_review_artifacts.py`
- `assets/daily-review-template.md`
- `references/review-rubric.md`
