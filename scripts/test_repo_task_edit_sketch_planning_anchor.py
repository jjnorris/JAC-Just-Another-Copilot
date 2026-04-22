import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "repo_task_edit_sketch", Path(__file__).with_name("repo_task_edit_sketch.py")
)
assert spec is not None
assert spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRepoTaskEditSketchPlanningAnchor(unittest.TestCase):
    def test_planning_focused_self_hosting_task_uses_rank_files_anchor(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            repo = Path(temp_dir_str)
            scripts_dir = repo / "scripts"
            jack_dir = repo / "jack"
            scripts_dir.mkdir(parents=True)
            jack_dir.mkdir(parents=True)

            (scripts_dir / "repo_task_plan.py").write_text(
                "def rank_files(candidates, task, inspect_symbols=None):\n"
                "    planner_flag = True\n"
                "    scored = list(candidates)\n"
                "    return scored\n\n"
                "def load_json(path):\n"
                "    return {}\n\n"
                "def read_jsonl(path):\n"
                "    return []\n\n"
                "def collect_candidate_files(repo_root):\n"
                "    return []\n\n"
                "def main(argv=None):\n"
                "    return 0\n",
                encoding="utf-8",
            )
            (scripts_dir / "repo_task_edit_sketch.py").write_text(
                "def load_json(path):\n"
                "    return {}\n\n"
                "def main(argv=None):\n"
                "    return 0\n",
                encoding="utf-8",
            )

            (jack_dir / "repo-task-plan.json").write_text(
                json.dumps(
                    {
                        "likely_target_files": [
                            "scripts/repo_task_plan.py",
                            "scripts/repo_task_edit_sketch.py",
                        ],
                        "recommended_first_edit_area": "scripts/repo_task_plan.py",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (jack_dir / "repo-task-inspect.json").write_text(
                json.dumps(
                    {
                        "inspected_files": [
                            "scripts/repo_task_plan.py",
                            "scripts/repo_task_edit_sketch.py",
                        ],
                        "key_symbols_or_sections": [
                            "def rank_files",
                            "def load_json",
                            "def read_jsonl",
                        ],
                        "recommended_first_code_edit_area": "scripts/repo_task_plan.py",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (jack_dir / "repo-task-brief.json").write_text(
                json.dumps({"ambiguities": []}, indent=2) + "\n",
                encoding="utf-8",
            )
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps({"repo_shape": "python_tooling_repo"}, indent=2) + "\n",
                encoding="utf-8",
            )

            task = "Self-host JACK: edit sketch planning-anchor focused run for single-file edit"
            result = mod.main(["--repo-root", str(repo), "--task", task])
            self.assertEqual(result, 0)

            sketch = json.loads(
                (jack_dir / "repo-task-edit-sketch.json").read_text(encoding="utf-8")
            )
            change_shape = sketch.get("suggested_change_shape", "")

            self.assertEqual(sketch.get("target_file"), "scripts/repo_task_plan.py")
            self.assertEqual(sketch.get("target_symbol_or_section"), "def rank_files")
            self.assertIn("planning-focused self-hosting path", change_shape)
            self.assertIn("rank_files", change_shape)
            self.assertIn("scripts/repo_task_plan.py", change_shape)
            self.assertIn("planning-aware selector", change_shape)
            self.assertIn("return scored", change_shape)
            self.assertNotIn("replace the one-line loader", change_shape)


if __name__ == "__main__":
    unittest.main()
