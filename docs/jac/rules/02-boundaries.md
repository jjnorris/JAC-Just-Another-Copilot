# Boundaries

## intent
Preserve stable ownership lines between authority pack, extension surface, planning, execution, and tools.

## applies_when
- Designing features, packaging behaviors, adapters, and review gates.

## non-negotiables
- Policy lives in the authority pack.
- Display and UX live in the extension or client surface.
- Tools do work; they do not define policy.
- Canonical state is not derived UI state.
- Fast path and heavy path must stay distinct.

## warnings
- Hidden orchestration inside UI code creates theater and drift.
- Duplicate policy in multiple files creates inconsistency.

## blockers
- Any design that moves authoritative gating into a display-only surface.

## examples
- Good: extension shows a review verdict that came from a policy file.
- Bad: extension locally decides whether a destructive action is safe without shared policy.

## interplay
Works with `06-tool-governance.md` and `11-review-policy.md`.
