#!/usr/bin/env python3
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


class TestRepoTaskPlanRankFilesPlanningSelfHosting(unittest.TestCase):
    def test_rank_files_prefers_repo_task_plan_for_planning_self_host(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scripts_dir = repo / "scripts"
            jack_dir = repo / "jack"
            scripts_dir.mkdir(parents=True)
            jack_dir.mkdir(parents=True)

            # Candidate files: planner and a generic helper that would normally
            # be boosted by helper-symbol heuristics.
            (scripts_dir / "repo_task_plan.py").write_text(
                "def rank_files(candidates, task, inspect_symbols=None):\n    pass\n",
                encoding="utf-8",
            )
            (scripts_dir / "helper_loader.py").write_text(
                "def load_spec(path):\n    pass\n",
                encoding="utf-8",
            )

            # Provide a profile that signals a python tooling repo so the
            # planner-boost path may trigger when the task shape matches.
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps({"repo_shape": "python_tooling_repo"}, indent=2),
                encoding="utf-8",
            )

            # Load the repo_task_plan implementation from the workspace so
            # we test the exact runtime behavior.
            spec = importlib.util.spec_from_file_location(
                "repo_task_plan", Path(__file__).with_name("repo_task_plan.py")
            )
            assert spec is not None and spec.loader is not None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # Run rank_files with CWD set to the temp repo so relative
            # artifact reads resolve to the temp repo's jack/ file.
            cwd = Path.cwd()
            try:
                os.chdir(repo)
                candidates = [
                    str(scripts_dir / "repo_task_plan.py"),
                    str(scripts_dir / "helper_loader.py"),
                    str(scripts_dir / "repo_task_plan.py"),  # duplicate to test dedupe
                ]
                task = "Self-host JACK: planning-focused single-file edit"
                ranked = mod.rank_files(
                    candidates, task, inspect_symbols=["def load_spec"]
                )
            finally:
                os.chdir(cwd)

            # Assertions: planner file must be first, results deduplicated,
            # bounded length, and helper should not outrank planner.
            self.assertGreater(len(ranked), 0)
            self.assertEqual(Path(ranked[0]).name, "repo_task_plan.py")
            self.assertEqual(len(ranked), len(set(ranked)))
            self.assertTrue(len(ranked) <= 25)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
