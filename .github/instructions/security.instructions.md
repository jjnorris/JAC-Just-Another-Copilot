---
applyTo: "jac-copilot/hooks/**/*.json,jac-copilot/event-contracts/**/*.json,jac-copilot/templates/**/*.json,jac-copilot/rules/06-tool-governance.md,jac-copilot/rules/07-output-guardrails.md,jac-copilot/rules/09-compliance-security-license.md,jac-copilot/workflows/secret-handling.md,jac-copilot/docs/secret-handling-model.md,jac-copilot/docs/rotation-runbook.md"
---

Keep the security posture plain and strict.

- do not place tokens, credentials, or secret-like strings in examples, prompts, logs, or docs
- distinguish secret material from ordinary configuration
- no `curl | bash`
- no destructive commands without explicit approval
- keep tool permissions narrow and cwd-aware
- treat hook files as behavioral contracts, not as proof of native enforcement
- warn about compliance or license obligations without pretending to give legal sign-off
