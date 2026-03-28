# Compatibility notes

## Verified native GitHub Copilot surfaces used in this repo

These are the documented native surfaces JAC now uses directly:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`

Repository instructions and `AGENTS.md` are the broad repo layer.
Skills and hooks are narrower agent surfaces and should be described with that narrower scope.

## Optional native surfaces used only if present

This repo ships `.github/agents/jac.agent.md` as a custom agent profile.
It has valid YAML frontmatter (`name`, `description`) and a concise body derived from the supporting canon.
Additional `.github/agents/*.agent.md` files may be added if a real agent profile justifies the extra layer.

## Supporting canon that Copilot does not directly consume as a native runtime surface

The longer canon lives in `docs/jac/`.
That includes:

- `docs/jac/instructions.md`
- `docs/jac/rules/`
- `docs/jac/workflows/`
- `docs/jac/templates/`
- `docs/jac/event-contracts/`
- `docs/jac/examples/`
- `docs/jac/hook-contracts/`
- `docs/jac/source-pack-registry.json`

Those files are for policy, rationale, examples, maintenance, and manual fallback.
They are not a claim that GitHub natively consumes the whole folder.

## Manual fallback mode

If a native surface is unavailable in your environment, read the native `.github/` files and `AGENTS.md` as ordinary Markdown, then fall back to `docs/jac/` for the deeper policy text.

## Remaining claim boundaries

JAC does not claim:

- undocumented manifest support for `docs/jac/source-pack-registry.json`
- undocumented workflow-command execution from Markdown workflow files
- any extra hook fields beyond GitHub's documented hook configuration
- skill loading in every Copilot UI outside the documented agent-capable surfaces
- identical behavior across GitHub.com, VS Code, CLI, and future clients
