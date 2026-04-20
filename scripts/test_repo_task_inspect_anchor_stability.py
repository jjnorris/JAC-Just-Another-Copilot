#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


class TestInspectAnchorStability(unittest.TestCase):
    def test_inspect_prefers_rank_files_despite_helper_before(self):
        # Load the inspect module from the workspace
        spec = importlib.util.spec_from_file_location(
            "repo_task_inspect", Path(__file__).with_name("repo_task_inspect.py")
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Simulate symbols where helper functions appear before the canonical
        # planner symbol `def rank_files` in the source order.
        symbols = [
            "def _dedupe_candidates",
            "def _score_file",
            "def rank_files",
            "def load_json",
        ]

        task = "Self-host JACK: verify rank_files canonical implementation"
        primary = mod.choose_primary_symbol(symbols, task, "scripts/repo_task_plan.py")
        self.assertEqual(primary, "def rank_files")


if __name__ == "__main__":
    raise SystemExit(unittest.main())
