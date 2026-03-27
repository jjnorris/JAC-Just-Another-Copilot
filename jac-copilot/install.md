# Install notes

This folder is designed as a portable authority pack.
At the time of writing, this repository does not verify a native GitHub Copilot global package schema for files like `manifest.json`, `hooks/`, `skills/`, or `workflows/`.
Treat installation as an adapter exercise, not a guaranteed official feature.

## Global user-level concept

A reasonable user-level setup is:

1. Copy or symlink `jac-copilot/` into a personal config or dotfiles location.
2. Point your editor's reusable Copilot instruction surface, if it has one, at `instructions.md`.
3. Keep `rules/`, `workflows/`, `templates/`, and `docs/` available for manual or tool-assisted reference.
4. Preserve the folder structure so the manifest file registry and references stay valid.

## Workspace override concept

Project-specific rules should live outside this pack and layer on top of it.
A workspace override can:
- narrow tool permissions
- tighten naming or layout conventions
- add domain-specific compliance notes
- declare local approval owners
- point to local tests and verification commands

A workspace override should not silently weaken the core non-negotiables.
If a project truly needs a weaker policy, make that change explicit and local.

## Possible adapter surfaces

These are examples, not verified claims for every editor build:

- a global custom-instructions feature
- a reusable prompt file or note pinned in the editor
- a workspace instruction file that references this pack
- a local extension that reads these files and exposes commands or views

Validate the actual surface in your environment before you depend on it.

## Suggested read order

1. `instructions.md`
2. any workspace override
3. relevant `rules/` files
4. relevant `workflows/` file
5. relevant templates and docs

## Manual fallback

If your Copilot surface does not support any clean install path:
- keep this folder in the repo or in a personal notes repo
- open `instructions.md` manually at session start
- use workflow files as operating rails
- use templates as copy-paste artifacts for review, assumptions, and verification

That fallback is plain, but it is honest and portable.
