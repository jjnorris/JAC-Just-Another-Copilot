# Bounded implementation

## goal
Execute work in small, reversible, understandable slices.

## when to use
- Most normal implementation tasks.

## prerequisites
- Task-ready scope.
- Correctness contract.
- Plan review outcome.

## steps
1. Choose the smallest next slice.
2. Select least-privilege tools and budgets.
3. Make the change.
4. Verify the changed path immediately.
5. Emit trace and evidence.
6. Repeat only if the next slice is still justified.

## pause points
- After each slice.
- When a slice increases scope or risk.

## evidence to collect
- changed files
- verification note
- usage note if relevant

## stop conditions
- Budget breach.
- Evidence contradicts the plan.
- New approval-zone behavior appears.

## escalation or review path
- Return to plan review if the slice boundary moves.

## final report contract
List slices completed, evidence collected, and remaining bounded work.
