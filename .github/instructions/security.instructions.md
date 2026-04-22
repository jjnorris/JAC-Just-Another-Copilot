---
applyTo: ".github/hooks/**/*.json,docs/jack/hook-contracts/**/*.json,docs/jack/event-contracts/**/*.json,docs/jack/templates/**/*.json,docs/jack/rules/06-tool-governance.md,docs/jack/rules/07-output-guardrails.md,docs/jack/rules/09-compliance-security-license.md,docs/jack/workflows/secret-handling.md,docs/jack/secret-handling-model.md,docs/jack/rotation-runbook.md"
---

Keep the security posture plain and strict.

- do not place tokens, credentials, or secret-like strings in examples, prompts, logs, or docs
- distinguish secret material from ordinary configuration
- no `curl | bash`
- no destructive commands without explicit approval
- keep tool permissions narrow and cwd-aware
- treat `docs/jack/hook-contracts/` as canonical rationale and `.github/hooks/*.json` as the native executable layer
- warn about compliance or license obligations without pretending to give legal sign-off
