# Reporting and traces

## intent
Make meaningful actions reviewable, durable, and honest.

## applies_when
- Significant decisions, risk-bearing actions, verification, memory changes, and research use.

## non-negotiables
- Emit structured events for major actions.
- Separate verified fact, inference, assumption, proposal, unverified behavior, and next step.
- Record usage and route choices when available.
- Preserve evidence links or artifact references.

## warnings
- Narrative-only reporting hides missing evidence.
- Missing trace payloads make later review expensive.

## blockers
- Significant action with no durable evidence path when one is required.

## examples
- Good: record `review_requested`, `memory_recorded`, and `usage_recorded` with task scope.
- Bad: "done" with no evidence, no assumptions, and no route record.

## interplay
Anchors `event-contracts/`, `.github/skills/trace-reporter/SKILL.md`, and `.github/hooks/telemetry-emitter.json`.
