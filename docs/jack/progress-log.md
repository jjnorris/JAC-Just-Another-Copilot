# Progress Log

## 2026-04-05 — Context-pack compiler batch

- **Added**: `scripts/compile_context_pack.py` — compiler for context packs (spec + plan + evidence -> JSON pack).
- **Added**: `scripts/run_context_pack_checks.py` — verification runner using fixture spec/plan/evidence.
- **Verified**: `run_context_pack_checks.py` ran successfully: "Context pack checks OK".
- **Notes**: compiler emits `project_memory_seed`, `proposed_skill_candidates`, `proposed_tool_policy`, `recommended_rules`, and an `evidence_index` referencing input JSONL evidence.

Small, conservative changes only; no external network calls in verification runner.

## 2026-04-05 — Context bundle writer batch

- **Added**: `scripts/write_context_bundle.py` — writes a repo-local JACK bundle under `jack/` from a compiled context pack.
- **Added**: `scripts/run_context_bundle_checks.py` — verification runner that compiles a small pack, runs the writer, and asserts expected bundle files and content.
- **Generated**: `jack/context-pack.json`, `jack/proposed-instructions.md`, `jack/evidence-index.json`, `jack/project-memory-seed.json`, `jack/proposed-skills.json`, `jack/proposed-tool-policy.json`, `jack/bundle-manifest.json`, `jack/README.md`.
- **Verified**: `run_context_bundle_checks.py` ran successfully: "Context bundle checks OK".
- **Verified**: `python3 scripts/validate_repo.py` ran successfully: "JACK repository validation passed.".

Notes: Generated files are proposal-only; nothing is auto-applied. Reviewers must manually adopt or adapt proposals.
 
## 2026-04-05 — Context adoption assistant batch

- **Added**: `scripts/review_context_adoption.py` — compares repo-local instruction/context files against `jack/` bundle and emits adoption-report.json and adoption-report.md.
- **Added**: `scripts/run_adoption_review_checks.py` — verification runner exercising no-instructions, existing-instructions, and conflict scenarios.
- **Generated**: `jack/adoption-report.json`, `jack/adoption-report.md` (proposal-only review artifacts).
- **Verified**: `run_adoption_review_checks.py` ran successfully: "Adoption review checks OK".
- **Verified**: `python3 scripts/validate_repo.py` ran successfully: "JACK repository validation passed.".

Notes: Adoption artifacts are proposal-only; do not auto-apply. Reviewers must manually inspect and merge any changes.

## 2026-04-05 — Context patchset generator batch

- **Added**: `scripts/generate_instruction_patchset.py` — dry-run patchset generator that converts JACK bundle + adoption report into a section-aware proposed patchset under `jack/`.
- **Added**: `scripts/run_patchset_checks.py` — verification runner for the patchset generator covering create-if-missing, section-aware proposals, and conflict/manual-only scenarios.
- **Generated**: `jack/proposed-patchset.json`, `jack/proposed-patchset.md` (proposal-only artifacts).
- **Verified**: `run_patchset_checks.py` ran successfully: "Patchset checks OK".
- **Verified**: `python3 scripts/validate_repo.py` ran successfully: "JACK repository validation passed.".

Notes: All outputs are dry-run proposals; do not apply automatically. Reviewers should follow the human adoption checklist before manual edits.

# Progress Log

