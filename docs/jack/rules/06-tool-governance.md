# Tool governance

## intent
Apply least privilege, explicit budgets, and approval rules to tools.

## applies_when
- Any tool or shell use.

## non-negotiables
- Set task-scoped budgets.
- Prefer read before write.
- Prefer list-form shell execution and explicit cwd.
- No `curl | bash`.
- No destructive action without explicit approval.
- No secret echoing.
- Label untrusted web content as untrusted.

## warnings
- Broad tool scopes invite confused deputy failures.
- Tool definition drift must trigger re-evaluation.

## blockers
- Privileged actions beyond explicit approval.
- Budget breaches without review.

## examples
- Good: narrow file writes with a bounded shell command budget.
- Bad: running a destructive recursive delete because a model suggested it.

## interplay
Uses `.github/hooks/tool-guardian.json`, `.github/hooks/dependency-risk.json`, and `.github/hooks/extension-surface-guard.json`.
