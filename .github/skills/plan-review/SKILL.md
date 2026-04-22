---
name: plan-review
description: Build the review artifact and route tasks through proceed or review-comment paths.
---

# plan-review

## Purpose
Build the review artifact and route tasks through proceed or review-comment paths.

## When to use
- before non-trivial work
- before approval-zone work

## Inputs
- correctness contract
- task scope
- initial plan

## Outputs
- review artifact
- review mode
- task-scoped comments

## What it checks
- Every non-trivial task needs a review artifact.
- Approval-zone work must request review.
- Comments must stay task-scoped and actionable.

## Warnings
- A good plan can still hide rollback gaps.
- Vague comments are not evidence.

## Blocks on
- Approval-zone work lacks approval.
- Plan has no explainable rollback or evidence path.

## Evidence expected or emitted
- review_requested
- review_comment_applied

## Examples
- Request review before deleting files or changing secrets handling.

## Limitations
- Falls back to: Manual plan review note.

## Boundary
- May request review or clear low-risk work to proceed. It may not approve blocked actions without policy basis.

## Related docs
- `docs/jack/rules/11-review-policy.md`
- `docs/jack/workflows/plan-review.md`