## Current slice
- Added a minimal `scripts/github_webhook_adapter.py` to convert GitHub webhook JSON into a hook payload and invoke the existing CLI wrapper (default hook: `telemetry-emitter`).
- Added `scripts/run_adapter_checks.py` to verify adapter behavior: with a `.git` directory the adapter writes a `.git/jac-hooks/telemetry-emitter.jsonl` artifact; without `.git` it emits the advisory and leaves no artifact.
- Verified the adapter checks and repository validator pass.
- Added a minimal `scripts/github_webhook_server.py` — a small stdlib HTTP shim that accepts POST /webhook and forwards to the existing adapter.
- Added `scripts/run_server_checks.py` — starts the shim in-thread and exercises: a successful POST and a malformed-JSON POST.
- Verified the HTTP shim checks and repository validator pass.
 - Added optional HMAC verification to `scripts/github_webhook_server.py` (env: `JAC_WEBHOOK_SECRET`) and extended `scripts/run_server_checks.py` to verify signed and unsigned POST behavior.
 - Verified the server checks (signed/unsigned/malformed) and repository validator pass.
 - Added optional artifact-directory override: `JAC_ARTIFACT_DIR` (env) to allow writing hook artifacts outside of a `.git` directory; updated `scripts/run_adapter_checks.py` to verify override behavior.
 - Verified the adapter checks (including override) and repository validator pass.
 - Added a small docs lookup MVP: `scripts/docs_lookup.py` to fetch, normalize, chunk, and emit JSONL evidence from curated official docs sources; added `scripts/run_docs_lookup_checks.py` which uses local fixture pages to verify fetch/normalize/chunk/search and JSONL output.
 - Verified the docs lookup checks and repository validator pass.
 - Added a minimal spec-intake normalizer: `scripts/spec_intake.py` to convert freeform project briefs into structured JSON (including omission detection and recommended clarifying questions); added `scripts/run_spec_intake_checks.py` to verify omission detection for underspecified, complete, and jurisdiction-sensitive briefs.
 - Fixed a deprecation warning in `scripts/docs_lookup.py` by using a timezone-aware `datetime.now(timezone.utc)` for `fetched_at` timestamps.
 - Verified spec intake checks, docs lookup checks, and repository validator pass.
 - Added an intake->lookup bridge: `scripts/intake_to_lookup.py` which converts a `spec_intake` artifact (or raw text) into prioritized docs lookup requests and can optionally execute them through `scripts/docs_lookup.py`.

## 2026-04-06 — Repo task research bridge batch

- **Added**: `scripts/repo_task_research.py` — bridge that consumes `jack/repo-stack-profile.json` and repo docs evidence to produce a grounded, task-specific implementation brief and concise next-steps.
- **Behavior**: reuses existing profile and evidence when present; falls back to at most two bounded docs lookups (official-docs-first) if evidence is missing or insufficient. Outputs are recommendation-only and include `do_not_auto_apply: true`.
- **Executed (smoke)**: ran a single focused invocation for the task: "Improve JACK's repo profiling and docs selection flow for real-world repositories" and wrote `jack/repo-task-brief.json`, `jack/repo-task-brief.md`, and `jack/repo-task-next-steps.md` (and appended bounded fallback evidence files when used).
- **Notes**: This slice is product-focused: it produces operator-facing, actionable briefs instead of additional meta reporting layers. No verification runners or repo-wide validators were added or run beyond the single smoke invocation.
 - Added `scripts/run_intake_to_lookup_checks.py` which verifies planning vs executed paths using the local fixture docs server.
 - Verified intake->lookup checks and repository validator pass.

## Tests added or updated
 - Added `test_assumption_recorder_cli_appends_payload_and_emits_advisory_for_assumption_prompt_when_git_dir_exists`.
 - Added `test_assumption_recorder_cli_appends_payload_and_stays_quiet_on_neutral_prompt_when_git_dir_exists`.
 - Added `test_context_budgeter_cli_appends_payload_and_stays_quiet_at_threshold_when_git_dir_exists`.
 - Added `test_context_budgeter_cli_appends_payload_and_emits_advisory_for_over_threshold_prompt_when_git_dir_exists`.
 - Added `test_structured_output_cli_emits_parse_advisory_without_git_dir_and_writes_no_local_artifact`.
 - Added `test_structured_output_cli_stays_quiet_without_git_dir_on_valid_json_and_writes_no_local_artifact`.
 - Added `test_session_start_cli_emits_secret_advisory_without_git_dir_and_writes_no_local_artifact`.
 - Added `test_session_start_cli_emits_json_without_git_dir_and_writes_no_local_artifact`.
 - Added `test_review_gate_cli_denies_destructive_without_git_dir`.
 - Added `test_review_gate_cli_stays_quiet_on_benign_command_without_git_dir`.
 - Added `test_tool_guardian_cli_denies_suspected_exfiltration_without_git_dir`.
 - Added `test_tool_guardian_cli_stays_quiet_on_benign_command_without_git_dir`.
 - Added `scripts/github_webhook_adapter.py` (integration adapter for GitHub events).
 - Added `scripts/run_adapter_checks.py` (small verification runner for the adapter).

## Current passing counts
 - `python3 scripts/hook_regression_tests.py`: 52 tests passing.
 - `python3 scripts/verify_local_checks.py`: passing.
 - `python3 scripts/validate_repo.py`: passing.
 - `python3 scripts/run_server_checks.py`: passing.

## 2026-04-07 — Edit sketch batch

