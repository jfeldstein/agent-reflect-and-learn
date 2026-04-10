"""Unit tests for agent-reflect-and-learn collector helpers."""
from __future__ import annotations

import datetime as dt
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


def _load_collector():
    script = Path(__file__).resolve().parent.parent / "scripts" / "collect_day_evidence.py"
    spec = importlib.util.spec_from_file_location("collect_day_evidence", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cde = _load_collector()


class TestClaudeProjectSlug(unittest.TestCase):
    def test_macos_style_path(self) -> None:
        p = Path("/Users/jordan/Code/Documents")
        self.assertEqual(cde.path_to_claude_code_project_slug(p), "-Users-jordan-Code-Documents")


class TestScheduledTaskFilter(unittest.TestCase):
    def test_removes_scheduled_lines(self) -> None:
        raw = '{"x":1}\n{"task":"<scheduled-task name=\\"x\\"/>"}\n{"y":2}\n'
        out = cde.filter_scheduled_task_jsonl_lines(raw)
        self.assertNotIn("scheduled-task", out)
        self.assertIn('"x":1', out)
        self.assertIn('"y":2', out)

    def test_all_filtered_placeholder(self) -> None:
        raw = '{"a":"<scheduled-task />"}\n'
        out = cde.filter_scheduled_task_jsonl_lines(raw)
        self.assertIn("filtered", out)


def _utime_day(path: Path, day: dt.date, *, offset_sec: float = 0) -> None:
    ts = dt.datetime.combine(day, dt.time(12, 0, 0)).timestamp() + offset_sec
    os.utime(path, (ts, ts))


class TestFindCursorAgentTranscripts(unittest.TestCase):
    def test_finds_nested_session_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "projects"
            f = root / "ws" / "agent-transcripts" / "session-uuid" / "session-uuid.jsonl"
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text('{"role":"user"}\n', encoding="utf-8")
            day = dt.date(2030, 6, 1)
            _utime_day(f, day)
            found = cde.find_cursor_agent_transcript_files(root, day)
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0], f)


class TestFindClaudeProjectJsonl(unittest.TestCase):
    def test_repo_slug_prioritized_over_newer_other_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = Path("/Users/jordan/Code/Documents")
            slug = cde.path_to_claude_code_project_slug(repo)
            mine = root / slug
            other = root / "other-workspace-slug"
            mine.mkdir(parents=True, exist_ok=True)
            other.mkdir(parents=True, exist_ok=True)
            f_mine = mine / "b.jsonl"
            f_other = other / "a.jsonl"
            f_mine.write_text("{}\n", encoding="utf-8")
            f_other.write_text("{}\n", encoding="utf-8")
            day = dt.date(2030, 6, 2)
            _utime_day(f_mine, day, offset_sec=0)
            _utime_day(f_other, day, offset_sec=3600)
            found = cde.find_claude_project_jsonl_for_day(root, day, repo)
            self.assertEqual(found[0], f_mine)
            self.assertEqual(found[1], f_other)


class TestRepoRootLaunchers(unittest.TestCase):
    """Marketplace repo root `scripts/*` delegates to the bundled plugin scripts."""

    def test_collect_launcher_delegates(self) -> None:
        root = Path(__file__).resolve().parents[5]
        launcher = root / "scripts" / "collect_day_evidence.py"
        self.assertTrue(launcher.is_file(), msg=str(launcher))
        r = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("Collect deterministic evidence", r.stdout)

    def test_push_launcher_delegates(self) -> None:
        root = Path(__file__).resolve().parents[5]
        launcher = root / "scripts" / "push_daily_review_artifacts.py"
        self.assertTrue(launcher.is_file(), msg=str(launcher))
        r = subprocess.run(
            [sys.executable, str(launcher), "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(r.returncode, 0, msg=r.stderr)
        self.assertIn("push", r.stdout.lower())


if __name__ == "__main__":
    unittest.main()
