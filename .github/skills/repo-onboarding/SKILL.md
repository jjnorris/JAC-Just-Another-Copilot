---
name: repo-onboarding
description: Establish stack, package manager, test entrypoints, dangerous zones, and first bounded slice for a new or unfamiliar repository.
---

# repo-onboarding

## Purpose
Establish the key facts about a repository before any non-trivial work begins.

## When to use
- First session in an unfamiliar repository
- Start of a significant change in a part of the codebase not previously touched
- When the task requires knowing what is safe to touch

## Inputs
- Repository root directory listing
- Primary language and package manager files
- Known test configuration files
- CI or workflow files if present

## Outputs
- Stack summary (language, package manager, build tool)
- Likely test entrypoints (commands, not invented commands)
- Dangerous zones (infra, migrations, secrets, config roots)
- First bounded slice recommendation

## What it checks
- Does a package manager file exist? Which one?
- Are there test scripts in package.json, Makefile, pyproject.toml, or similar?
- Are there directories named `migrations/`, `infra/`, `db/`, `secrets/`, or similar?
- Does a CI config exist and what commands does it run?

## Warnings
- Do not invent test commands that are not in the repo.
- Do not assume a framework is present without file evidence.
- Dangerous zones are advisory, not a block, but must be reported.

## Blocks on
- Starting non-trivial work without establishing the dangerous-zone list.

## Evidence expected or emitted
- Stack facts with source file citation
- Test entrypoint with source citation
- Dangerous zone list with path evidence

## Limitations
- Falls back to: manual inspection of file listing and top-level config files.
- Does not run code. Does not execute build or test commands.

## Boundary
- Read-only discovery. No writes, no executions, no assumptions without file evidence.

## Related docs
- `docs/jac/rules/01-repo-truth.md`
- `docs/jac/rules/10-correctness-contracts.md`
