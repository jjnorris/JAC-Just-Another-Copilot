# Hook contract schema families

This document records the schema families observed among `docs/jack/hook-contracts/*/hook.json` files in this repository.

Summary of families found

- `event-style` — purpose: observational event emitters and compact artifacts. Typical top-level keys (one or more):
  - `schema_version`, `name`, `event`, `intent`, `fires_on`, `deny_conditions`, `advisory_conditions`, `emits`, `notes`

- `trigger-style` — purpose: preflight inspection and gating (checks, advisories, blocks). Typical top-level keys (one or more):
  - `schema_version`, `name`, `trigger`, `inspects`, `warns_on`, `blocks_on`, `remediation`, `emitted_events`, `limitations`, `fallback_behavior`, `enforcement`

Mapping of current contracts to families (derived from repository files):

- event-style:
  - docs/jack/hook-contracts/session-start/hook.json
  - docs/jack/hook-contracts/error-occurred/hook.json

- trigger-style:
  - docs/jack/hook-contracts/tool-guardian/hook.json
  - docs/jack/hook-contracts/extension-surface-guard/hook.json
  - docs/jack/hook-contracts/assumption-recorder/hook.json
  - docs/jack/hook-contracts/context-budgeter/hook.json
  - docs/jack/hook-contracts/dependency-risk/hook.json
  - docs/jack/hook-contracts/telemetry-emitter/hook.json
  - docs/jack/hook-contracts/review-gate/hook.json
  - docs/jack/hook-contracts/secrets-scanner/hook.json
  - docs/jack/hook-contracts/structured-output/hook.json

Is the family split intentional or transitional?

Based on repository evidence (presence of `event`/`emits`/`intent` in some contracts and `trigger`/`inspects`/`blocks_on` in others, and the differing prose in the contract bodies), the split appears to be intentional by purpose: event-style contracts are focused on emitting compact artifacts and logging, while trigger-style contracts are focused on preflight inspection and gating. However, there is mild drift inside families (optional keys like `enforcement` appear in some trigger-style contracts but not others), which suggests some transitional variation in optional fields rather than a mistaken schema family.

Notes

- The validator is updated to treat these families as distinct and only check consistency within each family. This allows the repository to maintain separate, purposeful contract shapes without producing noise when families legitimately use different top-level keys.

