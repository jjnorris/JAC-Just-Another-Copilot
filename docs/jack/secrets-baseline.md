Tuning the detect-secrets baseline

Purpose
- Reduce false positives from detect-secrets and gitleaks by recording known non-secret patterns.

Quick steps
1. Install: python -m pip install detect-secrets
2. Generate a baseline: python scripts/generate_secrets_baseline.py --baseline .secrets.baseline
   or: detect-secrets scan > .secrets.baseline
3. Inspect the baseline carefully. DO NOT commit real secrets. Remove or redact any true secrets.
4. Commit the tuned .secrets.baseline and re-run CI.

Notes
- The repo uses .secrets.baseline by default. Use the generator script to create or refresh it.
- In CI, ensure the baseline is present and pre-commit will use it to reduce noise.
- For emergency local testing, prefer a local baseline file and avoid committing it (or redact it) until reviewed.

Security reminder
- Never store long-lived credentials in the repo. Baselines are for suppressing false positives, not for storing secrets.
