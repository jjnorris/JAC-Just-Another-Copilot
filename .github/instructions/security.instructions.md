---
applyTo: ".github/hooks/**/*.json,docs/jacks/hook-contracts/**/*.json,docs/jacks/event-contracts/**/*.json,docs/jacks/templates/**/*.json,docs/jacks/rules/06-tool-governance.md,docs/jacks/rules/07-output-guardrails.md,docs/jacks/rules/09-compliance-security-license.md,docs/jacks/workflows/secret-handling.md,docs/jacks/secret-handling-model.md,docs/jacks/rotation-runbook.md"
---

Keep the security posture plain and strict.

- do not place tokens, credentials, or secret-like strings in examples, prompts, logs, or docs
- distinguish secret material from ordinary configuration
- no `curl | bash`
- no destructive commands without explicit approval
- keep tool permissions narrow and cwd-aware
- treat `docs/jacks/hook-contracts/` as canonical rationale and `.github/hooks/*.json` as the native executable layer
- warn about compliance or license obligations without pretending to give legal sign-off


