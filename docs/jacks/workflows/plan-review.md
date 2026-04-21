# Plan review

## goal
Require a reviewable plan before non-trivial execution.

## when to use
- Before non-trivial implementation.
- Before approval-zone actions.

## prerequisites
- Correctness contract.
- Initial plan with bounded slices.

## steps
1. Create the review artifact.
2. Run Reuse, Convention, Explainability, Heightened Scrutiny, Correctness, Review, and Trace gates.
3. Mark policy mode as `always_proceed` or `request_review`.
4. Inject task-scoped review comments if concerns exist.
5. Proceed only when policy allows it.

## pause points
- After gate evaluation.
- After any review comment that changes scope or risk.

## evidence to collect
- review artifact
- review comments
- proceed decision or review request

## stop conditions
- Approval-zone action without approval.
- Plan remains unexplainable or lacks rollback notes.

## escalation or review path
- Route to human review with explicit requested decision.

## final report contract
State plan status, review mode, unresolved review comments, and approved next step.
