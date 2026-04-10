"""Tests for plugin_config (artifacts path JSON config)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path
import tempfile

import importlib.util


def _load_plugin_config():
    script = Path(__file__).resolve().parent.parent / "scripts" / "plugin_config.py"
    spec = importlib.util.spec_from_file_location("plugin_config", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pc = _load_plugin_config()


class TestPluginConfig(unittest.TestCase):
    def test_missing_file_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self.assertIsNone(pc.load_artifacts_path(repo))

    def test_loads_relative_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            d = repo / pc.CONFIG_DIR
            d.mkdir(parents=True)
            (d / pc.CONFIG_NAME).write_text(
                json.dumps({"artifactsPath": "my-artifacts"}),
                encoding="utf-8",
            )
            self.assertEqual(pc.load_artifacts_path(repo), "my-artifacts")

    def test_resolve_relative_to_repo(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            got = pc.resolve_artifacts_dir(repo, "logs/review")
            self.assertEqual(got, (repo / "logs" / "review").resolve())

    def test_resolve_absolute(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            abs_p = Path(td) / "abs-art"
            got = pc.resolve_artifacts_dir(repo, str(abs_p))
            self.assertEqual(got, abs_p.resolve())

    def test_invalid_json_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            d = repo / pc.CONFIG_DIR
            d.mkdir(parents=True)
            (d / pc.CONFIG_NAME).write_text("{not json", encoding="utf-8")
            self.assertIsNone(pc.load_artifacts_path(repo))

    def test_empty_artifacts_path_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            d = repo / pc.CONFIG_DIR
            d.mkdir(parents=True)
            (d / pc.CONFIG_NAME).write_text(
                json.dumps({"artifactsPath": "  "}),
                encoding="utf-8",
            )
            self.assertIsNone(pc.load_artifacts_path(repo))

    def test_extra_evidence_paths_missing_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            d = repo / pc.CONFIG_DIR
            d.mkdir(parents=True)
            (d / pc.CONFIG_NAME).write_text(
                json.dumps({"artifactsPath": "artifacts"}),
                encoding="utf-8",
            )
            self.assertEqual(pc.load_extra_evidence_paths(repo), [])

    def test_extra_evidence_paths_filters_non_strings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            d = repo / pc.CONFIG_DIR
            d.mkdir(parents=True)
            (d / pc.CONFIG_NAME).write_text(
                json.dumps({
                    "artifactsPath": "artifacts",
                    "extraEvidencePaths": ["a.md", 9, "  ", "b.md", {"x": 1}],
                }),
                encoding="utf-8",
            )
            self.assertEqual(pc.load_extra_evidence_paths(repo), ["a.md", "b.md"])

    def test_extra_evidence_paths_invalid_json_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            d = repo / pc.CONFIG_DIR
            d.mkdir(parents=True)
            (d / pc.CONFIG_NAME).write_text("{bad", encoding="utf-8")
            self.assertEqual(pc.load_extra_evidence_paths(repo), [])


if __name__ == "__main__":
    unittest.main()
