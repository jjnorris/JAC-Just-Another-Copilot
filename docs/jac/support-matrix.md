
### `docs/jac/support-matrix.md`
```md
# Support matrix

Use this file to check where each JAC native surface is documented, where support is narrower, and where you should verify behavior in the exact environment you care about.

This file prefers these labels over overly crisp yes/no claims:
- **documented**
- **documented in agent-capable flows**
- **documented in some IDEs**
- **environment-specific**
- **not documented**

## Surface summary

| Surface | GitHub.com | VS Code / IDEs | Agent-capable flows | Copilot CLI |
|---|---|---|---|---|
| `.github/copilot-instructions.md` | documented | documented in some IDEs | documented | documented |
| `.github/instructions/**/*.instructions.md` | documented | documented in some IDEs | documented | documented |
| `AGENTS.md` | documented in agent-capable flows | environment-specific | documented | documented |
| `.github/skills/*/SKILL.md` | documented in coding agent flows | environment-specific | documented | documented |
| `.github/hooks/*.json` | documented in coding agent flows | not documented | documented | documented |
| `.github/agents/*.agent.md` | documented in coding agent flows | environment-specific | documented | documented |
| user-scoped instructions | environment-specific | environment-specific | environment-specific | documented |
| user-scoped skills | environment-specific | environment-specific | environment-specific | documented |
| user-scoped agents | environment-specific | environment-specific | environment-specific | documented |
| user-scoped hooks | not documented | not documented | not documented | not documented |

## Notes by environment

### GitHub.com

GitHub documents:
- repository-wide instructions
- path-specific instructions
- agent instructions in agent-capable flows
- hooks, skills, and custom agents in coding-agent style flows

That does **not** mean every GitHub Copilot surface on GitHub.com loads every one of those files.
Treat hooks, skills, and agent profiles as narrower than broad repository instructions.

### VS Code and other IDEs

Repository-wide instructions and path-specific instructions are documented in some IDE environments.
`AGENTS.md`, skills, hooks, and custom-agent behavior are more dependent on the specific editor, mode, and release channel.
Do not compress all IDE behavior into one universal claim.

### Agent-capable flows

This is the safest place to describe JAC's broader native layer.
If a JAC feature depends on hooks, skills, or a custom agent profile, describe it as an agent-capable-flow feature unless GitHub's docs say more.

### Copilot CLI

GitHub documents:
- repository instructions
- path-specific instructions
- agent instructions
- hooks loaded from the current working directory
- personal instructions under `$HOME/.copilot/copilot-instructions.md`
- personal skills under `~/.copilot/skills/`
- personal agents under `~/.copilot/agents/`

Even here, keep claims about exact behavior narrow and version-aware.

## What JAC does not claim

JAC does not claim:
- identical behavior across all Copilot surfaces
- user-scoped hook directories
- native consumption of `docs/jac/inventory.json`
- native command execution from Markdown workflow files
- universal skill, hook, or custom-agent loading in every chat UI

## Practical rule

If the feature you care about is:
- broad instructions: the docs are strong
- skills, hooks, or custom agents: verify the target environment before making a strong promise

See `docs/jac/install-scopes.md` for placement rules.
