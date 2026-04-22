import json
import tempfile
import unittest
from pathlib import Path


class EditSketchNoYamlFallbackTest(unittest.TestCase):
    def test_no_yaml_fallback_when_repo_has_no_yaml(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            # Create a simple script that contains the target symbol
            scripts_dir = td_path / "scripts"
            scripts_dir.mkdir()
            target = scripts_dir / "foo.py"
            target.write_text("def load_json(path: Path) -> dict:\n    return {}\n")

            # Create jack inspection artifact that points to the script and symbol
            jack = td_path / "jack"
            jack.mkdir()
            inspect = {
                "inspected_files": ["scripts\\foo.py"],
                "key_symbols_or_sections": ["def load_json"],
            }
            (jack / "repo-task-inspect.json").write_text(
                json.dumps(inspect), encoding="utf-8"
            )

            # Run the edit-sketch module
            import importlib

            mod = importlib.import_module("scripts.repo_task_edit_sketch")
            # Call main with the temporary repo root
            res = mod.main(["--repo-root", str(td_path), "--task", "test task"])
            self.assertEqual(res, 0)

            sketch_path = jack / "repo-task-edit-sketch.json"
            self.assertTrue(sketch_path.exists())
            data = json.loads(sketch_path.read_text(encoding="utf-8"))
            suggested = data.get("suggested_change_shape", "")
            # Ensure we do not recommend 'YAML parsing if available' when no YAML support exists
            self.assertNotIn("YAML parsing if available", suggested)


if __name__ == "__main__":
    unittest.main()
