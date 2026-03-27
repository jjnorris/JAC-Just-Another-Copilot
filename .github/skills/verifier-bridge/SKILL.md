---
name: verifier-bridge
description: Translate raw tests, diffs, runtime checks, and file inspections into verification evidence tied to the contract.
---

# verifier-bridge

## Purpose
Translate raw tests, diffs, runtime checks, and file inspections into verification evidence tied to the contract.

## When to use
- after a slice
- before reporting

## Inputs
- test output
- file registry
- correctness contract

## Outputs
- verification report
- coverage-gap summary

## What it checks
- Map evidence to contract statements.
- Prefer behavioral proof over status badges.
- Warn when evidence is indirect.

## Warnings
- Green checks can still miss live integration paths.
- Static review can miss runtime usage.

## Blocks on
- Critical promised behavior has no mapped evidence.

## Evidence expected or emitted
- coverage_miss
- usage_recorded

## Examples
- Show that every JSON file parses and that the manifest registry points to real files.

## Limitations
- Falls back to: Manual evidence mapping note.

## Boundary
- May classify evidence quality. It may not manufacture proof from unrelated signals.

## Related docs
- `docs/jac/workflows/verify-before-claim.md`
- `docs/jac/templates/verification-report.json`
