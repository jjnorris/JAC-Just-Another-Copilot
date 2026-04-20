import importlib.util
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "profile_to_docs_lookup", Path(__file__).with_name("profile_to_docs_lookup.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestProfileToDocsLookupSourceSpecificity(unittest.TestCase):
    def test_self_hosting_python_tooling_repo_uses_topic_specific_python_docs(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            (temp_dir / "scripts").mkdir()
            (temp_dir / "docs" / "jac").mkdir(parents=True)
            (temp_dir / "scripts" / "run_repo_task_flow.py").write_text("# runner\n", encoding="utf-8")
            (temp_dir / "scripts" / "profile_to_docs_lookup.py").write_text("# lookup\n", encoding="utf-8")
            (temp_dir / "docs" / "jac" / "README.md").write_text("# JACK\n", encoding="utf-8")

            profile = {
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "confidence_level": "medium",
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "detected_runtime_targets": [],
            }

            selected, _ambiguity, _rationale = mod.pick_queries(profile, repo_root=temp_dir)
            selected_queries = [item["query"] for item in selected]

            self.assertIn(mod.IMPLEMENTATION_TOOLING_QUERY, selected_queries)

            source_urls = mod.source_urls_for_query(
                mod.IMPLEMENTATION_TOOLING_QUERY,
                "python",
                repo_root=temp_dir,
            )

            self.assertTrue(source_urls)
            self.assertNotIn("https://docs.python.org/3/", source_urls)
            self.assertTrue(all(url.startswith("https://docs.python.org/3/library/") for url in source_urls))


if __name__ == "__main__":
    unittest.main()
