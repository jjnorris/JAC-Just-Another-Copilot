# Support matrix

This file describes where each JAC native surface is expected to work.
Claims are narrow. If a surface is not explicitly documented by GitHub for an environment, it is marked as unknown or not applicable.

## Environment summary

| Surface | GitHub.com | VS Code | VS Code Insiders / agent flows | Copilot CLI |
|---|---|---|---|---|
| `.github/copilot-instructions.md` | yes | yes | yes | limited |
| `.github/instructions/**/*.instructions.md` | yes | yes | yes | limited |
| `AGENTS.md` | yes (agent flows) | partial | yes | yes |
| `.github/skills/*/SKILL.md` | coding agent | agent mode | agent mode | limited |
| `.github/hooks/*.json` | coding agent | not documented | preview | limited |
| `.github/agents/*.agent.md` | coding agent | coding agent | coding agent | unknown |
| User-scoped instructions | environment-specific | environment-specific | environment-specific | environment-specific |
| User-scoped skills | unknown | unknown | some environments | unknown |
| User-scoped hooks | not documented | not documented | not documented | not documented |

## Notes by environment

### GitHub.com

Repository instructions (`.github/copilot-instructions.md`) and path-specific instructions (`.github/instructions/`) are documented for Copilot on GitHub.com.
Skills and hooks are documented for agent-capable flows (coding agent).
Not every Copilot chat surface on GitHub.com loads skills or executes hooks.

### VS Code

Repository instructions are documented for VS Code Copilot Chat.
Agent skills are documented for agent-mode flows in VS Code.
Hook execution is not documented for standard VS Code Copilot Chat.
Behavior can vary between VS Code stable and VS Code Insiders.

### VS Code Insiders / agent-capable flows

This is where JAC's broader agent-mode features are most likely to appear, but support still varies by feature.
Skills are documented for agent mode, and hook support remains more cautious than the table may suggest on other surfaces.
Claims should still be verified against the current GitHub documentation before asserting any specific behavior.

### Copilot CLI

Repository instructions may be available depending on the version and mode.
Hook and skill support is limited and should not be assumed.
Verify against current CLI documentation before claiming any behavior.

## What is not claimed

JAC does not claim:

- identical behavior across all Copilot surfaces
- user-scoped hook directories in any environment
- that `docs/jac/inventory.json` is natively consumed by GitHub
- that Markdown workflow files are natively executed as commands
- that skills or hooks work in every Copilot chat UI

If behavior is environment-specific, it is labeled as such and not described as universal.

See `docs/jac/install-scopes.md` for placement details and scope terms.
