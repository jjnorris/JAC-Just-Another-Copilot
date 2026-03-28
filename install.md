# Install notes

Use this file when you want to keep JAC in this repository, transplant it into another repository, or compare repo-scoped and user-scoped placement.

## Repo-scoped files this repository ships

These files are committed in this repository and are the primary install shape for JAC:

1. `.github/copilot-instructions.md`
2. `.github/instructions/*.instructions.md`
3. `AGENTS.md`
4. `.github/skills/*/SKILL.md`
5. `.github/hooks/*.json`
6. `.github/agents/*.agent.md` if present
7. `docs/jac/`

Repository instructions and `AGENTS.md` provide broad repo guidance.
Skills, hooks, and custom agent profiles are narrower surfaces and should only be described where GitHub documents them.

## Using this repository directly

If you are using JAC in this repository, keep the repo-scoped files above together.
They are meant to travel as one set.

## Copying JAC into another repository

For a cross-project transplant:

1. copy `.github/copilot-instructions.md`
2. copy `.github/instructions/`
3. copy `.github/skills/`
4. copy `.github/hooks/`
5. copy `AGENTS.md`
6. copy `.github/agents/` if you want the custom agent profile
7. copy `docs/jac/`
8. edit only the repo-specific wording that truly needs to change in the target repository

Do not copy only `docs/jac/` and expect GitHub Copilot to discover it on its own.

## User-scoped equivalents

JAC itself is repo-scoped.
It does not install anything into your home directory.

Where GitHub documents user-scoped placement, some environments also support equivalents such as:

- `$HOME/.copilot/copilot-instructions.md`
- `~/.copilot/skills/`
- `~/.copilot/agents/`

Those locations are separate from this repository and remain environment-specific.

## What stays repo-scoped

Hooks stay repo-scoped here.
This repository does not claim a user-scoped hooks directory because GitHub does not document one for JAC to rely on.

The repo-scoped `.github/` files and `AGENTS.md` are the install target.
`docs/jac/` remains the longer reference set for rules, workflows, templates, examples, hook notes, support docs, and maintenance inventory in `docs/jac/inventory.json`.

## Manual fallback

If your environment does not load the repo-scoped files automatically:

1. read `.github/copilot-instructions.md`
2. read the relevant file under `.github/instructions/`
3. read `AGENTS.md` if you are working in an agent-style flow
4. read the matching skill, hook, or agent profile under `.github/` if the task is narrow
5. use `docs/jac/` for the longer rule set and support notes

## Environment differences

Repository instructions, skills, hooks, and custom agent profiles do not behave the same way everywhere.
Treat user-scoped support, skill loading, hook execution, and agent profile support as environment-specific unless GitHub documents the behavior for the environment you care about.
