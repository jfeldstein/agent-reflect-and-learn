"""Unit tests for daily-work-review collector helpers."""
from __future__ import annotations

import importlib.util
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


if __name__ == "__main__":
    unittest.main()
