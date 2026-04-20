import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

from scripts import run_repo_task_flow as rtf


class TestManifestAppendIdempotence(unittest.TestCase):
    def test_adversarial_and_freshness_append_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            jack = repo_root / "jack"
            jack.mkdir(parents=True)

            now = datetime.now(timezone.utc).isoformat()
            manifest = {
                "task": "t",
                "generated_at": now,
                "transition_ledger_ref": "jack/repo-task-transition-ledger.json",
                "validation_report_ref": "jack/repo-task-validation-report.json",
                "artifact_family_entries": [],
            }
            manifest_path = jack / "repo-task-artifact-family-manifest.json"
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            # create stub artifacts
            adv_path = jack / "repo-task-adversarial-review.json"
            adv_path.write_text(json.dumps({"task": "t"}), encoding="utf-8")
            fres_path = jack / "repo-task-freshness-evidence.json"
            fres_path.write_text(json.dumps({"task": "t"}), encoding="utf-8")

            # Call appenders twice
            rtf.append_adversarial_manifest_entry(repo_root, "t", manifest_path, adv_path)
            rtf.append_adversarial_manifest_entry(repo_root, "t", manifest_path, adv_path)

            rtf.append_freshness_manifest_entry(repo_root, manifest_path, fres_path)
            rtf.append_freshness_manifest_entry(repo_root, manifest_path, fres_path)

            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entries = data.get("artifact_family_entries", [])

            adv_count = sum(1 for e in entries if isinstance(e, dict) and (e.get("artifact_role") == "adversarial_review" or e.get("artifact_path", "").endswith("repo-task-adversarial-review.json")))
            fres_count = sum(1 for e in entries if isinstance(e, dict) and (e.get("artifact_role") == "freshness_evidence" or e.get("artifact_path", "").endswith("repo-task-freshness-evidence.json")))

            self.assertEqual(adv_count, 1, msg=f"adversarial entries duplicated: {adv_count}")
            self.assertEqual(fres_count, 1, msg=f"freshness entries duplicated: {fres_count}")


if __name__ == "__main__":
    unittest.main()
