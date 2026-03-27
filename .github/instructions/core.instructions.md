---
applyTo: "README.md,AGENTS.md,.github/copilot-instructions.md,.github/instructions/**/*.instructions.md,jac-copilot/README.md,jac-copilot/instructions.md,jac-copilot/install.md,jac-copilot/compatibility.md,jac-copilot/docs/**/*.md"
---

Use `jac-copilot/` as the source of truth and keep the repo-native adapter files as concise derivations of that source.
The public voice must stay intentionally modest and a little dull.
Do not use hype language and do not drag in outside product names.
Keep the two-layer structure clear:

- native Copilot adapter files first
- source pack second

Do not present `manifest.json`, hooks, skills, or workflow documents as proven native Copilot runtime primitives.
If a policy already has a canonical home, update that home instead of creating a second version elsewhere.
