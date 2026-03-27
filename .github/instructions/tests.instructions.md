---
applyTo: "README.md,install.md,compatibility.md,AGENTS.md,.github/copilot-instructions.md,.github/instructions/**/*.instructions.md,.github/hooks/**/*.json,docs/jac/source-pack-registry.json,docs/jac/release-readiness.md,docs/jac/event-contracts/**/*.json,docs/jac/templates/**/*.json,docs/jac/examples/**/*.json"
---

This repository does not have an application test suite.
Do not invent one.
Use targeted validation instead.

For meaningful changes, validate the things this repo actually ships:

- JSON parses cleanly
- JSON stays pretty-printed
- Markdown stays readable
- referenced paths still exist after moves or renames
- native adapter files exist and still reflect the supporting canon
- verified GitHub Copilot surfaces are described honestly
- portable-only or canon-only files are clearly marked as such
- hidden or bidirectional Unicode characters are absent and line endings stay LF
- the donation note uses either a real link or the explicit placeholder token
