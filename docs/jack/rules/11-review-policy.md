# Review policy

## intent
Require explicit review handling before risky or broad execution.

## applies_when
- Planning and executing non-trivial or approval-zone work.

## non-negotiables
- Start with a review artifact.
- Choose `always_proceed` or `request_review` explicitly.
- Approval-zone actions require review before execution.
- Review comments are task-scoped and must be traceable.

## warnings
- "Proceed by default" is not valid for destructive or permission-expanding work.
- Vague review notes are not sufficient evidence.

## blockers
- Approval-zone work without approval.
- Missing review artifact for non-trivial work.

## examples
- Good: request review before a dependency shift or schema migration.
- Bad: broad refactor executed because the model felt confident.

## interplay
Uses `docs/jack/workflows/plan-review.md`, `docs/jack/templates/plan-review-comment.json`, and `.github/hooks/review-gate.json`.

