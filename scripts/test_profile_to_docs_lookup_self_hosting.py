import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "profile_to_docs_lookup", Path(__file__).with_name("profile_to_docs_lookup.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestProfileToDocsLookupSelfHosting(unittest.TestCase):
    def test_self_hosting_python_tooling_repo_includes_implementation_query(self):
        temp_dir = Path(tempfile.mkdtemp())
        try:
            (temp_dir / "scripts").mkdir()
            (temp_dir / "docs" / "jac").mkdir(parents=True)
            (temp_dir / "scripts" / "run_repo_task_flow.py").write_text(
                "# runner\n", encoding="utf-8"
            )
            (temp_dir / "scripts" / "profile_to_docs_lookup.py").write_text(
                "# lookup\n", encoding="utf-8"
            )
            (temp_dir / "docs" / "jac" / "README.md").write_text(
                "# JACK\n", encoding="utf-8"
            )

            profile = {
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "confidence_level": "medium",
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "detected_runtime_targets": [],
            }

            selected, _ambiguity, _rationale = mod.pick_queries(
                profile, repo_root=temp_dir
            )
            selected_queries = [item["query"] for item in selected]

            self.assertIn(mod.IMPLEMENTATION_TOOLING_QUERY, selected_queries)
            self.assertFalse(
                set(selected_queries).issubset(
                    {
                        "Python virtualenv and environment management",
                        "Python packaging with pip/poetry",
                    }
                )
            )
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
