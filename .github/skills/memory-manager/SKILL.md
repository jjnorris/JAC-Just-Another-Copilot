---
name: memory-manager
description: Maintain bounded working memory and compact long-term knowledge records.
---

# memory-manager

## Purpose
Maintain bounded working memory and compact long-term knowledge records.

## When to use
- session start
- after a meaningful decision
- after completion of a slice

## Inputs
- active task state
- existing memory summaries
- artifact references

## Outputs
- working-memory summary
- knowledge item record

## What it checks
- Keep working memory short.
- Store decisions, constraints, rejected paths, unresolved risks.
- Never silently rewrite requirements.

## Warnings
- Chronology dumps waste context.
- Irrelevant retrieval floods prompts.

## Blocks on
- A proposed memory record changes requirement meaning.

## Evidence expected or emitted
- memory_retrieved
- memory_recorded

## Examples
- Store that a repo has no test harness instead of storing the whole command transcript.

## Limitations
- Falls back to: Working-memory-only mode.

## Boundary
- May summarize and retrieve relevant records. It may not alter source-of-truth requirements.

## Related docs
- `docs/jac/rules/05-memory-policy.md`
- `docs/jac/hook-contracts/context-budgeter/hook.json`
