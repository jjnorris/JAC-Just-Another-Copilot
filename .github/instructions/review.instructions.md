---
applyTo: "AGENTS.md,jac-copilot/rules/10-correctness-contracts.md,jac-copilot/rules/11-review-policy.md,jac-copilot/rules/12-reporting-and-traces.md,jac-copilot/rules/13-stop-conditions.md,jac-copilot/workflows/plan-review.md,jac-copilot/workflows/bugfix-with-proof.md,jac-copilot/workflows/verify-before-claim.md,jac-copilot/templates/correctness-contract.json,jac-copilot/templates/plan-review-comment.json,jac-copilot/templates/verification-report.json"
---

Non-trivial work should still read like JAC:

- state `given`, `must`, `must_not`, and `wiring_claim`
- distinguish autonomous work from approval-zone work
- ask for review before destructive, permission-expanding, or high-risk changes
- prefer narrowing a claim over pretending verification happened
- keep significant decisions traceable and task-scoped

If a review or verification rule changes in the source pack, make sure the adapter layer still reflects that change instead of drifting quietly.
