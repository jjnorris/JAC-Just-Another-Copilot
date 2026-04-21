---
applyTo: "AGENTS.md,docs/jacks/rules/10-correctness-contracts.md,docs/jacks/rules/11-review-policy.md,docs/jacks/rules/12-reporting-and-traces.md,docs/jacks/rules/13-stop-conditions.md,docs/jacks/workflows/plan-review.md,docs/jacks/workflows/bugfix-with-proof.md,docs/jacks/workflows/verify-before-claim.md,docs/jacks/templates/correctness-contract.json,docs/jacks/templates/plan-review-comment.json,docs/jacks/templates/verification-report.json"
---

Non-trivial work should still read like JACK:

- state `given`, `must`, `must_not`, and `wiring_claim`
- distinguish autonomous work from approval-zone work
- ask for review before destructive, permission-expanding, or high-risk changes
- prefer narrowing a claim over pretending verification happened
- keep significant decisions traceable and task-scoped

If a review or verification rule changes in `docs/jacks/`, update any repo-facing summary that depends on it.



