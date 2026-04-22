---
name: compliance-audit
description: Detect sensitive domain, security, and license implications and surface obligations early.
---

# compliance-audit

## Purpose
Detect sensitive domain, security, and license implications and surface obligations early.

## When to use
- auth changes
- regulated domain work
- dependency shifts
- distributed software decisions

## Inputs
- task scope
- domain context
- dependency or distribution information

## Outputs
- warning list
- blocker list
- safer substitute suggestions

## What it checks
- Warn early and separate warning from blocker.
- Do not claim legal sign-off.
- Record when strong copyleft may conflict with distribution goals.

## Warnings
- Compliance issues often hide inside normal engineering work.
- Domain context may be incomplete.

## Blocks on
- Explicit incompatible conflict.
- Unsafe credential handling path.

## Evidence expected or emitted
- review_requested
- unresolved_dependency

## Examples
- Review a new dependency for licensing or secret-handling concerns.

## Limitations
- Falls back to: Manual compliance checklist with explicit limitations.

## Boundary
- May surface obligations and suggest safer paths. It may not grant compliance approval.

## Related docs
- `docs/jack/rules/09-compliance-security-license.md`
- `docs/jack/workflows/compliance-triage.md`

