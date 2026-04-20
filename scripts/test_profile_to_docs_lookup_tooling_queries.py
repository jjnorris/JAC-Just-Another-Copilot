import unittest
from scripts.profile_to_docs_lookup import pick_queries

class TestProfileToDocsLookupToolingQueries(unittest.TestCase):
    def test_tooling_repo_selects_multiple_queries(self):
        profile = {
            "detected_frameworks": [],
            "detected_runtime_targets": [],
            "detected_languages": ["py"],
            "repo_shape": "python_tooling_repo",
            "repo_shape_confidence": "high",
            "confidence_level": "low",
        }
        selected, _ambiguity, _rationale = pick_queries(profile)
        queries = [s["query"] for s in selected]
        # Expect at least two queries for tooling repos with high shape confidence
        self.assertGreaterEqual(len(queries), 2)
        self.assertIn("Python packaging with pip/poetry", queries)

if __name__ == "__main__":
    unittest.main()
