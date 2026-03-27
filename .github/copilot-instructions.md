# JAC repository-wide instructions

This repository is a GitHub Copilot discipline pack, not an application or service.
The native layer lives in `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `.github/skills/`, `.github/hooks/`, and `AGENTS.md`.
The longer supporting canon lives under `docs/jac/`.

When editing this repository:

- treat `docs/jac/` as the canonical long-form source
- keep the native adapter files concise, immediately useful, and derived from the canon
- keep public-facing prose boring, modest, and plainly written
- do not reference outside product names or imply any external runtime is required
- keep hook and skill claims narrow and aligned with GitHub's documented surfaces
- do not claim native runtime support for `docs/jac/source-pack-registry.json` or Markdown workflow files
- keep one canonical home per policy instead of duplicating rules across files
- preserve the extension or client boundary: native files for activation, `docs/jac/` for policy and rationale
- prefer small reversible edits and explicit evidence over broad rewrites
- if a Copilot platform claim matters, verify it from official docs before stating it

This repo has no application build, lint, or test suite.
Validation is mostly file-quality and wiring work:

- parse JSON files
- keep JSON pretty-printed
- keep Markdown readable and normal
- verify referenced paths if the supporting-canon inventory changes
- verify the native adapter files still match the supporting canon intent
- remove hidden or bidirectional Unicode characters and keep LF line endings
- do not ship throwaway placeholder links in public docs
