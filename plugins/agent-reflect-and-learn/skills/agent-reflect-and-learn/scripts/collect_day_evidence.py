#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path
from typing import Iterable

_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

import plugin_config  # noqa: E402

SCHEDULED_TASK_MARKER = "<scheduled-task"


def filter_scheduled_task_jsonl_lines(text: str) -> str:
    """Drop jsonl lines that embed Claude scheduled-task payloads (noisy in daily review)."""
    lines = text.splitlines()
    kept = [line for line in lines if SCHEDULED_TASK_MARKER not in line]
    if not kept:
        return "[filtered: all lines contained scheduled-task markers]\n"
    return "\n".join(kept) + "\n"


def read_jsonl_snippet(path: Path, max_chars: int, *, exclude_scheduled_task_lines: bool) -> str:
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"[failed to read {path}: {exc}]"
    if exclude_scheduled_task_lines:
        raw = filter_scheduled_task_jsonl_lines(raw)
    if len(raw) > max_chars:
        return raw[:max_chars] + "\n\n[truncated]"
    return raw


def run(cmd: list[str], cwd: Path | None = None) -> str:
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            return f"[command failed: {' '.join(cmd)}]\n{stderr}".strip()
        return result.stdout.strip()
    except FileNotFoundError:
        return f"[command not found: {' '.join(cmd)}]"


def is_git_repo(repo: Path) -> bool:
    return (repo / ".git").exists() or run(["git", "rev-parse", "--is-inside-work-tree"], repo) == "true"


def read_text(path: Path, max_chars: int = 20000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n\n[truncated]"
        return text
    except Exception as exc:
        return f"[failed to read {path}: {exc}]"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect deterministic evidence for a daily work review.")
    p.add_argument("--date", required=True, help="Date in YYYY-MM-DD")
    p.add_argument("--repo", default=".", help="Repository root")
    p.add_argument(
        "--out",
        default=None,
        metavar="DIR",
        help="Output directory (default: artifactsPath from .agent-reflect-and-learn/config.json in --repo)",
    )
    p.add_argument("--extra", nargs="*", default=[], help="Extra files or directories to include")
    p.add_argument("--max-plan-files", type=int, default=8)
    p.add_argument("--max-history-items", type=int, default=25)
    p.add_argument(
        "--max-claude-project-jsonl",
        type=int,
        default=16,
        help="Cap for ~/.claude/projects/*/*.jsonl touched on target day (repo slug listed first)",
    )
    p.add_argument(
        "--max-claude-session-json",
        type=int,
        default=12,
        help="Cap for ~/.claude/sessions/*.json touched on target day",
    )
    p.add_argument(
        "--max-cursor-transcripts",
        type=int,
        default=24,
        help="Cap for ~/.cursor/projects/*/agent-transcripts/** (recursive) touched on target day",
    )
    p.add_argument(
        "--max-cursor-plan-files",
        type=int,
        default=8,
        help="Cap for ~/.cursor/plans files touched on target day",
    )
    p.add_argument(
        "--exclude-scheduled-task-lines",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Remove jsonl lines containing scheduled-task payloads from Claude project + "
        "Cursor .jsonl transcripts (default: true). Use --no-exclude-scheduled-task-lines for full capture.",
    )
    return p.parse_args()


def collect_git(repo: Path, day: dt.date) -> dict:
    if not is_git_repo(repo):
        return {"present": False}

    since = f"{day.isoformat()} 00:00:00"
    until = f"{(day + dt.timedelta(days=1)).isoformat()} 00:00:00"

    return {
        "present": True,
        "root": str(repo.resolve()),
        "branch": run(["git", "branch", "--show-current"], repo),
        "status_short": run(["git", "status", "--short"], repo),
        "diff_stat": run(["git", "diff", "--stat"], repo),
        "cached_diff_stat": run(["git", "diff", "--cached", "--stat"], repo),
        "log_today": run([
            "git",
            "log",
            f"--since={since}",
            f"--until={until}",
            "--date=iso",
            "--pretty=format:%h | %ad | %an | %s",
        ], repo),
        "files_touched_today": run([
            "git",
            "log",
            f"--since={since}",
            f"--until={until}",
            "--name-only",
            "--pretty=format:",
        ], repo),
    }


def iter_recent_files(base: Path, target_day: dt.date) -> Iterable[Path]:
    if not base.exists():
        return []
    files: list[Path] = []
    for path in base.rglob("*"):
        if path.is_file():
            try:
                mtime = dt.date.fromtimestamp(path.stat().st_mtime)
            except OSError:
                continue
            if mtime == target_day:
                files.append(path)
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files


def path_to_claude_code_project_slug(repo: Path) -> str:
    """Match Claude Code's ~/.claude/projects directory naming (leading dash)."""
    p = repo.resolve()
    s = str(p)
    if s.startswith("/"):
        return "-" + s[1:].replace("/", "-")
    return s.replace("/", "-")


def find_claude_project_jsonl_for_day(
    projects_root: Path,
    day: dt.date,
    repo: Path | None,
) -> list[Path]:
    """
    All Claude Code project *.jsonl touched on `day` under projects_root.

    When `repo` is set, files under that repo's slug directory are sorted first
    (then by newest mtime) so the reviewed workspace stays visible under tight caps.
    """
    if not projects_root.is_dir():
        return []

    slug: str | None = path_to_claude_code_project_slug(repo) if repo is not None else None

    scored: list[tuple[int, float, Path]] = []
    for proj_dir in projects_root.iterdir():
        if not proj_dir.is_dir():
            continue
        match_repo = slug is not None and proj_dir.name == slug
        for path in proj_dir.iterdir():
            if not path.is_file() or path.suffix != ".jsonl":
                continue
            if path.name == "sessions-index.json":
                continue
            try:
                st = path.stat()
                mtime_d = dt.date.fromtimestamp(st.st_mtime)
            except OSError:
                continue
            if mtime_d != day:
                continue
            priority = 0 if match_repo else 1
            scored.append((priority, -st.st_mtime, path))

    scored.sort(key=lambda t: (t[0], t[1]))
    return [p for _, _, p in scored]


def collect_claude_project_session_jsonl(
    repo: Path,
    day: dt.date,
    max_files: int,
    *,
    exclude_scheduled_task_lines: bool,
) -> list[dict]:
    """Claude Code transcript *.jsonl for all project slugs touched that day (repo slug first)."""
    projects_root = Path.home() / ".claude" / "projects"
    candidates = find_claude_project_jsonl_for_day(projects_root, day, repo)

    out: list[dict] = []
    for path in candidates[:max_files]:
        out.append({
            "path": str(path),
            "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "content": read_jsonl_snippet(
                path, 25000, exclude_scheduled_task_lines=exclude_scheduled_task_lines
            ),
        })
    return out


