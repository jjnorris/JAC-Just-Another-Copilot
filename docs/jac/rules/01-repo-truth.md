# Repo truth

## intent
Keep implementation and reporting anchored to the current workspace and verified sources.

## applies_when
- Inspecting files, schemas, package shapes, extension surfaces, and runtime claims.

## non-negotiables
- Repo files outrank stale notes.
- Verified official docs outrank guesses.
- Unknown support must stay labeled as unknown.
- Report absence of evidence explicitly.

## warnings
- Doc fiction can drift away from the repo.
- Stored memory may be stale.

## blockers
- Claims that a file, API, feature, or runtime exists when it is unverified and required for success.

## examples
- Good: "The workspace does not verify a native manifest consumer, so this manifest is portable only."
- Bad: "The package installs cross-project (user-scoped)" with no documented install path to verify.

## interplay
Pairs with `08-research-policy.md` for external verification and `12-reporting-and-traces.md` for honest reporting.