- **Added**: `scripts/repo_task_edit_sketch.py` — generates a conservative edit sketch for a repo task.
- **Ran**: `python -u scripts/repo_task_edit_sketch.py --repo-root . --task "Improve JACK's repo profiling and docs selection flow for real-world repositories"` producing `jack/repo-task-edit-sketch.json` and `jack/repo-task-edit-sketch.md`.
- **Verified**: Both artifacts exist; JSON contains non‑empty `target_file` and `suggested_change_shape` fields.

## 2026-04-07 — `load_spec` hardening

- **Changed**: `scripts/intake_to_lookup.py::load_spec` — replaced a fragile one-line JSON loader with a bounded, conservative loader that:
	- validates that the provided path exists and is a file,
	- reads file text with explicit IO error handling,
	- parses JSON with clear, user-friendly errors on decode failure,
	- asserts the parsed value is a JSON object (`dict`) and raises `TypeError` otherwise.
- **Rationale / Evidence**: The `jack/repo-task-inspect.json` and `jack/repo-task-edit-sketch.json` artifacts identified `scripts/intake_to_lookup.py` and the `def load_spec` symbol as the best first-edit target; the previous implementation was `return json.loads(spec_file.read_text(encoding="utf-8"))` (one-line) which produces opaque tracebacks on malformed or missing inputs.
- **YAML fallback**: Intentionally NOT added — repository contains no existing YAML parsing dependency, and adding one would broaden scope; the error message now explicitly instructs the human to convert YAML to JSON or add YAML support in a follow-up change.
- **Validation**: Ran the integrated JACK MVP entrypoint once after the change (`python -u scripts/run_repo_task_flow.py --repo-root . --task "Make JACK's final outputs more directly useful to a human who is about to edit one file"`). The run completed and `jack/repo-task-edit-sketch.json` and related artifacts were produced; no crash originated from `scripts/intake_to_lookup.py` during that run.

## 2026-04-07 — `load_spec` regression test

- **Added**: `scripts/test_intake_to_lookup.py` — a minimal `unittest`-style regression test that protects the hardened `load_spec` behavior.
- **Covered behaviors**:
	- valid JSON object file -> returns `dict`
	- missing file -> raises `FileNotFoundError`
	- invalid JSON -> raises `ValueError` with an explicit message
	- non-object JSON (e.g., list) -> raises `TypeError`
- **Local test run**: Executed the focused test only using the project Python (`python -m unittest scripts.test_intake_to_lookup -v`); the single-file run completed and all tests passed.

## 2026-04-07 — planner ranking hardening

- **Changed**: `scripts/repo_task_plan.py::rank_files` — small, conservative improvement: when ranking candidate files, the planner now inspects candidate file contents (if readable) for code-facing signals such as `def load_spec`, `load_spec`, and other intake/plan/inspect tokens and boosts files that contain those tokens. This reduces false positives where a workflow or README is ranked above a script that actually contains the target function.
- **Rationale / Evidence**: The integrated run for task "Find the weakest code-facing recommendation..." produced `jack/repo-task-plan.json` recommending `.github/workflows/validate-jac.yml` while `jack/repo-task-inspect.json` and `jack/repo-task-edit-sketch.json` pointed at `scripts/intake_to_lookup.py::def load_spec`. The planner's filename-only heuristic caused this misalignment; content-aware ranking reduces that mismatch.
- **Narrow test added**: `scripts/test_repo_task_plan.py` — ensures that a script containing `def load_spec` is ranked above a workflow file by the planner ranking function.
- **Validation**: Ran the new planner test only (`python -m unittest scripts.test_repo_task_plan -v`) — test passed. Then re-ran the integrated JACK flow once to confirm artifacts were generated and the plan now ranks `scripts/intake_to_lookup.py` higher when content signals are present.

## Intentionally deferred gap
- Full end-to-end GitHub event payload coverage remains out of scope for this slice.

## 2026-04-05 — Context freshness assessor batch

