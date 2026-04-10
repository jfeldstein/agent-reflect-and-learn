"""Per-repository JSON config for agent-reflect-and-learn (jq-friendly shape)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

CONFIG_DIR = ".agent-reflect-and-learn"
CONFIG_NAME = "config.json"
DEFAULT_ARTIFACTS_PATH = "artifacts"


def config_dir(repo: Path) -> Path:
    return repo.resolve() / CONFIG_DIR


def config_path(repo: Path) -> Path:
    return config_dir(repo) / CONFIG_NAME


def load_extra_evidence_paths(repo: Path) -> list[str]:
    """
    Return extraEvidencePaths from repo/.agent-reflect-and-learn/config.json.

    Each entry must be a non-empty string (typically repo-root-relative).
    Non-strings and blank strings are skipped. Missing key or unreadable
    config yields an empty list.
    """
    path = config_path(repo)
    if not path.is_file():
        return []
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    val = data.get("extraEvidencePaths")
    if not isinstance(val, list):
        return []
    out: list[str] = []
    for item in val:
        if not isinstance(item, str):
            continue
        s = item.strip()
        if s:
            out.append(s)
    return out


def load_artifacts_path(repo: Path) -> str | None:
    """
    Return artifactsPath from repo/.agent-reflect-and-learn/config.json, or None
    if missing, unreadable, or empty.
    """
    path = config_path(repo)
    if not path.is_file():
        return None
    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    val = data.get("artifactsPath")
    if not isinstance(val, str):
        return None
    s = val.strip()
    return s or None


def resolve_artifacts_dir(repo: Path, artifacts_path: str) -> Path:
    """Resolve artifactsPath: absolute paths as-is; relative paths against repo root."""
    p = Path(artifacts_path).expanduser()
    if p.is_absolute():
        return p.resolve()
    return (repo.resolve() / p).resolve()


def print_config_required_message(repo: Path, *, prog: str) -> None:
    cfg = config_path(repo)
    print(
        f"{prog}: no artifacts path configured for this repository.\n"
        f"Create {cfg} with jq (after asking the user for the directory; "
        f'default relative path is "{DEFAULT_ARTIFACTS_PATH}"):\n'
        f'  mkdir -p {CONFIG_DIR} && jq -n --arg p "{DEFAULT_ARTIFACTS_PATH}" '
        f"'{{artifactsPath: $p}}' > {CONFIG_DIR}/{CONFIG_NAME}\n"
        f"Or pass an explicit output flag to skip config for this run.",
        file=sys.stderr,
    )
