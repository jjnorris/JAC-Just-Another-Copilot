# Execution loop

## intent
Force a repeatable sequence from intake to reporting.

## applies_when
- Every meaningful task.

## non-negotiables
- Intake before execution.
- Correctness contract before non-trivial edits.
- Review artifact before approval-zone work.
- Verification before success claims.
- Trace emission for significant actions.

## warnings
- Skipping steps causes hidden scope drift.
- Long uninterrupted execution increases rollback cost.

## blockers
- Execution without a plan on non-trivial tasks.
- Success claims without collected evidence.

## examples
- Good: clarify, contract, plan, review, execute, verify, report.
- Bad: edit first and rationalize later.

## interplay
Operationalizes the master `instructions.md` loop and depends on `10-correctness-contracts.md` and `11-review-policy.md`.
