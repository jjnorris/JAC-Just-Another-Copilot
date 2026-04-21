---
name: trace-reporter
description: Emit durable structured events for meaningful decisions and actions.
---

# trace-reporter

## Purpose
Emit durable structured events for meaningful decisions and actions.

## When to use
- after review decisions
- after memory changes
- after tool denials
- after verification

## Inputs
- event payload data
- artifact references
- task identifiers

## Outputs
- structured event payloads
- usage summary

## What it checks
- Use the event contracts.
- Keep payloads task-scoped and evidence-linked.
- Record route and usage where available.

## Warnings
- Trace spam reduces value.
- Missing event fields reduce reviewability.

## Blocks on
- A required significant action cannot be traced at all.

## Evidence expected or emitted
- review_requested
- usage_recorded
- memory_recorded

## Examples
- Record that a review comment was applied and what artifact changed.

## Limitations
- Falls back to: Plain JSON note written from the schema.

## Boundary
- May emit records and usage summaries. It may not disguise missing evidence with logging noise.

## Related docs
- `docs/jacks/event-contracts/agent-trace.schema.json`
- `docs/jacks/event-contracts/review-events.schema.json`


