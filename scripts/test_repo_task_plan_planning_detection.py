import json
import unittest
from pathlib import Path

from scripts.repo_task_plan import (
    choose_recommended_first_edit_area,
    synthesize_implementation_steps,
    load_json,
)


class TestPlanningIntentDetection(unittest.TestCase):
    def setUp(self):
        self.jack_dir = Path("jack")
        self.jack_dir.mkdir(exist_ok=True)
        (self.jack_dir / "repo-stack-profile.json").write_text(json.dumps({"repo_shape": "python_tooling_repo"}))
        (self.jack_dir / "repo-task-brief.json").write_text(json.dumps({"actionable_suggestions": [], "ambiguities": [], "relevant_evidence_snippets": []}))

    def tearDown(self):
        p1 = self.jack_dir / "repo-stack-profile.json"
        p2 = self.jack_dir / "repo-task-brief.json"
        if p1.exists():
            p1.unlink()
        if p2.exists():
            p2.unlink()

    def test_planning_variant_triggers_planning_path(self):
        # Wording variant that previously missed the planning matcher
        task = "Self-host JACK: verify rank_files planner-first guarantee"
        profile = load_json(self.jack_dir / "repo-stack-profile.json")
        brief = load_json(self.jack_dir / "repo-task-brief.json")

        likely_targets = ["scripts/repo_task_plan.py", "scripts/load_helpers.py"]
        recommended = choose_recommended_first_edit_area(task, profile, likely_targets)

        # Expect the planning-specific recommended first edit area
        self.assertEqual(recommended, "scripts/repo_task_plan.py")

        steps = synthesize_implementation_steps(task, profile, brief, likely_targets, recommended)
        # Planning-focused synth should reference the planner target explicitly
        self.assertTrue(any("repo_task_plan.py" in s for s in steps), "Implementation steps should be planning-focused and mention the planner file")


if __name__ == "__main__":
    unittest.main()
