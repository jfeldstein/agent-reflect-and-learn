#!/usr/bin/env python3
"""Run the bundled push script from a clone of this marketplace repo (no CLAUDE_PLUGIN_ROOT)."""
from __future__ import annotations

import os
import sys
from pathlib import Path

_SKILL_SCRIPTS = (
    Path(__file__).resolve().parent.parent
    / "plugins"
    / "agent-reflect-and-learn"
    / "skills"
    / "agent-reflect-and-learn"
    / "scripts"
)
if str(_SKILL_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS))

from plugin_paths import resolve_bundled_script  # noqa: E402

_target = resolve_bundled_script("push_daily_review_artifacts.py")
os.execv(sys.executable, [sys.executable, str(_target), *sys.argv[1:]])
