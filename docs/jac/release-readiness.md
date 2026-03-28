# Release readiness

Use this as a quick honesty check before calling JAC done.

## Verified native files in this repo

- `.github/copilot-instructions.md` exists
- `.github/instructions/*.instructions.md` exist and use `applyTo` frontmatter
- `AGENTS.md` exists
- `.github/skills/*/SKILL.md` exist
- `.github/hooks/*.json` exist
- `.github/agents/jac.agent.md` exists with valid YAML frontmatter
- public docs describe repository instructions and `AGENTS.md` as the broad repo layer
- public docs describe skills and hooks as narrower documented agent surfaces

## Supporting canon only

- `docs/jac/source-pack-registry.json`
- `docs/jac/hook-contracts/`
- `docs/jac/workflows/`
- `docs/jac/templates/`
- `docs/jac/event-contracts/`
- `docs/jac/examples/`
- the longer docs under `docs/jac/`

## Manual fallback

- native files are still readable as plain Markdown or JSON
- `docs/jac/` is still usable directly when native loading is unavailable

## Still environment-specific

- which Copilot clients load which surfaces
- how widely hooks and skills are available outside agent-capable flows
- any undocumented runtime that might consume `docs/jac/source-pack-registry.json`
- any workflow-command behavior not documented by GitHub
