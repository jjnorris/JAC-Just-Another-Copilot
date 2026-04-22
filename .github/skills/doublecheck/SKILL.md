---
name: doublecheck
description: Re-run truth, correctness, reuse, and reporting checks before any strong claim.
---

# doublecheck

## Purpose
Re-run truth, correctness, reuse, and reporting checks before any strong claim.

## When to use
- before completion
- after non-trivial implementation
- after risky research conclusions

## Inputs
- correctness contract
- current diff or artifact set
- verification evidence
- report draft

## Outputs
- claim-status summary
- coverage miss note
- reduced overclaim risk

## What it checks
- Do not upgrade a claim without evidence.
- Flag wiring uncertainty explicitly.
- Prefer narrowing the claim over smoothing the language.

## Warnings
- Passing tests may still miss real wiring.
- Narrative confidence can hide missing proof.

## Blocks on
- Explicit wiring claim is contradicted.
- Critical claim has no evidence at all.

## Evidence expected or emitted
- coverage_miss
- wiring_claim_orphan
- usage_recorded

## Examples
- Check whether the package registry actually references newly added workflow docs.

## Limitations
- Falls back to: Manual verification checklist using `workflows/verify-before-claim.md`.

## Boundary
- May advise, warn, or narrow claims. It may not fabricate evidence or self-approve blocked work.

## Evidence trust order
When classifying or asserting verification, prefer higher-trust evidence first. Use this explicit hierarchy when mapping claims to proof:

1. Verified runtime behavior observed in this repository (test outputs, run logs, CI artifacts).
2. Parsing / schema / static checks of repository artifacts (JSON/YAML/manifest parsing that succeeds).
3. Directly executed scripts or commands run in-repo with recorded output (when available and repeatable).
4. Explicit repository artifacts authored by humans (README, docs, manifest files) that state behavior.
5. Trusted external documentation (official libraries, vendor docs) cited with links.
6. Heuristic or model inferences derived from the above (lowest trust).

Follow this order when mapping evidence to `must`/`must_not` statements: prefer moving a claim up the hierarchy by collecting a higher-trust item rather than relying on inference.

## Never claim without evidence (hard rule)
- Do not assert a task is "done", "validated", or "fixed" unless direct evidence from the trust order above supports the claim.
- Never fabricate or invent execution results, test outputs, or traces to satisfy a completion claim.
- If required evidence is missing, narrow the claim (e.g., "behaves for the tested path") or emit an explicit `coverage_miss` and leave the task open.

## Fact / Inference / Unknown / Assumption split
When reporting, always categorize statements using these explicit buckets:

- `verified_facts`: Observable outputs or artifacts that were produced and recorded (file paths, test lines, logs, JSON entries).
- `inferences`: Model or heuristic-based conclusions derived from facts but not directly observed (flag clearly as inference).
- `unknowns`: Concrete questions or data points that remain unobserved and materially affect correctness.
- `assumptions`: Explicit operational assumptions made to proceed (environment, profile presence, external service availability).

Record at least one example item under each bucket in any final validation report; do not omit buckets even if empty.

## Mandatory validation reporting (template)
Before any strong completion claim, produce a short, machine-parseable validation report including these fields:

```
validation_report:
	validated:           # list of claim ids or descriptions that were validated
		- "parse:jack/repo-task-plan.json"
	methods:             # how each validated claim was checked (command, test, file parse)
		- "ran: python -u scripts/run_repo_task_flow.py --task 'X'"
	not_validated:        # claims intentionally left unproven
		- "end-to-end CI integration"
	evidence_links:       # file paths or URLs to captured proof artifacts
		- "jack/repo-task-plan.json"
	assumptions:          # explicit assumptions used during validation
		- "profile indicates python_tooling_repo"
	verifier_version:     # skill or tool version used for verification
		- "doublecheck v1"
```

Attach or write this `validation_report` into the repository's JACK artifacts (e.g., `jack/` JSON) or emit it via trace events so downstream reviewers can evaluate claims without re-running everything.

## Anti-theater checklist
Before closing a task, run this checklist and surface any non-empty items in the validation report:

- [ ] Are the verified facts directly tied to the claim (wiring)?
- [ ] Are there any uncovered wiring claims (coverage_miss)?
- [ ] Did we rely on a single, fragile evidence item without corroboration?
- [ ] Are any runtime outputs presented without saved logs or file references?
- [ ] Was the same fix attempted more than twice without new verified facts?

If any box is checked, refuse strong completion or narrow the claim and record the reason.

## Reorient trigger
If a change attempt or investigation loop repeats without producing a new `verified_facts` item, trigger a structured reorient:

- Threshold: more than 2 failed attempts on the same narrow change path (or 2 automated retries) without new verified facts.
- Action: emit a `failure_triage` record and pause autonomous retries. The triage record must include
	- `verified_facts` (what is confirmed),
	- `unverified_guesses`,
	- `reproduction_path` (the narrowest command to reproduce),
	- `next_step` (one explicit action).

This prevents thrashing and enforces human review when local fixes stall.

## Completion gate (stronger)
A task may be reported as completed only when all of these conditions hold:

1. A `validation_report` is present and attached to JACK artifacts.
2. `verified_facts` map to every `must` in the correctness contract (or explicitly list gaps under `not_validated`).
3. `doublecheck` and `verifier-bridge` steps have been invoked and emitted coverage/trace records.
4. Anti-theater checklist has no blocking items, or all blocks are explicitly acknowledged and accepted by a human reviewer.

Meeting the gate is a precondition for high-confidence claims; if any part fails, the agent must narrow the claim and emit the corresponding `coverage_miss` and `assumption` records.

## Related docs
- `docs/jack/rules/10-correctness-contracts.md`
- `docs/jack/workflows/verify-before-claim.md`

