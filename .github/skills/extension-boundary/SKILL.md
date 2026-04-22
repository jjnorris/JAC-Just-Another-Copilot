---
name: extension-boundary
description: Keep the client surface limited to display, relay, and focused local interaction.
---

# extension-boundary

## Purpose
Keep the client surface limited to display, relay, and focused local interaction.

## When to use
- extension design
- editor integration decisions
- local UX planning

## Inputs
- extension proposal
- shared repo rules

## Outputs
- boundary compliance note
- surface capability summary

## What it checks
- Surface is not the brain.
- Local UX may display verdicts but not replace them.
- Prioritize targeted repo workflows and views.

## Warnings
- Feature creep can turn the client into a second orchestrator.
- Local-only verdict logic drifts from policy.

## Blocks on
- A proposed extension takes ownership of authoritative gating.

## Evidence expected or emitted
- model_route_chosen

## Examples
- Allow a tree view for traces, but keep policy evaluation in the shared rules.

## Limitations
- Falls back to: Manual boundary checklist in docs.

## Boundary
- May validate surface scope. It may not move policy ownership out of the shared rules.

## Related docs
- `docs/jack/rules/02-boundaries.md`
- `docs/jack/extension-boundaries.md`

