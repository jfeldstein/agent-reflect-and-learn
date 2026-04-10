"""Resolve paths to scripts bundled with this skill (works with or without CLAUDE_PLUGIN_ROOT)."""
from __future__ import annotations

import os
from pathlib import Path

_SKILL_SCRIPTS_REL = Path("skills") / "agent-reflect-and-learn" / "scripts"


def resolve_bundled_script(name: str) -> Path:
    """
    Return the path to a file in this skill's scripts directory.

    If CLAUDE_PLUGIN_ROOT is set and points at a plugin tree that contains the
    script, that path wins. Otherwise use this file's directory (install layout).
    """
    root = (os.environ.get("CLAUDE_PLUGIN_ROOT") or "").strip()
    anchor = Path(__file__).resolve().parent / name
    if root:
        env_path = Path(root).resolve() / _SKILL_SCRIPTS_REL / name
        if env_path.is_file():
            return env_path
    if anchor.is_file():
        return anchor
    raise FileNotFoundError(
        f"agent-reflect-and-learn: missing bundled script {name!r} "
        f"(tried {Path(root) / _SKILL_SCRIPTS_REL / name if root else '(no CLAUDE_PLUGIN_ROOT)'} and {anchor})"
    )
