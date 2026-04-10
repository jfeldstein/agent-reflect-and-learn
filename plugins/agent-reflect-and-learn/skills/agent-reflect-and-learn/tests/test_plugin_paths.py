"""Tests for plugin_paths (CLAUDE_PLUGIN_ROOT vs __file__ anchor)."""
from __future__ import annotations

import importlib
import os
import tempfile
import unittest
from pathlib import Path


def _plugin_root() -> Path:
    return Path(__file__).resolve().parents[3]


class TestResolveBundledScript(unittest.TestCase):
    def tearDown(self) -> None:
        import plugin_paths

        os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
        importlib.reload(plugin_paths)

    def test_anchor_without_env(self) -> None:
        import plugin_paths

        os.environ.pop("CLAUDE_PLUGIN_ROOT", None)
        importlib.reload(plugin_paths)
        p = plugin_paths.resolve_bundled_script("collect_day_evidence.py")
        self.assertTrue(p.is_file())
        self.assertEqual(p.name, "collect_day_evidence.py")

    def test_prefers_env_when_script_exists_there(self) -> None:
        import plugin_paths

        os.environ["CLAUDE_PLUGIN_ROOT"] = str(_plugin_root())
        importlib.reload(plugin_paths)
        p = plugin_paths.resolve_bundled_script("collect_day_evidence.py")
        self.assertTrue(p.is_file())
        self.assertEqual(p.resolve(), (_plugin_root() / "skills/agent-reflect-and-learn/scripts/collect_day_evidence.py").resolve())

    def test_ignores_bad_env_and_falls_back(self) -> None:
        import plugin_paths

        with tempfile.TemporaryDirectory() as tmp:
            os.environ["CLAUDE_PLUGIN_ROOT"] = tmp
            importlib.reload(plugin_paths)
            p = plugin_paths.resolve_bundled_script("collect_day_evidence.py")
            self.assertTrue(p.is_file())
            self.assertEqual(p.name, "collect_day_evidence.py")


if __name__ == "__main__":
    unittest.main()
