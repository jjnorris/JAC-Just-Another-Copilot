import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


spec = importlib.util.spec_from_file_location("docs_lookup", Path(__file__).with_name("docs_lookup.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestDocsLookupMultiSourceInterleaving(unittest.TestCase):
    def test_multiple_source_urls_survive_bounded_merge(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            temp_dir = Path(temp_dir_str)
            registry_path = temp_dir / "registry.json"
            out_path = temp_dir / "docs.jsonl"

            first_url = "https://docs.python.org/3/library/argparse.html"
            second_url = "https://docs.python.org/3/library/pathlib.html"

            registry_path.write_text(
                json.dumps({"python": [first_url, second_url]}, indent=2) + "\n",
                encoding="utf-8",
            )

            html_by_url = {
                first_url: "<html><head><title>First</title></head><body>"
                + " ".join(f"alpha{i}" for i in range(80))
                + "</body></html>",
                second_url: "<html><head><title>Second</title></head><body>"
                + " ".join(f"beta{i}" for i in range(80))
                + "</body></html>",
            }

            def fake_fetch_url(url: str, timeout: int = 10) -> str:
                return html_by_url[url]

            with mock.patch.object(mod, "fetch_url", side_effect=fake_fetch_url):
                exit_code = mod.main(
                    [
                        "--query",
                        "alpha0",
                        "--stack",
                        "python",
                        "--registry-file",
                        str(registry_path),
                        "--out",
                        str(out_path),
                        "--chunk-size",
                        "10",
                    ]
                )

            self.assertEqual(exit_code, 0)

            output_records = [json.loads(line) for line in out_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            leading_sources = [record["source_url"] for record in output_records[:4]]

            self.assertIn(first_url, leading_sources)
            self.assertIn(second_url, leading_sources)
            self.assertGreater(len(set(leading_sources)), 1)


if __name__ == "__main__":
    unittest.main()