import json
import unittest
from pathlib import Path

from scripts.repo_task_plan import (
    rank_files,
    choose_recommended_first_edit_area,
    synthesize_implementation_steps,
    load_json,
)


class TestRankFilesAnchor(unittest.TestCase):
    def setUp(self):
        self.jack_dir = Path("jack")
        self.jack_dir.mkdir(exist_ok=True)
        (self.jack_dir / "repo-stack-profile.json").write_text(
            json.dumps({"repo_shape": "python_tooling_repo"})
        )
        (self.jack_dir / "repo-task-brief.json").write_text(
            json.dumps(
                {
                    "actionable_suggestions": [],
                    "ambiguities": [],
                    "relevant_evidence_snippets": [],
                }
            )
        )

    def tearDown(self):
        for p in (
            self.jack_dir / "repo-stack-profile.json",
            self.jack_dir / "repo-task-brief.json",
        ):
            if p.exists():
                p.unlink()

    def test_planning_variant_anchors_rank_files(self):
        task = "Self-host JACK: verify rank_files planner-first guarantee"
        candidates = ["scripts/repo_task_plan.py", "scripts/load_helpers.py"]
        # Simulate inspector reporting the rank_files symbol first
        ranked = rank_files(candidates, task, inspect_symbols=["def rank_files"])
        self.assertTrue(
            ranked[0].endswith("repo_task_plan.py"),
            "Planner should be ranked first when inspector reports def rank_files",
        )

        profile = load_json(self.jack_dir / "repo-stack-profile.json")
        brief = load_json(self.jack_dir / "repo-task-brief.json")
        recommended = choose_recommended_first_edit_area(task, profile, ranked[:5])
        self.assertEqual(recommended, "scripts/repo_task_plan.py")

        steps = synthesize_implementation_steps(
            task, profile, brief, ranked[:5], recommended
        )
        self.assertTrue(
            any("rank_files" in s or "def rank_files" in s for s in steps),
            "Implementation steps should reference def rank_files for planner-focused tasks",
        )


if __name__ == "__main__":
    unittest.main()
