CI guidance for JACK

- Recommended secret scanning: use gitleaks (CI) + detect-secrets (local/pre-commit).
- Provide a gitleaks config at `.github/ci/gitleaks.toml` to tune false positives.
- To bootstrap `detect-secrets` locally, run:
  ```bash
  pip install detect-secrets
  detect-secrets scan --all-files > .secrets.baseline
  ```
- This repo deliberately ships a minimal guidance file rather than enabling detect-secrets in pre-commit by default to avoid CI breakage; follow the steps above to adopt local scanning.
