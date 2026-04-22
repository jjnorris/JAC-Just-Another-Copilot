import unittest
import importlib.util
from pathlib import Path


class TestSuppressGenericQuestion(unittest.TestCase):
    def test_suppress_generic_question_for_python_app_shape(self):
        spec = importlib.util.spec_from_file_location(
            "repo_task_research",
            str(Path(__file__).parent / "repo_task_research.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        profile = {
            "detected_languages": ["py"],
            "detected_frameworks": [],
            "repo_shape": "python_app_repo",
            "repo_shape_confidence": "medium",
            "confidence_level": "low",
        }

        brief = mod.make_brief(
            Path("."),
            "Self-host JACK: research-quality focused run for single-file edit",
            profile,
            [],
            [],
            [],
        )
        questions = brief.get("recommended_next_questions", [])
        generic = "Is this repository using Django, FastAPI, Flask, or another Python framework? Please confirm."
        self.assertNotIn(generic, questions)
        self.assertTrue(
            any("Python application" in q for q in questions),
            f"expected targeted question, got {questions}",
        )
        # The brief-generation should upgrade confidence for actionability
        # when local signals are strong (low->medium for python_app_repo).
        self.assertEqual(
            brief.get("repo_stack_summary", {}).get("confidence_level"),
            "medium",
            f"expected effective confidence 'medium', got {brief.get('repo_stack_summary', {})}",
        )


if __name__ == "__main__":
    unittest.main()