def collect_claude_sessions_dir_json(day: dt.date, max_files: int) -> list[dict]:
    """Claude IDE session payloads under ~/.claude/sessions (numeric *.json)."""
    base = Path.home() / ".claude" / "sessions"
    if not base.is_dir():
        return []

    candidates: list[Path] = []
    for path in base.iterdir():
        if not path.is_file() or path.suffix != ".json":
            continue
        try:
            mtime = dt.date.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if mtime == day:
            candidates.append(path)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    out: list[dict] = []
    for path in candidates[:max_files]:
        out.append({
            "path": str(path),
            "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "content": read_text(path, 12000),
        })
    return out


def find_cursor_agent_transcript_files(projects_root: Path, day: dt.date) -> list[Path]:
    """
    Cursor agent chat logs: *.jsonl / *.json under each workspace's agent-transcripts/,
    including nested session folders (e.g. agent-transcripts/<uuid>/*.jsonl) and subagents/.
    """
    if not projects_root.is_dir():
        return []

    candidates: list[Path] = []
    for proj in projects_root.iterdir():
        if not proj.is_dir():
            continue
        at_dir = proj / "agent-transcripts"
        if not at_dir.is_dir():
            continue
        for path in at_dir.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in (".jsonl", ".json"):
                continue
            try:
                mtime = dt.date.fromtimestamp(path.stat().st_mtime)
            except OSError:
                continue
            if mtime == day:
                candidates.append(path)
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates


def collect_cursor_agent_transcripts(
    day: dt.date,
    max_files: int,
    *,
    exclude_scheduled_task_lines: bool,
) -> list[dict]:
    """Cursor workspace agent transcripts (recursive under agent-transcripts/)."""
    projects_root = Path.home() / ".cursor" / "projects"
    candidates = find_cursor_agent_transcript_files(projects_root, day)

    out: list[dict] = []
    for path in candidates[:max_files]:
        content = (
            read_jsonl_snippet(path, 25000, exclude_scheduled_task_lines=exclude_scheduled_task_lines)
            if path.suffix == ".jsonl"
            else read_text(path, 25000)
        )
        out.append({
            "path": str(path),
            "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "content": content,
        })
    return out


