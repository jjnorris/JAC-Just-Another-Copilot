---
applyTo: "README.md,install.md,compatibility.md,AGENTS.md,.github/copilot-instructions.md,.github/instructions/**/*.instructions.md,.github/skills/**/*.md,docs/jac/**/*.md"
---

Use `docs/jac/` as the source of truth and keep the repo-native adapter files as concise derivations of that source.
The public voice must stay intentionally modest and a little dull.
Do not use hype language and do not drag in outside product names.
Keep the two-layer structure clear:

- native Copilot files first
- supporting canon second

Do not present `docs/jac/source-pack-registry.json`, `docs/jac/hook-contracts/`, or workflow documents as runtime features beyond what GitHub docs currently describe.
Keep `.github/skills/` and `.github/hooks/` honest, documented, and narrowly described.
If a policy already has a canonical home, update that home instead of creating a second version elsewhere.
