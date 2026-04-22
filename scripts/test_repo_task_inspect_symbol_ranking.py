import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "repo_task_inspect", Path(__file__).with_name("repo_task_inspect.py")
)
assert spec is not None
assert spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRepoTaskInspectSymbolRanking(unittest.TestCase):
    def test_planning_focused_self_hosting_inspect_prefers_rank_files(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            repo = Path(temp_dir_str)
            scripts_dir = repo / "scripts"
            jack_dir = repo / "jack"
            scripts_dir.mkdir(parents=True)
            jack_dir.mkdir(parents=True)

            (scripts_dir / "repo_task_plan.py").write_text(
                "def load_json(path):\n"
                "    pass\n\n"
                "def read_jsonl(path):\n"
                "    pass\n\n"
                "def collect_candidate_files(repo_root):\n"
                "    pass\n\n"
                "def rank_files(candidates, task):\n"
                "    pass\n\n"
                "def main(argv=None):\n"
                "    pass\n",
                encoding="utf-8",
            )
            (scripts_dir / "repo_task_edit_sketch.py").write_text(
                "def load_json(path):\n"
                "    pass\n\n"
                "def main(argv=None):\n"
                "    pass\n",
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

            task = "Self-host JACK: inspect specificity focused run for planning single-file edit"
            result = mod.main(["--repo-root", str(repo), "--task", task])
            self.assertEqual(result, 0)

            inspection = json.loads(
                (jack_dir / "repo-task-inspect.json").read_text(encoding="utf-8")
            )
            symbols = inspection.get("key_symbols_or_sections", [])
            changes = inspection.get("likely_change_areas", [])

            self.assertEqual(
                inspection.get("recommended_first_code_edit_area"),
                "scripts/repo_task_plan.py",
            )
            self.assertGreater(len(symbols), 0)
            self.assertEqual(symbols[0], "def rank_files")
            self.assertEqual(len(symbols), len(set(symbols)))
            self.assertEqual(changes[0], "Modify or extend def rank_files")


if __name__ == "__main__":
    unittest.main()
