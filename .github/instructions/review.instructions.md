---
applyTo: "AGENTS.md,docs/jac/rules/10-correctness-contracts.md,docs/jac/rules/11-review-policy.md,docs/jac/rules/12-reporting-and-traces.md,docs/jac/rules/13-stop-conditions.md,docs/jac/workflows/plan-review.md,docs/jac/workflows/bugfix-with-proof.md,docs/jac/workflows/verify-before-claim.md,docs/jac/templates/correctness-contract.json,docs/jac/templates/plan-review-comment.json,docs/jac/templates/verification-report.json"
---

Non-trivial work should still read like JAC:

- state `given`, `must`, `must_not`, and `wiring_claim`
- distinguish autonomous work from approval-zone work
- ask for review before destructive, permission-expanding, or high-risk changes
- prefer narrowing a claim over pretending verification happened
- keep significant decisions traceable and task-scoped

If a review or verification rule changes in the source pack, make sure the adapter layer still reflects that change instead of drifting quietly.
