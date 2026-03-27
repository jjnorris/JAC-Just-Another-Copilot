# Compatibility notes

## Verified GitHub Copilot surfaces

These are the documented native surfaces this repository now targets first:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`

They are the public activation layer for this repo.

## Portable extras and behavioral contracts

Everything under `jac-copilot/` remains useful, but not every part of it is a documented native Copilot runtime primitive.
Portable-only parts include:

- `manifest.json` as internal source-pack metadata
- `hooks/` as behavioral hook contracts
- `skills/` as behavioral skill contracts
- `workflows/` as procedural rails and adapter inputs
- templates, event schemas, docs, and examples

Those files can guide adapters, manual use, or future integrations.
They should not be described as already-executed native runtime features unless verified.

## Environment differences

### GitHub.com
Repository-wide instructions, path-specific instructions, and `AGENTS.md` are documented customization surfaces.
GitHub's docs also note that path-specific instruction files on GitHub.com currently apply to Copilot coding agent and Copilot code review.

### VS Code
Repository custom instructions are documented for VS Code as well.
Treat the repo-native files as the first layer, but keep editor-version-specific claims narrow unless you verify them directly.

### Copilot CLI
Copilot CLI documents the same repository files and also documents extra local instruction locations.
Those extra local paths are outside this repo's primary public release story.

## Manual fallback mode

If the native adapter files are not being consumed in your environment, use them as readable Markdown and fall back to the source pack under `jac-copilot/`.
The source pack is verbose on purpose and can be used directly without pretending runtime support exists.

## Release readiness note

- Verified: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`
- Portable only: `jac-copilot/manifest.json`, hooks, skills, workflows, templates, event schemas, docs, examples
- Manual fallback: read adapter files and source-pack files directly
- Adapter-dependent: executable hook behavior, executable skill behavior, workflow command surfaces, or any manifest consumer

## Optional prompt files

This release does not ship prompt files.
They are omitted because this revision did not verify a current official prompt-file path and syntax that should be claimed for this repository.
