# Install scopes

Use this file to distinguish JACK's repo-scoped layout from user-scoped equivalents that some environments document.

## Repo-scoped (the primary JACK layout)

These files live in the repository and are the main way JACK is shipped:

| Path | Purpose |
|---|---|
| `.github/copilot-instructions.md` | broad repo-wide instructions |
| `.github/instructions/**/*.instructions.md` | path-specific or topic-specific instructions |
| `.github/skills/*/SKILL.md` | repo-scoped skills for supported agent-capable flows |
| `.github/hooks/*.json` | repo-scoped hooks |
| `AGENTS.md` | contributor / agent operating notes for this repo |
| `.github/agents/*.agent.md` | repo-scoped custom agent profiles, if present |
| `docs/jack/` | longer reference material, maintenance docs, templates, examples, and support notes |

Repo-scoped means:
- committed with the repository
- available to anyone using the repository in a supported environment
- the primary distribution model for JACK

## User-scoped (optional and environment-specific)

Some environments also document user-scoped Copilot files under the home directory.
These are not installed by JACK automatically.
They are separate, manual, per-user setup.

| Path | Purpose |
|---|---|
| `$HOME/.copilot/copilot-instructions.md` | user-scoped instructions across that user's projects |
| `~/.copilot/skills/` | user-scoped skills across projects |
| `~/.copilot/agents/` | user-scoped custom agents across projects |

User-scoped means:
- lives in the user's home directory
- can apply across multiple projects in supported environments
- separate from this repository's committed files

## Hooks remain repo-scoped

JACK does not claim a user-scoped hooks directory.
Hooks are kept repo-scoped under `.github/hooks/*.json`.
See `docs/jack/hook-contract-schema-families.md` and `docs/jack/hook-enforcement-truth-matrix.md` for the reconciled schema-family definitions and the runner-vs-contract enforcement mapping.
For CLI, GitHub documents hook loading from the current working directory, which still aligns with repo-scoped placement rather than a shared user hook directory.

## When to use each scope

Use **repo-scoped** placement when:
- you want JACK to travel with the repository
- you want collaborators to get the same native files
- you want support boundaries to be visible in version control

Use **user-scoped** placement when:
- you want personal instructions, skills, or agents across multiple projects
- the target environment explicitly documents those user-scoped home-directory paths
- you accept that the repo itself does not carry that configuration for other contributors

## Manual fallback

If a native surface is unavailable in your environment:
1. read the repo-scoped files directly
2. use `docs/jack/` as the longer reference set
3. keep support claims narrow and environment-specific

See `docs/jack/support-matrix.md` for environment notes.
