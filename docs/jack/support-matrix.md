# Support matrix

Use this file to check where each JACK native surface is documented, where support is narrower, and where you should verify behavior in the exact environment you care about.

This matrix is a conservative maintenance shortcut, not a permanent truth table for every client.
It prefers these labels over overly crisp yes/no claims:
- **documented**
- **documented in agent-capable flows**
- **documented in some IDEs**
- **environment-specific**
- **not documented**
- **verify in target environment**

## Surface summary

| Surface | GitHub.com | VS Code / IDEs | Agent-capable flows | Copilot CLI |
|---|---|---|---|---|
| `.github/copilot-instructions.md` | documented | documented in some IDEs | documented | documented |
| `.github/instructions/**/*.instructions.md` | documented | documented in some IDEs | documented | documented |
| `AGENTS.md` | documented in agent-capable flows | environment-specific | documented | documented |
| `.github/skills/*/SKILL.md` | documented in agent-capable flows | environment-specific | documented | documented |
| `.github/hooks/*.json` | documented in agent-capable flows | not documented | documented | documented |
| `.github/agents/*.agent.md` | documented in agent-capable flows | environment-specific | documented | documented |
| user-scoped instructions | environment-specific | environment-specific | environment-specific | documented; verify in target environment |
| user-scoped skills | environment-specific | environment-specific | environment-specific | documented; verify in target environment |
| user-scoped agents | environment-specific | environment-specific | environment-specific | documented; verify in target environment |
| user-scoped hooks | not documented | not documented | not documented | not documented |

## Notes by environment

### GitHub.com

GitHub documents:
- repository-wide instructions
- path-specific instructions
- agent instructions in agent-capable flows
- hooks, skills, and custom agents in agent-capable flows

That does **not** mean every GitHub Copilot surface on GitHub.com loads every one of those files.
Treat hooks, skills, and agent profiles as narrower than broad repository instructions.

### VS Code and other IDEs

Repository-wide instructions and path-specific instructions are documented in some IDE environments.
`AGENTS.md`, skills, hooks, and custom-agent behavior are more dependent on the specific editor, mode, and release channel.
Do not compress all IDE behavior into one universal claim.

### Agent-capable flows

This is the safest place to describe JACK's broader native layer.
If a JACK feature depends on hooks, skills, or a custom agent profile, describe it as an agent-capable-flow feature unless GitHub's docs say more.

### Copilot CLI

GitHub documents:
- repository instructions
- path-specific instructions
- agent instructions
- hooks loaded from the current working directory
- user-scoped instructions under `$HOME/.copilot/copilot-instructions.md`
- user-scoped skills under `~/.copilot/skills/`
- user-scoped agents under `~/.copilot/agents/`

Even here, keep claims about exact behavior narrow and version-aware.

## What JACK does not claim

JACK does not claim:
- identical behavior across all Copilot surfaces
- user-scoped hook directories
- native consumption of `docs/jack/inventory.json`
- native command execution from Markdown workflow files
- universal skill, hook, or custom-agent loading in every chat UI

## Practical rule

If the feature you care about is:
- broad instructions: the docs are strong
- skills, hooks, or custom agents: verify in the target environment before making a strong promise

See `docs/jack/install-scopes.md` for placement rules.

### Hook reconciliation

- The reconciled hook schema families and the runner-vs-contract enforcement mapping are recorded in `docs/jack/hook-contract-schema-families.md` and `docs/jack/hook-enforcement-truth-matrix.md`.
- For the detailed edits performed during the reconciliation batches, see the batch closeouts in `docs/jack/` (for example `docs/jack/reconciliation_batch4_closeout.md`).