def collect_claude_plans(day: dt.date, max_files: int) -> list[dict]:
    plan_dir = Path.home() / ".claude" / "plans"
    files = list(iter_recent_files(plan_dir, day))[:max_files]
    out = []
    for path in files:
        out.append({
            "path": str(path),
            "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "content": read_text(path, 12000),
        })
    return out


def collect_cursor_plans(day: dt.date, max_files: int) -> list[dict]:
    plan_dir = Path.home() / ".cursor" / "plans"
    files = list(iter_recent_files(plan_dir, day))[:max_files]
    out = []
    for path in files:
        out.append({
            "path": str(path),
            "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "content": read_text(path, 12000),
        })
    return out


def collect_claude_history(day: dt.date, max_items: int) -> list[dict]:
    history_path = Path.home() / ".claude" / "history.jsonl"
    if not history_path.exists():
        return []

    items: list[dict] = []
    prefix = day.isoformat()
    try:
        with history_path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                joined = json.dumps(obj, ensure_ascii=False)
                if prefix not in joined:
                    continue

                items.append(obj)
                if len(items) >= max_items:
                    break
    except Exception:
        return []

    return items


def dedupe_resolve_extra_paths(
    repo: Path, config_paths: list[str], cli_paths: list[str]
) -> list[str]:
    """
    Merge config extras then CLI extras; resolve repo-relative paths against
    repo root; dedupe by resolved path (first occurrence wins).
    """
    root = repo.resolve()
    out: list[str] = []
    seen: set[str] = set()
    for raw in [*config_paths, *cli_paths]:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = (root / p).resolve()
        else:
            p = p.resolve()
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def collect_extra(paths: list[str]) -> list[dict]:
    out: list[dict] = []
    for raw in paths:
        path = Path(raw).expanduser()
        if not path.exists():
            out.append({"path": raw, "error": "not found"})
            continue

        if path.is_file():
            out.append({"path": str(path), "content": read_text(path, 12000)})
            continue

        if path.is_dir():
            files = sorted([p for p in path.rglob("*") if p.is_file()])[:10]
            out.append({
                "path": str(path),
                "files": [{"path": str(p), "content": read_text(p, 6000)} for p in files],
            })
    return out


