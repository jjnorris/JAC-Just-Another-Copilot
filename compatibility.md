# Compatibility notes

Use this file to check which GitHub Copilot surfaces JACK relies on, which ones are optional or environment-specific, and which files are only reference material.

## Repo-scoped surfaces used here

JACK uses these repo-scoped files where GitHub documents them:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`

Repository instructions and `AGENTS.md` provide broad repo guidance.
Skills and hooks are narrower surfaces and should be described with that narrower scope.

## Optional or environment-specific surfaces

This repository also ships `.github/agents/jac.agent.md` as a custom agent profile.
User-scoped instructions, skills, and agent profiles may exist in some environments, but they remain environment-specific.
Hook and skill availability outside agent-capable flows is also environment-specific.

## What `docs/jack/` is

`docs/jack/` is the longer reference set behind the repo-scoped files.
Use `docs/jack/README.md` for its map.
Those files support maintenance and manual fallback use.
They are not described here as native runtime surfaces.

## What JACK does not claim

JACK does not claim:

- undocumented runtime support for `docs/jack/inventory.json`
- undocumented command execution from Markdown workflow files
- any extra hook fields beyond GitHub's documented hook configuration
- a user-scoped hooks directory
- skill loading in every Copilot UI outside documented agent-capable surfaces
- identical behavior across GitHub.com, VS Code, CLI, and future clients

## Manual fallback

If a repo-scoped surface is unavailable in your environment, read the `.github/` files and `AGENTS.md` directly, then use `docs/jack/` for the longer reference material.
Use `docs/jack/support-matrix.md` when you need a more conservative environment-by-environment summary.

