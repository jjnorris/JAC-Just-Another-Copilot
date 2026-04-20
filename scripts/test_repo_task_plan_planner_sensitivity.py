import json
import os
import unittest
from pathlib import Path

from scripts.repo_task_plan import rank_files


class TestRankFilesPlannerSensitivity(unittest.TestCase):
    def setUp(self):
        # Ensure jack dir exists and write a self-hosting profile to trigger
        # the planning-focused branch in rank_files.
        self.jack_dir = Path("jack")
        self.jack_dir.mkdir(exist_ok=True)
        (self.jack_dir / "repo-stack-profile.json").write_text(json.dumps({"repo_shape": "python_tooling_repo"}))

    def tearDown(self):
        # Clean up test artifacts
        p = self.jack_dir / "repo-stack-profile.json"
        if p.exists():
            p.unlink()
        for fname in ("scripts/weak_competitor.py", "scripts/strong_competitor.py"):
            fp = Path(fname)
            if fp.exists():
                fp.unlink()

    def test_planner_sensitive(self):
        # Scenario A: weak competitor -> planner should be first
        weak = Path("scripts/weak_competitor.py")
        weak.parent.mkdir(exist_ok=True)
        weak.write_text("def helper():\n    pass\n")

        candidates = ["scripts/repo_task_plan.py", "scripts/weak_competitor.py"]
        # Use a planning-focused, self-hosting task string
        task = "Self-host planning: keep planner first for close evidence"
        ranked = rank_files(candidates, task, inspect_symbols=None)
        self.assertGreaterEqual(len(ranked), 1)
        self.assertTrue(ranked[0].endswith("repo_task_plan.py"), "Planner should be first when competitor evidence is weak")

        # Scenario B: strong competitor with explicit stage symbols and defs
        strong = Path("scripts/strong_competitor.py")
        parts = [
            "def inspect_x():\n    pass\n\n",
            "def edit_x():\n    pass\n\n",
            "def change_x():\n    pass\n\n",
            "def plan_x():\n    pass\n\n",
            "def research_x():\n    pass\n\n",
            "def intake_x():\n    pass\n\n",
            "def lookup_x():\n    pass\n\n",
            "def profile_x():\n    pass\n\n",
            "def docs_x():\n    pass\n\n",
        ]
        strong.write_text("\n".join(parts))

        candidates2 = ["scripts/repo_task_plan.py", "scripts/strong_competitor.py"]
        # task includes many active stage tokens so the competitor can gather
        # materially stronger stage-based evidence
        task2 = "Self-host planning inspect edit change plan research intake lookup profile docs"
        ranked2 = rank_files(candidates2, task2, inspect_symbols=None)
        self.assertGreaterEqual(len(ranked2), 1)
        self.assertTrue(ranked2[0].endswith("strong_competitor.py"), "Strong competitor should outrank planner when evidence is materially stronger")


if __name__ == "__main__":
    unittest.main()
