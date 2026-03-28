# Workspace rule example

A workspace override should stay local and explicit.

```md
# local workspace override

- project owner for review approvals: platform-team
- approval required for changes under `infra/` and `migrations/`
- preferred verification commands: `npm test`, `npm run lint`
- local compliance note: treat customer export files as regulated data
```

This narrows local behavior without pretending the repo-scoped pack changed its own canon.