- **Added**: `scripts/assess_context_freshness.py` — conservative freshness assessor that inspects `jack/` artifacts and repo signals (file presence and modification timestamps) and emits recommendation-only refresh plans.
- **Added**: `scripts/run_freshness_checks.py` — verification runner exercising four scenarios: fully-fresh, stale pack older than sources, missing evidence referenced by the evidence-index, and missing downstream adoption report.
- **Generated (fixture)**: `jack/freshness-report.json`, `jack/freshness-report.md` (under inspected repo or fixture repo; recommendation-only artifacts).
- **Behavior**: The assessor reports `artifacts_checked`, `repo_signals_checked`, `stale_items`, `missing_items`, `broken_references`, `recommendations`, `recommended_refresh_order`, `safe_to_skip`, and `manual_review_notes` in the JSON output. The MD output summarizes what looks stale, what looks current, and the conservative recommended refresh order. All outputs explicitly state "recommendation-only" and `do_not_auto_refresh` guidance.
- **Verified**: `run_freshness_checks.py` ran successfully: "Freshness checks OK".
- **Notes**: This slice is intentionally recommendation-only — it does not auto-run refreshes, apply patches, or mutate repository files. Refresh recommendations are dependency-aware (evidence -> intake/compile -> bundle -> adoption -> patchset) and require manual review before execution.

## 2026-04-05 — Context refresh planner batch

- **Added**: `scripts/generate_refresh_plan.py` — generates a dependency-aware, human-reviewable refresh plan from `jack/freshness-report.json` and writes `jack/refresh-plan.json` and `jack/refresh-plan.md` (proposal-only).
- **Added**: `scripts/run_refresh_plan_checks.py` — verification runner exercising fresh, stale-pack, missing-evidence, and missing-adoption scenarios; asserts plan JSON and MD are written and include conservative commands.
- **Generated (proposal-only)**: `jack/refresh-plan.json`, `jack/refresh-plan.md` (under inspected repo or fixture repo).
- **Behavior**: The refresh planner emits both a `minimal_plan` (targeted steps inferred from the freshness report) and a `full_plan` (the complete JACK pipeline order). Each recommended step includes conservative, edit-first `recommended_commands` and explicit `prerequisites`. The JSON includes `do_not_auto_execute: true` and `manual_review_required` flags.
- **Verified**: `run_refresh_plan_checks.py` ran successfully: "Refresh plan checks OK".
- **Notes**: This batch remains strictly recommendation-only — it does not run refreshes, apply patches, or mutate repository files. Human reviewers must inspect and run the proposed commands.

## 2026-04-05 — Maintenance runbook batch

- **Added**: `scripts/generate_maintenance_runbook.py` — generator that converts `jack/refresh-plan.json` into a human-reviewable `jack/maintenance-runbook.json` and `jack/maintenance-runbook.md` (proposal-only).
- **Added**: `scripts/run_runbook_checks.py` — verification runner that uses a fixture `refresh-plan` to validate runbook generation behavior without requiring live artifacts.
- **Behavior**: The generator groups recommended commands into conservative flows, labels review-oriented steps, and emits `manual_review_points` plus `do_not_auto_execute: true` to ensure outputs are recommendation-only. It does not execute any commands.
- **Verified**: `run_runbook_checks.py` ran successfully: "Runbook checks OK".
- **Prerequisite**: Live repo does not contain `jack/refresh-plan.json` at this time; the generator will not write live `jack/maintenance-runbook.*` artifacts until a `jack/refresh-plan.json` is present. No live runbook was fabricated in this batch.
- **Notes**: This slice is conservative and recommendation-only. To produce a live runbook, run the refresh-planner to create `jack/refresh-plan.json`, then run `python3 scripts/generate_maintenance_runbook.py` and inspect the outputs.

## 2026-04-05 — JACK status dashboard batch

- **Added**: `scripts/generate_jack_status.py` — conservative status generator that inspects `jack/` artifacts and repo signals and emits `jack/status.json` and `jack/status.md` (proposal-only).
- **Added**: `scripts/run_status_checks.py` — verification runner that creates fixture repos and verifies detection of present/current, stale, missing, blocked, and review-pending states.
- **Behavior**: The status generator reports `artifacts_present`, `artifacts_missing`, `freshness_state`, `adoption_state`, `patchset_state`, `runbook_state`, `blocked_items`, `pending_human_review`, `recommended_next_action`, and `do_not_auto_apply`. It is conservative and dependency-aware (e.g., runbook blocked by missing refresh plan).
- **Verified**: `run_status_checks.py` ran successfully: "Status checks OK" (fixture-based). The generator is recommendation-only and does not mutate repository files.
- **Notes / Prerequisite**: The generator reports blockers when upstream artifacts are missing (for example, maintenance runbook generation is blocked if `jack/refresh-plan.json` is absent). The script will not fabricate missing upstream artifacts.

