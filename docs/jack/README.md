# JACK reference docs

This directory holds the longer reference material behind the repo-scoped files in `.github/` and `AGENTS.md`.

## Use this directory as a map

- `design-rationale.md` explains why JACK keeps the repo-scoped native layer short and keeps the longer canon here
- `install-scopes.md` separates repo-scoped placement from user-scoped equivalents some environments document
- `support-matrix.md` keeps support claims conservative and environment-specific
- `hook-payloads.md` explains what the shared hook runner actually reads
- `rules/`, `workflows/`, `templates/`, and `examples/` hold the longer policy, support notes, and reusable artifacts
- `inventory.json` is maintenance inventory for anchors, file classes, and validation targets

## When to use this directory

Read this directory when you need the longer policy text, a template, environment notes, or maintenance detail.

## What `inventory.json` is

`inventory.json` is maintenance inventory for this directory and the repo-scoped files that point back to it.
It is not presented as a GitHub Copilot package manifest or runtime surface.
