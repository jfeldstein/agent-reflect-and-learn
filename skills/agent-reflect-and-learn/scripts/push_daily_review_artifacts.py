#!/usr/bin/env python3
"""Stage dated daily-review artifacts, commit if needed, pull --rebase, push."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(
    cmd: list[str],
    cwd: Path,
    *,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.setdefault("GIT_PAGER", "")
    env.setdefault("PAGER", "")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    p = argparse.ArgumentParser(
        description="Git add/commit/pull --rebase/push for daily review artifact files.",
    )
    p.add_argument("--date", required=True, help="YYYY-MM-DD (must match artifact name prefix)")
    p.add_argument("--repo", default=".", type=Path, help="Git repository root")
    p.add_argument("--artifacts-dir", default="artifacts", help="Directory under repo root")
    p.add_argument("--dry-run", action="store_true", help="Print actions only")
    args = p.parse_args()

    repo = args.repo.expanduser().resolve()
    art = (repo / args.artifacts_dir).resolve()
    date = args.date
    names = [
        f"{date}-evidence.md",
        f"{date}-evidence.json",
        f"{date}-daily-review.md",
        f"{date}-improvement-actions.json",
    ]
    existing = [art / n for n in names if (art / n).is_file()]
    if not existing:
        print(f"No artifact files found under {art} for date {date}", file=sys.stderr)
        return 1

    rels = [str(x.relative_to(repo)) for x in existing]

    if args.dry_run:
        print("Would: git add --", " ".join(rels))
        print("Would: commit if staged diff non-empty, then pull --rebase, push")
        return 0

    chk = run(["git", "rev-parse", "--is-inside-work-tree"], repo)
    if chk.returncode != 0 or chk.stdout.strip() != "true":
        print("Not a git repository:", repo, file=sys.stderr)
        return 1

    add_r = run(["git", "add", "--", *rels], repo)
    if add_r.returncode != 0:
        print(add_r.stderr or add_r.stdout, file=sys.stderr)
        return add_r.returncode

    diff_r = run(["git", "diff", "--staged", "--quiet"], repo)
    if diff_r.returncode == 0:
        print("Nothing to commit (staged empty).")
        upstream = run(["git", "rev-parse", "--abbrev-ref", "@{u}"], repo)
        if upstream.returncode != 0:
            print("No upstream branch; skipping pull/push.", file=sys.stderr)
            return 0
        pull_r = run(
            ["git", "pull", "--rebase"],
            repo,
            extra_env={"EDITOR": "true"},
        )
        if pull_r.returncode != 0:
            print(pull_r.stderr or pull_r.stdout, file=sys.stderr)
            return pull_r.returncode
        push_r = run(["git", "push"], repo)
        if push_r.returncode != 0:
            print(push_r.stderr or push_r.stdout, file=sys.stderr)
            return push_r.returncode
        print("Pushed (no new commit for artifacts).")
        return 0

    commit_r = run(
        ["git", "commit", "-m", f"docs: daily review artifacts {date}"],
        repo,
    )
    if commit_r.returncode != 0:
        print(commit_r.stderr or commit_r.stdout, file=sys.stderr)
        return commit_r.returncode

    pull_r = run(
        ["git", "pull", "--rebase"],
        repo,
        extra_env={"EDITOR": "true"},
    )
    if pull_r.returncode != 0:
        print(pull_r.stderr or pull_r.stdout, file=sys.stderr)
        return pull_r.returncode

    push_r = run(["git", "push"], repo)
    if push_r.returncode != 0:
        print(push_r.stderr or push_r.stdout, file=sys.stderr)
        return push_r.returncode

    print("Committed and pushed daily review artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