## 2026-04-05 — Live artifact writer batch

- **Added**: `scripts/write_live_jack_artifacts.py` — safe driver that invokes existing, read-only JACK generators to produce live, recommendation-only outputs under `jack/` when prerequisites permit. It orchestrates: freshness assessor -> refresh planner -> status generator (each called with `--repo-root`) and records what was written, skipped, or blocked.
- **Added**: `scripts/run_live_artifact_checks.py` — verification runner that uses temporary repos to verify: successful live writes when inputs exist; blocked/skipped behavior when prerequisites are absent; and that a `jack/live-artifact-write-report.*` is produced with `do_not_auto_apply: true`.
- **Outputs written**: `jack/freshness-report.json`, `jack/freshness-report.md`, `jack/refresh-plan.json`, `jack/refresh-plan.md`, `jack/status.json`, `jack/status.md`, and `jack/live-artifact-write-report.json`/`.md` (only when run in a repo with adequate prerequisites or when generators succeed).
- **Behavior**: The writer is conservative — it only writes recommendation-only artifacts, records blocked items when prerequisites are missing, and never mutates repository instructions or applies patches.
- **Verified**: `run_live_artifact_checks.py` ran successfully: "Live artifact checks OK". `python3 scripts/validate_repo.py` passed: "JACK repository validation passed.".
- **Notes / Deferred**: The writer does not generate adoption patches or apply proposed patchsets; those remain proposal-only and require manual review. The maintenance runbook remains a separately gated artifact (it is reported as blocked until `jack/refresh-plan.json` exists, if applicable).

## 2026-04-05 — Adoption-readiness summary batch

- **Added**: `scripts/generate_adoption_readiness.py` — conservative adoption-readiness generator that inspects `jack/` artifacts (adoption report, proposed instructions, proposed patchset, freshness/refresh/status) and synthesizes a structured `jack/adoption-readiness.json` and human-readable `jack/adoption-readiness.md` to help humans decide whether the repository is ready for manual adoption of JACK proposals.
- **Added**: `scripts/run_adoption_readiness_checks.py` — verification runner that exercises clearly-blocked, partially-ready, and ready-for-manual-review fixture scenarios and asserts the readiness outputs include conservative flags and `do_not_auto_apply: true`.
- **Behavior**: The readiness generator classifies the repository into explicit, explainable readiness states (`not_ready`, `partially_ready`, `ready_for_manual_review`) and reports the specific artifacts considered, missing prerequisites, pending review items, any conflicts discovered in adoption outputs, recommended next actions, and a `safe_to_adopt_now` boolean. The generator is conservative: it never resolves conflicts, never applies patches, and never mutates repository files.
- **Verified**: `run_adoption_readiness_checks.py` ran successfully: "Adoption readiness checks OK". `python3 scripts/validate_repo.py` passed: "JACK repository validation passed.".
- **Notes / Blockers**: The readiness assessment treats missing or conflicting adoption outputs as blockers; it will not fabricate missing inputs. Human review remains required for any `ready_for_manual_review` state before manual adoption is performed.

## 2026-04-05 — Adoption checklist batch

- **Added**: `scripts/generate_adoption_checklist.py` — generator that composes a human-reviewable, ordered manual adoption checklist from JACK artifacts (`jack/adoption-readiness.json`, `jack/adoption-report.*`, `jack/proposed-instructions.*`, `jack/proposed-patchset.*`, and related status/refresh artifacts). The generator writes `jack/adoption-checklist.json` and a readable `jack/adoption-checklist.md` and is explicitly recommendation-only (`do_not_auto_apply: true`).
- **Added**: `scripts/run_adoption_checklist_checks.py` — verification runner that creates isolated fixtures for three conservative scenarios (blocked, partially-ready, ready-for-manual-review), invokes the generator, and asserts the checklist contains explicit ordered steps, manual-review gates, blockers, and `do_not_auto_apply: true`.
- **Behavior**: The checklist includes `readiness_state`, `artifacts_considered`, `ordered_manual_steps` (clear, numbered steps with pause points), `manual_review_gates` (explicit pause reasons), `files_to_review`, `patchsets_to_review`, `conflicts_to_resolve`, `safe_to_delay`, and `recommended_start_point`. The generator avoids fabricating happy-path advice when prerequisites are missing — it instead emits a blocked checklist that explains precisely what must be produced or resolved first.
- **Verification**: `scripts/run_adoption_checklist_checks.py` was executed and passed in fixture scenarios: "Adoption checklist checks OK". `python3 scripts/validate_repo.py` was run and passed: "JACK repository validation passed.".
- **Notes / Rationale**: This checklist is intentionally the next conservative human-facing step: it helps a reviewer follow a deterministic, minimal sequence for manual adoption without performing any automatic edits. It codifies the pause points and explicitly documents what can safely be delayed (for example, maintenance runbook review) versus what must be resolved before manual adoption (missing adoption report, adoption conflicts, or stale patchsets).

