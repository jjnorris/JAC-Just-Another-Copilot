---
name: migration-safety
description: Review schema, migration, infra, or config changes for approval-zone risk, rollback path, and destructive-vs-additive behavior.
---

# migration-safety

## Purpose
Classify schema, migration, infra, or config changes by risk level and require a rollback path for destructive or irreversible operations.

## When to use
- Any change to `migrations/`, `db/`, `infra/`, `terraform/`, `helm/`, `k8s/`, `config/`, or environment files
- Any SQL `DROP`, `TRUNCATE`, or column removal
- Any change to secrets configuration, environment variable structure, or deployment manifests
- Any change that cannot be fully reversed by a single rollback command

## Inputs
- Diff or proposed change
- Current directory context
- Migration file content if available

## Outputs
- Risk classification: additive, destructive, or mixed
- Rollback path: explicit command or procedure, or "no safe rollback identified"
- Required review flag if destructive or irreversible
- Brief rationale

## What it checks
- Is the operation additive (add column, add table, add resource) or destructive (drop, truncate, delete, remove)?
- Is there a documented rollback or undo path?
- Does the change touch approval-zone paths?
- Does the change affect multiple environments or is it environment-scoped?

## Warnings
- Mixed additive-and-destructive in one migration is high risk.
- "Reversible in theory" is not the same as "has a tested rollback path."
- Config changes can be non-obvious migrations.

## Blocks on
- Destructive or irreversible change without an explicit rollback path.
- Change to approval-zone paths without a review flag.

## Evidence expected or emitted
- risk_level: additive | destructive | mixed
- rollback_path: explicit | none_identified
- review_required: true | false
- rationale

## Limitations
- Falls back to: flag the file for manual review and emit a rollback-note template.
- Does not execute migrations. Does not validate SQL syntax.

## Boundary
- Classification and gate only. Does not approve, apply, or roll back changes.

## Related docs
- `docs/jacks/rules/11-review-policy.md`
- `docs/jacks/templates/rollback-note.md`
- `docs/jacks/hook-payloads.md`


