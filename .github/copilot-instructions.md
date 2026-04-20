# JACK repository-wide instructions

This repository contains JACK's repo-scoped Copilot files and the longer docs that support them.

When editing this repository:

- write each file for its actual audience and purpose
- keep public-facing prose plain, modest, and practical
- keep `.github/` files and `AGENTS.md` concise
- use `docs/jack/` for longer rules, rationale, workflows, templates, examples, and support notes
- keep hook, skill, and agent-profile claims narrow and aligned with GitHub's documented surfaces
- use precise scope terms: `repo-scoped`, `user-scoped`, `cross-project`, and `environment-specific`
- do not present `docs/jack/inventory.json`, Markdown workflows, templates, examples, or hook notes as native runtime features
- keep one clear home for each policy instead of retelling the same rule everywhere
- prefer small, reversible edits and explicit evidence over broad rewrites
- verify platform claims before stating them

This repo has no application build, lint, or test suite.
Validation is targeted file-quality and path-check work:

- parse JSON files
- keep JSON pretty-printed
- keep Markdown readable and normal
- verify referenced paths after moves or renames
- verify that repo-facing files still agree with the longer docs in `docs/jack/`
- remove hidden or bidirectional Unicode characters and keep LF line endings
- do not ship throwaway placeholder links in public docs


