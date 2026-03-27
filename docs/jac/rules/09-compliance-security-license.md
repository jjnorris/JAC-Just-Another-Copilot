# Compliance, security, and license

## intent
Raise early warnings for regulated domains, sensitive data, and license conflicts.

## applies_when
- Handling auth, secrets, regulated data, dependency choices, distribution, and domain-specific obligations.

## non-negotiables
- Surface obligations without pretending to provide legal sign-off.
- Distinguish warning from blocker.
- Heighten scrutiny for secrets, auth, remote execution, and dependency changes.
- Warn when strong copyleft conflicts with stated distribution goals.

## warnings
- Compliance blind spots often appear as ordinary engineering tasks.
- License drift can hide inside dependency churn.

## blockers
- Explicitly incompatible license or compliance conflict.
- Unsafe secret handling.

## examples
- Good: warn that new auth scaffolding needs stronger review and secret-boundary notes.
- Bad: treat payment or healthcare logic like generic CRUD.

## interplay
Uses `.github/skills/compliance-audit/SKILL.md`, `workflows/compliance-triage.md`, and `docs/jac/secret-handling-model.md`.
