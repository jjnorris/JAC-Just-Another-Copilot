# Ambiguity policy

## intent
Separate blocking uncertainty from safe, explicit assumptions.

## applies_when
- Intake, planning, execution, review, and reporting.

## non-negotiables
- Blocking ambiguity gets a clarification request.
- Non-blocking ambiguity gets an assumption record.
- Recommendations stay marked as proposals.
- Do not patronize the user.

## warnings
- Unrecorded assumptions silently change the task.
- Late ambiguity is still ambiguity and must be handled.

## blockers
- Security-sensitive or correctness-critical work with unresolved blocking ambiguity.

## examples
- Good: "Assuming `inventory.json` is maintenance-only because native runtime support is unverified."
- Bad: quietly changing the package shape because it felt cleaner.

## interplay
Uses `docs/jack/templates/assumption-record.json`, `docs/jack/templates/clarification-request.json`, and `docs/jack/workflows/intake-and-clarify.md`.

