# Design rationale

JAC is organized as a portable authority pack because the repository does not verify a native GitHub Copilot package runtime for hooks, skills, workflows, or manifest loading.
That uncertainty is not a side note. It is one of the central design constraints.

The pack therefore puts the brain in readable markdown and JSON contracts.
This keeps policy portable across:
- user-level notes
- workspace overrides
- custom extensions
- manual operation
- future adapters if richer Copilot packaging becomes real and verified

The package is intentionally split so each policy has one canonical home.
Examples:
- memory law lives in `instructions.md` plus `rules/05-memory-policy.md` and the memory-manager skill
- tool least privilege lives in `rules/06-tool-governance.md` and the tool-guardian hook contract
- correctness obligations live in `rules/10-correctness-contracts.md` and the correctness-contract skill
- review policy lives in `rules/11-review-policy.md` and `workflows/plan-review.md`

This avoids policy drift and parallel abstractions.

The severe internal tone is deliberate.
The public README stays plain because JAC should not market unsupported runtime promises.
