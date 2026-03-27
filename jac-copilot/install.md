# Install notes

JAC now ships in two layers.

- **Layer A** is the source pack in `jac-copilot/`
- **Layer B** is the native Copilot adapter layer in `.github/` plus `AGENTS.md`

Use the native adapter layer first when your environment supports it.
Use the source pack as the canonical long-form backing material.

## Verified GitHub Copilot surfaces

The following file locations are documented by GitHub Copilot documentation and are the first install path for this repo:

1. **Repository-wide instructions** at `.github/copilot-instructions.md`
2. **Path-specific instructions** at `.github/instructions/*.instructions.md` using `applyTo` frontmatter
3. **Agent instructions** in `AGENTS.md`

### Concrete install flow

If you are using this repository directly:

1. keep `.github/copilot-instructions.md`
2. keep `.github/instructions/`
3. keep `AGENTS.md`
4. keep `jac-copilot/` in the repository as the source pack those files summarize

If you are transplanting JAC into another repository:

1. copy `.github/copilot-instructions.md`
2. copy `.github/instructions/`
3. copy `AGENTS.md`
4. copy `jac-copilot/`
5. adjust only the adapter summaries if the target repository needs local wording, and keep the source-pack policy canon intact

## Portable extras and behavioral contracts

The following pieces remain useful, but they are not the primary verified activation path:

- `jac-copilot/manifest.json` as portable source-pack metadata
- `jac-copilot/hooks/` as behavioral hook contracts
- `jac-copilot/skills/` as behavioral skill contracts
- `jac-copilot/workflows/` as workflow notes and manual rails
- templates, schemas, docs, and examples under `jac-copilot/`

Do not present those files as proven native Copilot runtime primitives unless you verify that in your actual environment.

## Manual fallback mode

If your environment does not load the native adapter files reliably:

1. open `.github/copilot-instructions.md`
2. open the relevant file under `.github/instructions/`
3. open `AGENTS.md` if you are using a coding-agent style flow
4. use `jac-copilot/instructions.md` and the matching source-pack files as the long-form reference

That fallback is manual, but still usable.

## Environment differences

### GitHub.com
GitHub documents `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, and `AGENTS.md` as repository customization surfaces.
GitHub's docs currently note that path-specific instruction files on GitHub.com are used by Copilot coding agent and Copilot code review.

### VS Code
VS Code documentation and GitHub's Copilot docs both describe repository custom instructions based on these repo files.
Exact UX details can vary by extension version, so verify any editor-specific behavior you depend on.

### Copilot CLI
Copilot CLI documents the same repo-native files and also documents local instruction locations such as `$HOME/.copilot/copilot-instructions.md`.
This repo does not rely on those extra local paths as its primary public install story.
