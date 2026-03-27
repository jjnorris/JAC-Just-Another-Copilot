---
applyTo: ".github/hooks/**/*.json,docs/jac/hook-contracts/**/*.json,docs/jac/event-contracts/**/*.json,docs/jac/templates/**/*.json,docs/jac/rules/06-tool-governance.md,docs/jac/rules/07-output-guardrails.md,docs/jac/rules/09-compliance-security-license.md,docs/jac/workflows/secret-handling.md,docs/jac/secret-handling-model.md,docs/jac/rotation-runbook.md"
---

Keep the security posture plain and strict.

- do not place tokens, credentials, or secret-like strings in examples, prompts, logs, or docs
- distinguish secret material from ordinary configuration
- no `curl | bash`
- no destructive commands without explicit approval
- keep tool permissions narrow and cwd-aware
- treat `docs/jac/hook-contracts/` as canonical rationale and `.github/hooks/*.json` as the native executable layer
- warn about compliance or license obligations without pretending to give legal sign-off
