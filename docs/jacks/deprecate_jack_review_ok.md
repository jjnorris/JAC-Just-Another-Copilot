Deprecation: JACK_REVIEW_OK

Overview

The environment variable JACK_REVIEW_OK is deprecated and will be removed in a future release.
It allowed consumers to bypass review gates via an environment variable (for example, setting it to "1").
This bypass is insecure and not auditable in CI; prefer server-verified approval artifacts instead.

Why remove it

- Security: env vars can be set locally or by CI jobs and are easily forged.
- Auditability: server-verified runs provide provable evidence of a successful workflow.
- Principle: fail-closed, minimize silent bypasses.

Migration steps

1. Use server-side verification in GitHub Actions:
   - Create an approval artifact in the repository (for example, write a JSON line to "jack/review-approved.jsonl" during a successful Actions run).
   - Ensure the artifact includes these fields: approved: true, provider: "github-actions", repo: "owner/repo", run_id: <actions-run-id>

   Example (workflow step snippet):

   - name: Write review-approved artifact
     run: |
       mkdir -p jack
       python - <<'PY'
       import json
       data = {"approved": True, "provider": "github-actions", "repo": "${{ github.repository }}", "run_id": int("${{ github.run_id }}")}
       open('jack/review-approved.jsonl','a').write(json.dumps(data)+'\n')
       PY

2. Ensure workflows that need to bypass review are run in the same repository and complete successfully. The hook attempts to verify the claimed run via the repository's Actions credential if available.

3. Audit: the artifact is accepted only if the run can be verified server-side. This prevents spoofing by untrusted local changes.

Temporary migration window

During a short migration window, JACK_REVIEW_OK will still be recognized but will emit a deprecation advisory in hook logs when used. Plan to remove the env var entirely after the migration window.

Emergency overrides

For emergencies, create an explicit repository-only approval artifact from a trusted runner (not via a mutable env var). Avoid using JACK_REVIEW_OK in production CI.

If you have constrained CI environments that make server verification difficult, open an issue describing the environment and constraints — the recommended path is to adopt a secure, auditable mechanism rather than an env var.
