#!/usr/bin/env bash
# Plugin-root entrypoint: works when CLAUDE_PLUGIN_ROOT is unset (uses this file's location).
set -euo pipefail
_plugin_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$_plugin_root/skills/agent-reflect-and-learn/scripts/push_daily_review_artifacts.py" "$@"