## 2026-04-05 — Artifact lineage map batch

- **Added**: `scripts/generate_artifact_lineage.py` — conservative lineage generator that inspects JACK artifacts and repository signals to produce `jack/artifact-lineage.json` and `jack/artifact-lineage.md`. The generator emits upstream/downstream relationships, invalidation rules, missing dependencies, blocked artifacts, review-sensitive classifications, and a conservative recompute order. All outputs are recommendation-only (`do_not_auto_execute: true`).
- **Added**: `scripts/run_lineage_checks.py` — verification runner that creates fixtures for a healthy dependency graph, a missing-upstream scenario that causes blocked downstream artifacts, and an invalidation-rule scenario that asserts invalidation rules for core upstream artifacts (for example `jack/context-pack.json`). The runner asserts the lineage JSON/MD are written and that blocked/missing dependencies and invalidation rules are reported.
- **Behavior**: The lineage generator captures conservative relationships such as:
	- evidence -> `jack/evidence-index.json`
	- evidence/index -> `jack/context-pack.json`
	- context-pack -> `jack/bundle-manifest.json` -> `jack/adoption-report.json` -> `jack/proposed-patchset.json`
	- `jack/freshness-report.json` -> `jack/refresh-plan.json` -> `jack/maintenance-runbook.json`
	- `jack/status.json`, `jack/adoption-readiness.json`, and `jack/adoption-checklist.json` depend on several upstream artifacts and are recompute-sensitive

- **Invalidation rules**: For each artifact the generator lists downstream artifacts that may become invalid when the upstream artifact changes (for example, changes to `jack/context-pack.json` recommend regenerating the bundle, adoption review, and patchset artifacts). Rules are human-readable and conservative.
- **Verified**: `scripts/run_lineage_checks.py` was executed and passed in all fixture scenarios: "Lineage checks OK". `python3 scripts/validate_repo.py` was run and passed: "JACK repository validation passed.".
- **Notes / Rationale**: This batch is the right next step because it makes the dependency graph explicit for human reviewers and operators — showing what becomes stale after upstream updates and what should be recomputed first. It enables lineage-aware human decisions for refresh and adoption without adding any automation.

## 2026-04-07 — Inspector-symbol planner boost

- **Changed**: `scripts/repo_task_plan.py::rank_files` — added a conservative boost for files containing exact symbols reported in `jack/repo-task-inspect.json` (`key_symbols_or_sections`). This helps the planner prefer the exact script and symbol that the inspector/edit-sketch target (for example, a file containing `def load_json`).
- **Rationale**: reduces planner/inspector mismatches where filename-only heuristics favored manifests or workflows while the inspector/edit-sketch targeted a script symbol.
- **Test**: Added `scripts/test_repo_task_plan_inspect_boost.py` — a narrow regression test asserting that a file containing the inspector symbol ranks above a file that does not contain it.
- **Validation**: Ran the integrated JACK flow once to confirm artifacts were written and planner output aligned more closely with inspector/edit-sketch recommendations.
- **Do not auto-apply**: recommendation-only changes; `do_not_auto_apply: true`.

## 2026-04-05 — Lineage-aware invalidation summary batch

- **Added**: `scripts/generate_invalidation_summary.py` — generator that consumes `jack/artifact-lineage.json` and emits `jack/invalidation-summary.json` and `jack/invalidation-summary.md`. The summary explains, for a given changed artifact, the direct and transitive downstream impacts, separates direct vs transitive impacts, synthesizes review-sensitive impacts, reports uncertain/blocked impacts where upstream dependencies are missing, and recommends a conservative recompute and review order. Outputs are recommendation-only and include `do_not_auto_execute: true`.
- **Added**: `scripts/run_invalidation_summary_checks.py` — verification runner that invokes the generator against the fixture lineage and asserts the expected top-level keys and outputs are written.
- **Generated (fixture)**: `jack/invalidation-summary.json`, `jack/invalidation-summary.md` (recommendation-only human-readable summary and machine-ready JSON).
- **Verified**: `run_invalidation_summary_checks.py` ran successfully: "Invalidation summary checks OK".
- **Verified**: `python3 scripts/validate_repo.py` ran successfully: "JACK repository validation passed.".

