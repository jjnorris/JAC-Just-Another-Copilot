import unittest
from typing import Any, Dict, List

from scripts.repo_task_plan import (
    choose_recommended_first_edit_area,
    prioritize_first_edit_area,
    synthesize_implementation_steps,
)


class TestRepoTaskPlanPlanningSynthesis(unittest.TestCase):
    def test_self_hosting_python_tooling_plan_turns_brief_into_concrete_steps(self):
        profile: Dict[str, Any] = {
            "repo_shape": "python_tooling_repo",
            "repo_shape_confidence": "high",
            "detected_languages": ["py"],
            "detected_runtime_targets": ["Python"],
        }
        task = "Self-host JACK: planning synthesis focused run for single-file edit"
        brief: Dict[str, Any] = {
            "actionable_suggestions": [
                "Inspect the target script for argument parsing and subprocess invocation before editing.",
                "Check the target script for path handling and JSON/file I/O paths for the single-file change.",
            ],
            "implementation_considerations": [
                "Repository appears Pythonic: prefer virtualenv/venv, pin dependencies, and run unit tests locally before changes.",
            ],
        }
        likely_targets: List[str] = [
            "scripts/repo_task_research.py",
            "scripts/repo_task_edit_sketch.py",
            "scripts/repo_task_plan.py",
        ]

        first_edit_area = choose_recommended_first_edit_area(task, profile, likely_targets)
        ordered_targets = prioritize_first_edit_area(likely_targets, first_edit_area)
        steps = synthesize_implementation_steps(task, profile, brief, ordered_targets, first_edit_area)

        self.assertEqual(first_edit_area, "scripts/repo_task_plan.py")
        self.assertEqual(ordered_targets[0], "scripts/repo_task_plan.py")
        self.assertIn("scripts/repo_task_plan.py", steps[0])
        self.assertIn("argument parsing and subprocess invocation", steps[0])
        self.assertTrue(any("path handling and JSON/file I/O" in step for step in steps))
        self.assertIn(
            "Regenerate jack/repo-task-plan.json and jack/repo-task-first-edit.md, then confirm recommended_first_edit_area remains scripts/repo_task_plan.py.",
            steps,
        )
        self.assertNotIn(
            "Based on the inspection, propose concrete code or config changes.",
            steps,
        )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
