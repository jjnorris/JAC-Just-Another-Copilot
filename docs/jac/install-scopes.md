# Install scopes

JAC ships two distinct placement scopes: repo-scoped and user-scoped.
They are not interchangeable.

## Repo-scoped (primary)

These files are committed inside this repository under `.github/` plus `AGENTS.md`.
They are active for anyone working in this repo on a supported Copilot surface.

| File or path | What it does |
|---|---|
| `.github/copilot-instructions.md` | Broad repo-level instructions for Copilot |
| `.github/instructions/**/*.instructions.md` | Path-specific or topic-specific instruction files |
| `.github/skills/*/SKILL.md` | Named agent skills for agent-capable flows |
| `.github/hooks/*.json` | Agent hooks for documented hook event types |
| `AGENTS.md` | Agent operating notes, read by agent-capable flows |
| `.github/agents/*.agent.md` | Custom agent profiles, if present |

Repo-scoped files require no home-directory setup.
They are active when the repo is open in a supported environment.

## User-scoped (optional, environment-dependent)

Some Copilot environments document user-level placement under the home directory.
These are separate from this repository and require manual setup by the individual user.

| Path | What it does |
|---|---|
| `$HOME/.copilot/copilot-instructions.md` | Personal instructions applied across that user's projects |
| `~/.copilot/skills/` | Personal named skills |
| `~/.copilot/agents/` | Personal custom agent profiles |

User-scoped files are optional and environment-specific.
Not every Copilot surface loads them.
This repository does not install anything into your home directory.

## Hooks are not user-scoped

JAC does not claim a user-scoped hooks directory.
Hook files live under `.github/hooks/` and are repo-scoped.
No user-scoped hook placement is documented by GitHub as of this writing.

## Summary

- This repository ships the repo-scoped layer.
- User-scoped equivalents exist in some environments but require separate manual placement.
- Do not conflate the two scopes.

See `docs/jac/support-matrix.md` for environment-specific details.
