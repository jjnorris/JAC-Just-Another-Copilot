# Release readiness

Use this as a quick honesty check before calling JAC done.

## Verified

- `.github/copilot-instructions.md` exists
- `.github/instructions/*.instructions.md` exist and use `applyTo` frontmatter
- `AGENTS.md` exists
- public docs describe those files as the primary Copilot-facing layer

## Portable only

- `jac-copilot/manifest.json` is treated as source-pack metadata
- `jac-copilot/hooks/` are treated as behavioral contracts
- `jac-copilot/skills/` are treated as behavioral contracts
- `jac-copilot/workflows/` are treated as procedural rails and adapter inputs

## Manual fallback

- adapter files are still readable as plain Markdown
- source-pack files are still usable directly when native loading is unavailable

## Still adapter-dependent

- any executable hook behavior
- any executable skill behavior
- any workflow command surface
- any runtime that consumes `jac-copilot/manifest.json`
