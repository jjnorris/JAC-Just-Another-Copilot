#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
import os


class TestRepoTaskPlanPlanningSpecificity(unittest.TestCase):
    def test_planning_wording_variant_emits_concrete_steps_and_keeps_plan_first(self):
        spec = importlib.util.spec_from_file_location(
            "repo_task_plan", Path(__file__).with_name("repo_task_plan.py")
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scripts_dir = repo / "scripts"
            jack_dir = repo / "jack"
            scripts_dir.mkdir(parents=True)
            jack_dir.mkdir(parents=True)

            # Minimal planner and intake files so collect_candidate_files
            # finds the first-edit pair, plus a few broader pipeline scripts
            # that should stay out of the planning-focused shortlist.
            (scripts_dir / "repo_task_plan.py").write_text(
                "def rank_files(candidates, task, inspect_symbols=None):\n    pass\n",
                encoding="utf-8",
            )
            (scripts_dir / "intake_to_lookup.py").write_text(
                "def load_spec(path):\n    return {}\n",
                encoding="utf-8",
            )
            (scripts_dir / "verify_validation_report.py").write_text(
                "def main(argv=None):\n    return 0\n",
                encoding="utf-8",
            )
            (scripts_dir / "run_repo_task_flow.py").write_text(
                "def main(argv=None):\n    return 0\n",
                encoding="utf-8",
            )
            (scripts_dir / "repo_task_change_outline.py").write_text(
                "def main(argv=None):\n    return 0\n",
                encoding="utf-8",
            )

            # Provide profile that signals python tooling repo
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps({"repo_shape": "python_tooling_repo"}, indent=2), encoding="utf-8"
            )

            task = "Self-host JACK: implement rank_files planning fix"
            # Run planner against the temp repo
            ret = mod.main(["--repo-root", str(repo), "--task", task])
            self.assertEqual(ret, 0)

            plan = json.loads((jack_dir / "repo-task-plan.json").read_text(encoding="utf-8"))

            # Assertions: planner remains first-edit area and emits concrete
            # planning-focused steps (contains 'rewrite').
            self.assertIn("repo_task_plan.py", plan.get("recommended_first_edit_area", ""))
            steps = plan.get("implementation_steps", [])
            self.assertGreater(len(steps), 0)
            first = steps[0].lower()
            self.assertIn("modify or extend", first)
            self.assertEqual(
                plan.get("likely_target_files"),
                ["scripts/repo_task_plan.py", "scripts/intake_to_lookup.py"],
            )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
