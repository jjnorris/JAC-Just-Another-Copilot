---
applyTo: "AGENTS.md,docs/jack/rules/10-correctness-contracts.md,docs/jack/rules/11-review-policy.md,docs/jack/rules/12-reporting-and-traces.md,docs/jack/rules/13-stop-conditions.md,docs/jack/workflows/plan-review.md,docs/jack/workflows/bugfix-with-proof.md,docs/jack/workflows/verify-before-claim.md,docs/jack/templates/correctness-contract.json,docs/jack/templates/plan-review-comment.json,docs/jack/templates/verification-report.json"
---

Non-trivial work should still read like JACK:

- state `given`, `must`, `must_not`, and `wiring_claim`
- distinguish autonomous work from approval-zone work
- ask for review before destructive, permission-expanding, or high-risk changes
- prefer narrowing a claim over pretending verification happened
- keep significant decisions traceable and task-scoped

If a review or verification rule changes in `docs/jack/`, update any repo-facing summary that depends on it.