Notes: This generator is conservative and recommendation-only. It requires an up-to-date `jack/artifact-lineage.json` to produce accurate impacts; when upstream lineage or dependencies are missing the generator reports uncertainty and marks impacted artifacts as blocked or needing manual review. No automatic recompute or patching is performed.

## 2026-04-05 — Artifact family change impact batch

- **Added**: `scripts/generate_family_change_impact.py` — conservative family-level impact generator that consumes `jack/artifact-lineage.json` and a `--changed-family` input and emits `jack/family-change-impact.json` and `jack/family-change-impact.md`. The generator expands explicit family definitions to concrete artifact candidates, prefers lineage-reported artifacts when available, separates direct vs transitive artifact impacts, synthesizes review-sensitive impacts, reports uncertainty and blocked impacts when family members or upstream dependencies are absent, and recommends a conservative recompute and review order. All outputs are recommendation-only and include `do_not_auto_execute: true`.
- **Added**: `scripts/run_family_impact_checks.py` — verification runner that creates small temporary lineage fixtures for the following scenarios: evidence-family impact, adoption-family impact, freshness-family impact, and an uncertain/missing-family-members case. The runner invokes the generator using the current Python interpreter (`sys.executable`) to ensure portability, verifies the expected top-level keys and scenario-specific expectations (for example, review-sensitive synthesis in the evidence scenario), and finally runs a repo-local invocation against `jack/artifact-lineage.json` (if present) to produce `jack/family-change-impact.json`/`.md` in the working repository.
- **Generated (fixture & repo-local)**: `jack/family-change-impact.json`, `jack/family-change-impact.md` (recommendation-only JSON + human-readable MD; the runner writes temporary artifacts for fixture verification and writes a repo-local artifact if a repo lineage exists).
- **Verified**: `run_family_impact_checks.py` ran successfully: "Family impact checks OK".
- **Verified**: `python3 scripts/validate_repo.py` ran successfully: "JACK repository validation passed.".

Notes: This batch is the right next step because it elevates the single-artifact invalidation view into a family-level summary that operators can use to prioritize work when a whole class of inputs (for example `evidence`) change. The implementation is explicitly conservative: it only considers artifacts mapped to pre-defined families, prefers lineage-reported artifacts over guesses, and reports uncertainty when family members or upstream inputs are missing. No automatic recompute, application of patches, or mutation of instruction files is performed by this batch.

## 2026-04-05 — Lineage-backed recompute explainer batch

- **Added**: `scripts/generate_recompute_explainer.py` — recompute explainer generator that consumes `jack/artifact-lineage.json` (and optionally `jack/invalidation-summary.json` or `jack/family-change-impact.json` when present), accepts a `--changed-artifact` or `--changed-family` trigger, and emits `jack/recompute-explainer.json` and `jack/recompute-explainer.md`. The explainer justifies JACK's recommended recompute order using explicit dependency chains drawn from the lineage map, synthesizes review checkpoints, identifies blocked and uncertain steps, and explains why each recompute step is recommended. All outputs are recommendation-only and include `do_not_auto_execute: true`.
- **Added**: `scripts/run_recompute_explainer_checks.py` — verification runner that creates temporary lineage fixtures for three scenarios (single-artifact trigger, family trigger, blocked/uncertain trigger), invokes the generator using the current Python interpreter (`sys.executable`) for portability, validates required JSON keys, asserts presence of dependency-chain explanations and review-checkpoint synthesis, and writes a repo-local `jack/recompute-explainer.json`/`.md` if a repo lineage exists.
- **Generated (fixture & repo-local)**: `jack/recompute-explainer.json`, `jack/recompute-explainer.md` (recommendation-only JSON and human-readable MD). The runner writes temporary artifacts for fixture verification and writes repo-local artifacts when `jack/artifact-lineage.json` is present.
- **Verified**: `run_recompute_explainer_checks.py` ran successfully: "Recompute explainer checks OK".
- **Verified**: `python3 scripts/validate_repo.py` ran successfully: "JACK repository validation passed.".

