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


class TestRepoTaskEditSketchParameterName(unittest.TestCase):
    def test_self_hosting_planning_task_uses_actual_loader_parameter_name(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            repo = Path(temp_dir_str)
            scripts_dir = repo / "scripts"
            jack_dir = repo / "jack"
            scripts_dir.mkdir(parents=True)
            jack_dir.mkdir(parents=True)

            (scripts_dir / "repo_task_plan.py").write_text(
                "from pathlib import Path\n"
                "from typing import Any, Dict, Optional\n\n"
                "def load_json(path: Path) -> Optional[Dict[str, Any]]:\n"
                "    try:\n"
                "        return json.loads(path.read_text(encoding=\"utf-8\"))\n"
                "    except Exception:\n"
                "        return None\n",
                encoding="utf-8",
            )

            (jack_dir / "repo-task-plan.json").write_text(
                json.dumps(
                    {
                        "recommended_first_edit_area": "scripts/repo_task_plan.py",
                        "likely_target_files": [
                            "scripts/repo_task_plan.py",
                            "scripts/repo_task_edit_sketch.py",
                        ],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (jack_dir / "repo-task-inspect.json").write_text(
                json.dumps(
                    {
                        "inspected_files": ["scripts/repo_task_plan.py"],
                        "key_symbols_or_sections": ["def load_json"],
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
                json.dumps({}, indent=2) + "\n",
                encoding="utf-8",
            )

            task = "Self-host JACK: packaging source-specificity focused run for planning single-file edit"
            result = mod.main(["--repo-root", str(repo), "--task", task])
            self.assertEqual(result, 0)

            sketch = json.loads((jack_dir / "repo-task-edit-sketch.json").read_text(encoding="utf-8"))
            suggested = sketch.get("suggested_change_shape", "")

            self.assertIn("validates that `path` exists and is readable", suggested)
            self.assertNotIn("spec_file", suggested)
            self.assertEqual(sketch.get("primary_edit_target"), "scripts/repo_task_plan.py")


if __name__ == "__main__":
    unittest.main()