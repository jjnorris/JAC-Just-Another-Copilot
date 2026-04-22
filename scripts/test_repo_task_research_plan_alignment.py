import unittest
from scripts.repo_task_research import pick_top_snippets


class TestRepoTaskResearchPlanAlignment(unittest.TestCase):
    def test_plan_alignment_prefers_plan_sources_and_queries(self):
        plan = {
            "selected_queries": [
                "Python virtualenv and environment management",
                "Python packaging with pip/poetry",
            ],
            "selected_sources": {
                "Python virtualenv and environment management": [
                    "https://docs.python.org/3/"
                ],
                "Python packaging with pip/poetry": ["https://docs.python.org/3/"],
            },
        }

        evidence = [
            {
                "title": "Python venv",
                "source_url": "https://docs.python.org/3/library/venv.html",
                "chunk_text": "Use venv to manage virtual environments",
                "query": "Python virtualenv and environment management",
                "stack": "python",
            },
            {
                "title": "Python packaging",
                "source_url": "https://docs.python.org/3/",
                "chunk_text": "Packaging with pip and poetry",
                "query": "Python packaging with pip/poetry",
                "stack": "python",
            },
            {
                "title": "Django middleware",
                "source_url": "https://docs.djangoproject.com/en/stable/topics/middleware/",
                "chunk_text": "Middleware patterns in Django",
                "query": "Django middleware",
                "stack": "django",
            },
            {
                "title": "Next routing",
                "source_url": "https://nextjs.org/docs/routing",
                "chunk_text": "Routing in Next.js",
                "query": "Next.js routing",
                "stack": "nextjs",
            },
        ]

        selected = pick_top_snippets(
            evidence, "Self-host JACK: single-file edit", 3, plan=plan, profile=None
        )

        # All selected snippets must align with the plan (source prefix or query)
        for s in selected:
            src = s.get("source_url", "")
            q = s.get("query", "")
            self.assertTrue(
                src.startswith("https://docs.python.org/3/")
                or q in plan["selected_queries"]
            )

        # Ensure stale framework docs are not promoted
        for s in selected:
            self.assertNotIn("docs.djangoproject.com", s.get("source_url", ""))
            self.assertNotIn("nextjs.org", s.get("source_url", ""))


if __name__ == "__main__":
    unittest.main()