def render_markdown(date_str: str, payload: dict) -> str:
    lines: list[str] = []
    lines.append(f"# Daily Review Evidence Packet — {date_str}")
    lines.append("")
    lines.append("This file is deterministic collection output intended to ground the daily retrospective.")
    lines.append("")

    git = payload.get("git", {})
    lines.append("## Git")
    lines.append("")
    if not git.get("present"):
        lines.append("No git repository detected.")
    else:
        lines.append(f"- Repo root: `{git.get('root', '')}`")
        lines.append(f"- Branch: `{git.get('branch', '')}`")
        lines.append("")
        lines.append("### Status")
        lines.append("")
        lines.append("```text")
        lines.append(git.get("status_short", "") or "[empty]")
        lines.append("```")
        lines.append("")
        lines.append("### Diff stat")
        lines.append("")
        lines.append("```text")
        lines.append(git.get("diff_stat", "") or "[empty]")
        lines.append("```")
        lines.append("")
        lines.append("### Cached diff stat")
        lines.append("")
        lines.append("```text")
        lines.append(git.get("cached_diff_stat", "") or "[empty]")
        lines.append("```")
        lines.append("")
        lines.append("### Commits today")
        lines.append("")
        lines.append("```text")
        lines.append(git.get("log_today", "") or "[empty]")
        lines.append("```")
        lines.append("")
        lines.append("### Files touched today")
        lines.append("")
        lines.append("```text")
        lines.append(git.get("files_touched_today", "") or "[empty]")
        lines.append("```")

    plans = payload.get("claude_plans", [])
    lines.append("")
    lines.append("## Claude Plans")
    lines.append("")
    if not plans:
        lines.append("No same-day Claude plan files found.")
    else:
        for item in plans:
            lines.append(f"### {item['path']}")
            lines.append("")
            lines.append(f"Modified: `{item['mtime']}`")
            lines.append("")
            lines.append("```markdown")
            lines.append(item["content"])
            lines.append("```")
            lines.append("")

    history = payload.get("claude_history", [])
    lines.append("## Claude History Entries")
    lines.append("")
    if not history:
        lines.append("No same-day Claude history entries found in `~/.claude/history.jsonl`.")
    else:
        lines.append("```json")
        lines.append(json.dumps(history, indent=2, ensure_ascii=False))
        lines.append("```")

    def append_file_snippets(heading: str, items: list[dict], empty_note: str) -> None:
        lines.append("")
        lines.append(heading)
        lines.append("")
        if not items:
            lines.append(empty_note)
        else:
            for item in items:
                lines.append(f"### {item['path']}")
                lines.append("")
                lines.append(f"Modified: `{item['mtime']}`")
                lines.append("")
                lines.append("```text")
                lines.append(item["content"])
                lines.append("```")
                lines.append("")

    append_file_snippets(
        "## Claude Code project transcripts (`~/.claude/projects/*/*.jsonl`)",
        payload.get("claude_project_session_jsonl", []),
        "No same-day Claude Code `.jsonl` transcripts under `~/.claude/projects` (all slugs).",
    )
    append_file_snippets(
        "## Claude IDE session files (`~/.claude/sessions/*.json`)",
        payload.get("claude_sessions_dir_json", []),
        "No same-day session JSON files in `~/.claude/sessions`.",
    )
    append_file_snippets(
        "## Cursor plans (`~/.cursor/plans`)",
        payload.get("cursor_plans", []),
        "No same-day Cursor plan files found.",
    )
    append_file_snippets(
        "## Cursor agent transcripts (`~/.cursor/projects/*/agent-transcripts/**`)",
        payload.get("cursor_agent_transcripts", []),
        "No same-day Cursor agent transcript files found (searched recursively under each workspace's `agent-transcripts/`).",
    )

    extra = payload.get("extra", [])
    lines.append("")
    lines.append("## Extra Inputs")
    lines.append("")
    if not extra:
        lines.append("No extra paths provided.")
    else:
        for item in extra:
            if "error" in item:
                lines.append(f"- `{item['path']}` — {item['error']}")
                continue
            if "content" in item:
                lines.append(f"### {item['path']}")
                lines.append("")
                lines.append("```text")
                lines.append(item["content"])
                lines.append("```")
                lines.append("")
            elif "files" in item:
                lines.append(f"### {item['path']}")
                lines.append("")
                for f in item["files"]:
                    lines.append(f"#### {f['path']}")
                    lines.append("")
                    lines.append("```text")
                    lines.append(f["content"])
                    lines.append("```")
                    lines.append("")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    args = parse_args()
    target_day = dt.date.fromisoformat(args.date)
    repo = Path(args.repo).expanduser().resolve()
    if args.out is not None:
        out_dir = Path(args.out).expanduser().resolve()
    else:
        ap = plugin_config.load_artifacts_path(repo)
        if ap is None:
            plugin_config.print_config_required_message(repo, prog="collect_day_evidence.py")
            return 2
        out_dir = plugin_config.resolve_artifacts_dir(repo, ap)
    out_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "date": args.date,
        "git": collect_git(repo, target_day),
        "claude_plans": collect_claude_plans(target_day, args.max_plan_files),
        "claude_history": collect_claude_history(target_day, args.max_history_items),
        "claude_project_session_jsonl": collect_claude_project_session_jsonl(
            repo,
            target_day,
            args.max_claude_project_jsonl,
            exclude_scheduled_task_lines=args.exclude_scheduled_task_lines,
        ),
        "claude_sessions_dir_json": collect_claude_sessions_dir_json(
            target_day, args.max_claude_session_json
        ),
        "cursor_plans": collect_cursor_plans(target_day, args.max_cursor_plan_files),
        "cursor_agent_transcripts": collect_cursor_agent_transcripts(
            target_day,
            args.max_cursor_transcripts,
            exclude_scheduled_task_lines=args.exclude_scheduled_task_lines,
        ),
        "extra": collect_extra(
            dedupe_resolve_extra_paths(
                repo,
                plugin_config.load_extra_evidence_paths(repo),
                list(args.extra),
            )
        ),
    }

    json_path = out_dir / f"{args.date}-evidence.json"
    md_path = out_dir / f"{args.date}-evidence.md"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(args.date, payload), encoding="utf-8")

    print(str(md_path))
    print(str(json_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