Notes: This batch is the right follow-up because operators not only need to know which artifacts are stale but also why JACK recommends the recompute order. The explainer ties recompute steps to explicit lineage paths (when available), surfaces review checkpoints (proposed instructions, adoption report, proposed patchset, readiness, checklist, runbook), and lists blocked/uncertain steps that require prerequisite resolution. The generator is conservative: it prefers lineage and explicit family definitions, does not invent new artifacts or dependency edges, and reports uncertainty rather than guessing when inputs are missing.

## 2026-04-05 — Repo profile → Docs lookup bridge batch

- **Added**: `scripts/profile_to_docs_lookup.py` — conservative bridge that consumes `jack/repo-stack-profile.json` and invokes the existing `scripts/docs_lookup.py` for a small set of high-value, repo-specific queries. Prefers official docs and records ambiguity; does not perform network-based expansion beyond selected sources.
- **Generated (smoke)**: `jack/repo-docs-lookup-plan.json`, `jack/repo-docs-lookup-plan.md`, `jack/repo-docs-evidence.jsonl` (appended evidence from docs lookup).
- **Executed (smoke)**: Per process rules, ran a single focused invocation against the current repo root to produce the plan and at least one evidence output; the bridge wrote the plan and evidence files. No fixture runner or repo-wide validation was added or executed.
- **Notes**: Outputs are recommendation-only and include `do_not_auto_execute: true`. The bridge invokes `scripts/docs_lookup.py` using the active Python interpreter (`sys.executable`) to ensure portability. When the repo profile is ambiguous the bridge selects fewer queries (or none) and records explicit ambiguity notes rather than guessing a stack.


## 2026-04-06 — Repo profiling batch

- **Added**: `scripts/profile_repo_stack.py` — conservative repo profiling generator that detects languages, frameworks, package managers, build/runtime targets, and recommends official docs and starter queries. Detection is manifest- and evidence-file-driven; no network lookups.
- **Generated (smoke)**: `jack/repo-stack-profile.json`, `jack/repo-stack-profile.md`, `jack/repo-research-brief.md` (proposal-only, recommendation artifacts).
- **Verified (smoke)**: Ran a single focused smoke invocation to produce the artifacts; normalized line endings and re-ran `scripts/validate_repo.py` — repository validation passed.
- **Notes**: Outputs are explicitly recommendation-only and include `do_not_auto_execute: true`. Following the repository policy: a single smoke check was performed; no automatic changes to instructions or patchsets were applied.

## 2026-04-06 — Source-signal profiling hardening batch

- **Updated**: `scripts/profile_repo_stack.py` — added bounded source-signal scanning across a small set of high-value file extensions (`*.py, *.ts, *.tsx, *.js, *.jsx`), explicit import/use pattern detection (FastAPI, Django, Flask, React, Next.js), and conservative integration of source hints with manifest/config signals.
- **Behavior**: manifest/config detection remains the primary signal; repeated, consistent source hints (seen in >=2 files) may seed framework inference when manifests are absent; conflicting signals reduce confidence rather than override manifests.
- **Executed (smoke)**: ran `python -u scripts/profile_repo_stack.py --repo-root .` and wrote `jack/repo-stack-profile.json` (includes `confidence_notes` and generated timestamp). Outputs remain recommendation-only.
- **Notes**: No fixture runners or repo-wide validators were added or executed.

## 2026-04-06 — Docs-selection hardening batch

- **Updated**: `scripts/profile_to_docs_lookup.py` — tightened selection to consume the strengthened profile directly, prefer official docs for the strongest detected frameworks/languages, and cap queries conservatively by profile `confidence_level`.
- **Behavior**: selects at most 2 queries by default (3 only for high-confidence profiles), records per-query rationales (signals, target stack, why), reduces query breadth when confidence is low, and records explicit ambiguity notes instead of speculative lookups.
- **Evidence handling**: deduplicates appended JSONL evidence, limits appended snippets per query, and removes temporary per-query fallback files to avoid spraying many artifacts under `jack/`.
- **Executed (smoke)**: ran `python -u scripts/profile_to_docs_lookup.py --repo-root .` and wrote `jack/repo-docs-lookup-plan.json` and appended deduplicated `jack/repo-docs-evidence.jsonl` (plan includes selected queries, selected_sources, and `query_rationales`).
- **Notes**: No new verification runners or fixture-based checks were added. Outputs remain recommendation-only.

