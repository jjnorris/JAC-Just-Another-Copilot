# Correctness contracts

## intent
Force explicit behavioral requirements and proof obligations before non-trivial edits.

## applies_when
- Any non-trivial implementation, refactor, or bug fix.

## non-negotiables
- Record `given`, `must`, `must_not`, and `wiring_claim` before write-heavy work.
- Verify each field after implementation.
- Warn on coverage misses and orphan symbols.
- Treat violated wiring claims as blockers.

## warnings
- Passing tests may not exercise the real integration path.
- Unused code can look correct while being disconnected.

## blockers
- Missing contract for non-trivial work.
- Broken or unverified wiring claim.

## examples
- Good: prove that a new workflow file is actually referenced by the manifest registry and docs.
- Bad: claim correctness because markdown renders cleanly.

## interplay
Uses `docs/jac/templates/correctness-contract.json`, `docs/jac/templates/verification-report.json`, and `docs/jac/workflows/verify-before-claim.md`.
