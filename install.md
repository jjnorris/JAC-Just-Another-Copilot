# Install notes

JAC now ships in two layers.

- **Native layer:** `.github/` plus `AGENTS.md`
- **Supporting canon:** `docs/jac/`

Use the native layer first.
Use `docs/jac/` when you need the longer rationale, policy text, templates, or supporting artifacts.

## Repo-scoped native files this repo ships

These are the repo files JAC actually places where Copilot expects them:

1. `.github/copilot-instructions.md`
2. `.github/instructions/*.instructions.md`
3. `AGENTS.md`
4. `.github/skills/*/SKILL.md`
5. `.github/hooks/*.json`
6. `.github/agents/*.agent.md` if present

The instruction files and `AGENTS.md` are the broad repo guidance.
The skill and hook files are narrower agent surfaces and should be claimed only where GitHub documents them.

## Concrete repo install flow

If you are using this repository directly:

1. keep `.github/copilot-instructions.md`
2. keep `.github/instructions/`
3. keep `.github/skills/`
4. keep `.github/hooks/`
5. keep `AGENTS.md`
6. keep `.github/agents/` if present
7. keep `docs/jac/`

If you are transplanting JAC into another repository:

1. copy `.github/copilot-instructions.md`
2. copy `.github/instructions/`
3. copy `.github/skills/`
4. copy `.github/hooks/`
5. copy `AGENTS.md`
6. copy `.github/agents/` if you want the agent profile
7. copy `docs/jac/`
8. adjust only the concise adapter wording if the target repo truly needs local detail

## User-scoped or personal setup

This repository is repo-scoped.
It does not try to install anything into your home directory.

If you want a personal setup instead, GitHub's docs also describe user-level instruction and skill locations in some environments, such as `$HOME/.copilot/copilot-instructions.md` and `~/.copilot/skills/`.
Those are separate from what this repository ships.

## Supporting canon

`docs/jac/` is the human-maintained canon, not the runtime surface.
It keeps:

- long-form instructions
- rules and workflows
- templates and event contracts
- examples
- hook contract notes under `docs/jac/hook-contracts/`
- inventory metadata in `docs/jac/source-pack-registry.json`

## Manual fallback mode

If your environment does not load the native files reliably:

1. open `.github/copilot-instructions.md`
2. open the relevant file under `.github/instructions/`
3. open `AGENTS.md` if you are using an agent-style workflow
4. open the matching skill or hook file under `.github/` if the task is narrow and agent-specific
5. use `docs/jac/` as the longer reference set

That fallback is manual, but still usable.

## Environment differences

### GitHub.com
GitHub documents repository instructions, path-specific instructions, skills, and hooks.
Those surfaces are the concrete native story for this repo.

### VS Code
VS Code documents repository instructions and agent skills.
Editor behavior can still vary by version and mode, so keep any VS Code-specific claim narrow.

### Agent-capable flows and CLI
Agent hooks and some skill behavior are documented for Copilot coding agent and Copilot CLI style flows.
Do not describe them as guaranteed in every Copilot chat surface.
