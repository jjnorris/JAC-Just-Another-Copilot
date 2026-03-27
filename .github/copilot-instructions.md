# JAC repository-wide instructions

This repository is a GitHub Copilot discipline pack, not an application or service.
The repo-native adapter layer lives in `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, and `AGENTS.md`.
The longer source of truth lives under `jac-copilot/`.

When editing this repository:

- treat `jac-copilot/` as the canonical source pack
- keep the native adapter files concise, immediately useful, and derived from the source pack
- keep public-facing prose boring, modest, and plainly written
- do not reference outside product names or imply any external runtime is required
- do not claim native runtime support for `jac-copilot/manifest.json`, `jac-copilot/hooks/`, `jac-copilot/skills/`, or `jac-copilot/workflows/`
- keep one canonical home per policy instead of duplicating rules across files
- preserve the extension or client boundary: surface for display and relay, source pack for policy and gate logic
- prefer small reversible edits and explicit evidence over broad rewrites
- if a Copilot platform claim matters, verify it from official docs before stating it

This repo has no application build, lint, or test suite.
Validation is mostly file-quality and wiring work:

- parse JSON files
- keep JSON pretty-printed
- keep Markdown readable and normal
- verify manifest registry paths if the source-pack metadata changes
- verify the native adapter files still match the source-pack intent
- remove hidden or bidirectional Unicode characters and keep LF line endings
- do not ship throwaway placeholder links in public docs
