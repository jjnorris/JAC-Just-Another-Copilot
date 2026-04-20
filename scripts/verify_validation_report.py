#!/usr/bin/env python3
"""Narrow verifier: ensure run_repo_task_flow produced a validation report.

Exit codes:
 0: OK
 1: missing or incomplete
"""
from pathlib import Path
import json
import os
from typing import Any, cast


PROFILE_REPO_STACK_STAGE = "profile_repo_stack.py"
PROFILE_TO_DOCS_LOOKUP_STAGE = "profile_to_docs_lookup.py"
REPO_TASK_RESEARCH_STAGE = "repo_task_research.py"
REPO_TASK_PLAN_STAGE = "repo_task_plan.py"
REPO_TASK_INSPECT_STAGE = "repo_task_inspect.py"
REPO_TASK_EDIT_SKETCH_STAGE = "repo_task_edit_sketch.py"
REPO_TASK_CHANGE_OUTLINE_STAGE = "repo_task_change_outline.py"
REPO_TASK_PATCH_SKETCH_STAGE = "repo_task_patch_sketch.py"

ARTIFACT_FAMILY_MANIFEST_PATH = Path("jack/repo-task-artifact-family-manifest.json")
TRANSITION_LEDGER_REL_PATH = "jack/repo-task-transition-ledger.json"
VALIDATION_REPORT_REL_PATH = "jack/repo-task-validation-report.json"

REPO_STACK_PROFILE_JSON = "jack/repo-stack-profile.json"
REPO_DOCS_LOOKUP_PLAN_JSON = "jack/repo-docs-lookup-plan.json"
REPO_DOCS_EVIDENCE_JSONL = "jack/repo-docs-evidence.jsonl"
REPO_TASK_BRIEF_JSON = "jack/repo-task-brief.json"
REPO_TASK_PLAN_JSON = "jack/repo-task-plan.json"
REPO_TASK_INSPECT_JSON = "jack/repo-task-inspect.json"
REPO_TASK_EDIT_SKETCH_JSON = "jack/repo-task-edit-sketch.json"
REPO_TASK_CHANGE_OUTLINE_JSON = "jack/repo-task-change-outline.json"


MINIMAL_ARTIFACT_REQUIREMENTS = {
    "repo-task-plan.json": ("recommended_first_edit_area",),
    "repo-task-inspect.json": ("recommended_first_code_edit_area",),
    "repo-task-edit-sketch.json": ("target_file",),
    "repo-task-change-outline.json": ("target_file",),
}

REQUIRED_EVIDENCE_LINKS = set(MINIMAL_ARTIFACT_REQUIREMENTS)

TRANSITION_REQUIRED_STAGE_SEQUENCE = (
    PROFILE_REPO_STACK_STAGE,
    PROFILE_TO_DOCS_LOOKUP_STAGE,
    REPO_TASK_RESEARCH_STAGE,
    REPO_TASK_PLAN_STAGE,
    REPO_TASK_INSPECT_STAGE,
    REPO_TASK_EDIT_SKETCH_STAGE,
    REPO_TASK_CHANGE_OUTLINE_STAGE,
)

TRANSITION_REQUIRED_ARTIFACTS = (
    REPO_STACK_PROFILE_JSON,
    REPO_DOCS_LOOKUP_PLAN_JSON,
    REPO_TASK_BRIEF_JSON,
    REPO_TASK_PLAN_JSON,
    REPO_TASK_INSPECT_JSON,
    REPO_TASK_EDIT_SKETCH_JSON,
    REPO_TASK_CHANGE_OUTLINE_JSON,
)

TRANSITION_OPTIONAL_STAGE = REPO_TASK_PATCH_SKETCH_STAGE

POST_VALIDATION_STAGE = "post_validation"


REQUIRED_VALIDATED_STAGES: set[str] = set(TRANSITION_REQUIRED_STAGE_SEQUENCE)

KNOWN_VALIDATED_STAGES: set[str] = REQUIRED_VALIDATED_STAGES | {TRANSITION_OPTIONAL_STAGE}

TRANSITION_LEDGER_PATH = Path("jack/repo-task-transition-ledger.json")
TRANSITION_LEDGER_ARTIFACTS: dict[str, str] = dict(zip(TRANSITION_REQUIRED_STAGE_SEQUENCE, TRANSITION_REQUIRED_ARTIFACTS))

REQUIRED_ARTIFACT_FAMILY_PATHS = {
    REPO_STACK_PROFILE_JSON,
    REPO_DOCS_LOOKUP_PLAN_JSON,
    REPO_DOCS_EVIDENCE_JSONL,
    REPO_TASK_BRIEF_JSON,
    REPO_TASK_PLAN_JSON,
    REPO_TASK_INSPECT_JSON,
    REPO_TASK_EDIT_SKETCH_JSON,
    REPO_TASK_CHANGE_OUTLINE_JSON,
}

REQUIRED_ARTIFACT_FAMILY_STAGE_PATHS = {
    PROFILE_REPO_STACK_STAGE: REPO_STACK_PROFILE_JSON,
    PROFILE_TO_DOCS_LOOKUP_STAGE: REPO_DOCS_LOOKUP_PLAN_JSON,
    REPO_TASK_RESEARCH_STAGE: REPO_TASK_BRIEF_JSON,
    REPO_TASK_PLAN_STAGE: REPO_TASK_PLAN_JSON,
    REPO_TASK_INSPECT_STAGE: REPO_TASK_INSPECT_JSON,
    REPO_TASK_EDIT_SKETCH_STAGE: REPO_TASK_EDIT_SKETCH_JSON,
    REPO_TASK_CHANGE_OUTLINE_STAGE: REPO_TASK_CHANGE_OUTLINE_JSON,
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def should_validate_transition_ledger() -> bool:
    return os.environ.get("JACK_REQUIRE_TRANSITION_LEDGER") == "1"


def should_validate_artifact_family_manifest() -> bool:
    return os.environ.get("JACK_REQUIRE_ARTIFACT_FAMILY_MANIFEST") == "1"


def should_validate_adversarial_review() -> bool:
    return os.environ.get("JACK_REQUIRE_ADVERSARIAL_REVIEW") == "1"


def should_validate_freshness_evidence() -> bool:
    return os.environ.get("JACK_REQUIRE_FRESHNESS_EVIDENCE") == "1"


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def require_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        data = load_json(path)
    except Exception as exc:
        print(f"INVALID {label} JSON:", exc)
        raise SystemExit(1)

    if not isinstance(data, dict):
        print(f"INVALID {label}: expected a JSON object")
        raise SystemExit(1)

    return data


def validate_required_stage_record(stage_record: dict[str, Any], expected_name: str) -> None:
    if stage_record.get("stage_name") != expected_name:
        print("INVALID TRANSITION LEDGER: stage order mismatch")
        raise SystemExit(1)
    if stage_record.get("status") != "completed":
        print("INVALID TRANSITION LEDGER: required stages must be completed")
        raise SystemExit(1)

    artifact_paths = stage_record.get("artifact_paths")
    if not isinstance(artifact_paths, list):
        print("INVALID TRANSITION LEDGER: artifact_paths must be a list")
        raise SystemExit(1)
    artifact_paths = cast(list[object], artifact_paths)
    if len(artifact_paths) != 1:
        print("INVALID TRANSITION LEDGER: required stages must name exactly one primary artifact path")
        raise SystemExit(1)

    expected_artifact = TRANSITION_LEDGER_ARTIFACTS.get(expected_name)
    if expected_artifact is None:
        print(f"INVALID TRANSITION LEDGER: no artifact mapping for {expected_name}")
        raise SystemExit(1)
    if str(artifact_paths[0]) != expected_artifact:
        print("INVALID TRANSITION LEDGER: artifact path mismatch")
        raise SystemExit(1)
    if not Path(expected_artifact).is_file():
        print(f"INVALID TRANSITION LEDGER: missing artifact path {expected_artifact}")
        raise SystemExit(1)

    if not is_non_empty_string(stage_record.get("reason")):
        print("INVALID TRANSITION LEDGER: reason must be a string")
        raise SystemExit(1)


def expected_transition_stage_names(validated_stages: list[object], optional_stage_present: bool) -> list[str]:
    expected_stage_names = [str(stage) for stage in validated_stages]
    if not optional_stage_present:
        expected_stage_names.append(TRANSITION_OPTIONAL_STAGE)
    return expected_stage_names


def validate_optional_stage_record(stage_record: dict[str, Any], optional_stage_present: bool) -> None:
    if stage_record.get("stage_name") != TRANSITION_OPTIONAL_STAGE:
        print("INVALID TRANSITION LEDGER: optional stage record missing")
        raise SystemExit(1)

    status = stage_record.get("status")
    artifact_paths = stage_record.get("artifact_paths")
    if not isinstance(artifact_paths, list):
        print("INVALID TRANSITION LEDGER: artifact_paths must be a list")
        raise SystemExit(1)
    artifact_paths = cast(list[object], artifact_paths)
    if not is_non_empty_string(stage_record.get("reason")):
        print("INVALID TRANSITION LEDGER: reason must be a string")
        raise SystemExit(1)

    if optional_stage_present:
        if status != "completed":
            print("INVALID TRANSITION LEDGER: optional stage handling mismatch")
            raise SystemExit(1)
    else:
        if status != "skipped":
            print("INVALID TRANSITION LEDGER: optional stage should be skipped when the script is absent")
            raise SystemExit(1)
    if artifact_paths:
        print("INVALID TRANSITION LEDGER: optional stage should not name artifact paths")
        raise SystemExit(1)


def validate_transition_ledger_header(ledger: dict[str, Any], report_task: Any) -> None:
    required_fields = ["task", "started_at", "finished_at", "stages", "optional_stages_encountered", "final_status"]
    missing_fields = [field for field in required_fields if field not in ledger]
    if missing_fields:
        print("INVALID TRANSITION LEDGER: missing keys:", missing_fields)
        raise SystemExit(1)

    if ledger.get("task") != report_task:
        print("INVALID TRANSITION LEDGER: task mismatch")
        raise SystemExit(1)

    if not is_non_empty_string(ledger.get("started_at")):
        print("INVALID TRANSITION LEDGER: started_at must be a non-empty string")
        raise SystemExit(1)
    if not is_non_empty_string(ledger.get("finished_at")):
        print("INVALID TRANSITION LEDGER: finished_at must be a non-empty string")
        raise SystemExit(1)


def validate_transition_ledger_stage_records(
    stages: list[object],
    validated_stages: list[object],
    optional_stage_present: bool,
) -> None:
    expected_stage_names = expected_transition_stage_names(validated_stages, optional_stage_present)
    if len(stages) != len(expected_stage_names):
        print("INVALID TRANSITION LEDGER: stage count mismatch")
        raise SystemExit(1)

    for index, expected_name in enumerate(expected_stage_names):
        stage_record = stages[index]
        if not isinstance(stage_record, dict):
            print(f"INVALID TRANSITION LEDGER: stage {index} is not an object")
            raise SystemExit(1)

        stage_record_dict = cast(dict[str, Any], stage_record)

        if expected_name == TRANSITION_OPTIONAL_STAGE:
            validate_optional_stage_record(stage_record_dict, optional_stage_present)
            continue

        validate_required_stage_record(stage_record_dict, expected_name)


def validate_transition_ledger_optional_stage_list(encountered: object, optional_stage_present: bool) -> None:
    if not isinstance(encountered, list):
        print("INVALID TRANSITION LEDGER: optional_stages_encountered must be a list")
        raise SystemExit(1)

    encountered_values = [str(item) for item in cast(list[object], encountered)]
    if optional_stage_present:
        if encountered_values != [TRANSITION_OPTIONAL_STAGE]:
            print("INVALID TRANSITION LEDGER: optional stage encounter list mismatch")
            raise SystemExit(1)
    elif encountered_values:
        print("INVALID TRANSITION LEDGER: skipped optional stage must not be listed as encountered")
        raise SystemExit(1)


def validate_ledger_status(ledger: dict[str, Any], stages: list[dict[str, Any]]) -> None:
    final_status = ledger.get("final_status")
    if final_status not in {"completed", "failed"}:
        print("INVALID TRANSITION LEDGER: invalid final_status")
        raise SystemExit(1)

    has_failed_stage = any(stage.get("status") == "failed" for stage in stages)
    if final_status == "failed" and not has_failed_stage:
        print("INVALID TRANSITION LEDGER: final_status failed without a failed stage record")
        raise SystemExit(1)
    if final_status == "completed" and has_failed_stage:
        print("INVALID TRANSITION LEDGER: final_status completed despite a failed stage record")
        raise SystemExit(1)


def validate_transition_ledger(report_task: Any, validated_stages: list[object]) -> None:
    if not should_validate_transition_ledger():
        return

    if not TRANSITION_LEDGER_PATH.exists():
        print("MISSING TRANSITION LEDGER: jack/repo-task-transition-ledger.json")
        raise SystemExit(1)

    ledger = require_json_object(TRANSITION_LEDGER_PATH, "TRANSITION LEDGER")
    validate_transition_ledger_header(ledger, report_task)

    stages = ledger.get("stages")
    if not isinstance(stages, list) or not stages:
        print("INVALID TRANSITION LEDGER: stages must be a non-empty list")
        raise SystemExit(1)

    optional_stage_present = Path("scripts/repo_task_patch_sketch.py").is_file()
    stage_records = cast(list[object], stages)
    validate_transition_ledger_stage_records(stage_records, validated_stages, optional_stage_present)
    validate_transition_ledger_optional_stage_list(
        ledger.get("optional_stages_encountered"),
        optional_stage_present,
    )

    validate_ledger_status(ledger, cast(list[dict[str, Any]], stage_records))


def expected_output_type(artifact_path: str) -> str:
    if artifact_path.endswith(".jsonl"):
        return "jsonl"
    if artifact_path.endswith(".json"):
        return "json"
    return "md"


def validate_artifact_family_entry(entry: dict[str, Any], validated_stage_names: set[str]) -> None:
    required_fields = [
        "stage_name",
        "artifact_role",
        "artifact_path",
        "required_or_optional",
        "producer",
        "consumers",
        "output_type",
        "expected_in_current_live_flow",
    ]
    missing_fields = [field for field in required_fields if field not in entry]
    if missing_fields:
        print("INVALID ARTIFACT FAMILY MANIFEST: missing keys:", missing_fields)
        raise SystemExit(1)

    stage_name = entry.get("stage_name")
    if not isinstance(stage_name, str):
        print("INVALID ARTIFACT FAMILY MANIFEST: unknown stage_name", stage_name)
        raise SystemExit(1)
    # Allow a post-validation artifact entry that is not produced by a validated stage.
    if stage_name not in validated_stage_names and stage_name != POST_VALIDATION_STAGE:
        print("INVALID ARTIFACT FAMILY MANIFEST: unknown stage_name", stage_name)
        raise SystemExit(1)

    artifact_role = entry.get("artifact_role")
    if not is_non_empty_string(artifact_role):
        print("INVALID ARTIFACT FAMILY MANIFEST: artifact_role must be a string")
        raise SystemExit(1)

    artifact_path = entry.get("artifact_path")
    if not is_non_empty_string(artifact_path):
        print("INVALID ARTIFACT FAMILY MANIFEST: artifact_path must be a string")
        raise SystemExit(1)
    artifact_path_text = str(artifact_path)
    if not Path(artifact_path_text).is_file():
        print(f"INVALID ARTIFACT FAMILY MANIFEST: missing artifact path {artifact_path_text}")
        raise SystemExit(1)

    required_or_optional = entry.get("required_or_optional")
    if required_or_optional not in {"required", "optional"}:
        print("INVALID ARTIFACT FAMILY MANIFEST: invalid required_or_optional")
        raise SystemExit(1)

    producer = entry.get("producer")
    if stage_name != POST_VALIDATION_STAGE:
        if producer != f"scripts/{stage_name}":
            print("INVALID ARTIFACT FAMILY MANIFEST: producer mismatch")
            raise SystemExit(1)
    else:
        # For post-validation artifacts accept runner-produced or human-reviewed producers.
        if not (isinstance(producer, str) and (producer.startswith("scripts/") or producer == "human review")):
            print("INVALID ARTIFACT FAMILY MANIFEST: producer mismatch for post-validation artifact")
            raise SystemExit(1)

    consumers = entry.get("consumers")
    if not isinstance(consumers, list) or not consumers:
        print("INVALID ARTIFACT FAMILY MANIFEST: consumers must be a non-empty list")
        raise SystemExit(1)
    if not all(isinstance(consumer, str) and consumer.strip() for consumer in consumers):
        print("INVALID ARTIFACT FAMILY MANIFEST: consumers must be strings")
        raise SystemExit(1)

    output_type = entry.get("output_type")
    if output_type != expected_output_type(artifact_path_text):
        print("INVALID ARTIFACT FAMILY MANIFEST: output_type mismatch")
        raise SystemExit(1)

    if entry.get("expected_in_current_live_flow") is not True:
        print("INVALID ARTIFACT FAMILY MANIFEST: expected_in_current_live_flow must be true")
        raise SystemExit(1)


def validate_artifact_family_top_level(manifest: dict[str, Any], report_task: Any) -> None:
    required_top_level_fields = [
        "task",
        "generated_at",
        "transition_ledger_ref",
        "validation_report_ref",
        "artifact_family_entries",
    ]
    missing_top_level_fields = [field for field in required_top_level_fields if field not in manifest]
    if missing_top_level_fields:
        print("INVALID ARTIFACT FAMILY MANIFEST: missing keys:", missing_top_level_fields)
        raise SystemExit(1)

    if manifest.get("task") != report_task:
        print("INVALID ARTIFACT FAMILY MANIFEST: task mismatch")
        raise SystemExit(1)

    if not is_non_empty_string(manifest.get("generated_at")):
        print("INVALID ARTIFACT FAMILY MANIFEST: generated_at must be a string")
        raise SystemExit(1)

    if manifest.get("transition_ledger_ref") != TRANSITION_LEDGER_REL_PATH:
        print("INVALID ARTIFACT FAMILY MANIFEST: transition_ledger_ref mismatch")
        raise SystemExit(1)

    if manifest.get("validation_report_ref") != VALIDATION_REPORT_REL_PATH:
        print("INVALID ARTIFACT FAMILY MANIFEST: validation_report_ref mismatch")
        raise SystemExit(1)


def collect_artifact_family_entries(
    entries: list[object],
    validated_stage_names: set[str],
) -> tuple[set[str], dict[str, dict[str, Any]]]:
    required_paths_in_manifest: set[str] = set()
    manifest_entries_by_path: dict[str, dict[str, Any]] = {}

    for entry in entries:
        if not isinstance(entry, dict):
            print("INVALID ARTIFACT FAMILY MANIFEST: entry is not an object")
            raise SystemExit(1)

        entry_dict = cast(dict[str, Any], entry)
        validate_artifact_family_entry(entry_dict, validated_stage_names)

        artifact_path = str(entry_dict["artifact_path"])
        manifest_entries_by_path[artifact_path] = entry_dict
        if entry_dict["required_or_optional"] == "required":
            required_paths_in_manifest.add(artifact_path)

    return required_paths_in_manifest, manifest_entries_by_path


def validate_artifact_family_required_paths(required_paths_in_manifest: set[str]) -> None:
    if required_paths_in_manifest != REQUIRED_ARTIFACT_FAMILY_PATHS:
        print("INVALID ARTIFACT FAMILY MANIFEST: required artifact path set mismatch")
        print(" - expected:")
        for path in sorted(REQUIRED_ARTIFACT_FAMILY_PATHS):
            print(f"   - {path}")
        print(" - actual:")
        for path in sorted(required_paths_in_manifest):
            print(f"   - {path}")
        raise SystemExit(1)


def validate_artifact_family_evidence_coverage(evidence_names: set[str]) -> None:
    if not evidence_names <= REQUIRED_ARTIFACT_FAMILY_PATHS:
        print("INVALID ARTIFACT FAMILY MANIFEST: validation report evidence not covered by required artifacts")
        raise SystemExit(1)


def validate_artifact_family_ledger_alignment(manifest_entries_by_path: dict[str, dict[str, Any]]) -> None:
    ledger = require_json_object(TRANSITION_LEDGER_PATH, "TRANSITION LEDGER")
    ledger_stage_records = ledger.get("stages")
    if not isinstance(ledger_stage_records, list):
        print("INVALID ARTIFACT FAMILY MANIFEST: transition ledger stages must be a list")
        raise SystemExit(1)

    for stage_record in cast(list[object], ledger_stage_records):
        if not isinstance(stage_record, dict):
            print("INVALID ARTIFACT FAMILY MANIFEST: transition ledger stage record is not an object")
            raise SystemExit(1)

        stage_record_dict = cast(dict[str, Any], stage_record)
        stage_name = stage_record_dict.get("stage_name")
        if stage_name == TRANSITION_OPTIONAL_STAGE:
            continue

        expected_path = REQUIRED_ARTIFACT_FAMILY_STAGE_PATHS.get(str(stage_name))
        if expected_path is None:
            print(f"INVALID ARTIFACT FAMILY MANIFEST: no manifest path for stage {stage_name}")
            raise SystemExit(1)

        entry = manifest_entries_by_path.get(expected_path)
        if entry is None:
            print(f"INVALID ARTIFACT FAMILY MANIFEST: missing manifest entry for {expected_path}")
            raise SystemExit(1)
        if entry.get("stage_name") != stage_name:
            print("INVALID ARTIFACT FAMILY MANIFEST: stage_name mismatch")
            raise SystemExit(1)
        if entry.get("required_or_optional") != "required":
            print("INVALID ARTIFACT FAMILY MANIFEST: ledger artifact must be required")
            raise SystemExit(1)


def validate_adversarial_review(
    manifest: dict[str, Any],
    report_task: Any,
    manifest_entries_by_path: dict[str, dict[str, Any]],
) -> None:
    if not should_validate_adversarial_review():
        return

    # Locate the adversarial review entry by role or by known filename
    adv_entry: dict[str, Any] | None = None
    for path, entry in manifest_entries_by_path.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("artifact_role") == "adversarial_review" or Path(path).name == "repo-task-adversarial-review.json":
            adv_entry = entry
            break

    if adv_entry is None:
        print("MISSING ADVERSARIAL REVIEW: manifest lacks an adversarial_review entry")
        raise SystemExit(1)

    adv_path_text = str(adv_entry.get("artifact_path"))
    if not Path(adv_path_text).is_file():
        print(f"MISSING ADVERSARIAL REVIEW ARTIFACT: {adv_path_text}")
        raise SystemExit(1)

    adv = require_json_object(Path(adv_path_text), "ADVERSARIAL REVIEW")

    required_fields = [
        "task",
        "generated_at",
        "review_scope",
        "evidence_inputs",
        "findings",
        "acceptance_recommendation",
        "confidence",
        "rationale",
        "unresolved_gaps",
        "recommended_return_stage",
    ]
    missing_fields = [f for f in required_fields if f not in adv]
    if missing_fields:
        print("INVALID ADVERSARIAL REVIEW: missing keys:", missing_fields)
        raise SystemExit(1)

    if adv.get("task") != report_task:
        print("INVALID ADVERSARIAL REVIEW: task mismatch")
        raise SystemExit(1)

    evidence_inputs = adv.get("evidence_inputs")
    if not isinstance(evidence_inputs, list):
        print("INVALID ADVERSARIAL REVIEW: evidence_inputs must be a list")
        raise SystemExit(1)

    validation_ref = manifest.get("validation_report_ref")
    ledger_ref = manifest.get("transition_ledger_ref")
    if validation_ref not in evidence_inputs or ledger_ref not in evidence_inputs:
        print("INVALID ADVERSARIAL REVIEW: evidence_inputs must include validation report and transition ledger refs")
        raise SystemExit(1)

    if adv.get("acceptance_recommendation") not in {"accept", "needs_followup", "escalate"}:
        print("INVALID ADVERSARIAL REVIEW: bad acceptance_recommendation")
        raise SystemExit(1)

    if adv.get("recommended_return_stage") not in {"none", "planning", "hardening", "execution", "testing", "validation", "escalate"}:
        print("INVALID ADVERSARIAL REVIEW: bad recommended_return_stage")
        raise SystemExit(1)

    conf = adv.get("confidence")
    if not (isinstance(conf, (int, float)) and 0 <= conf <= 1):
        print("INVALID ADVERSARIAL REVIEW: confidence must be numeric in [0,1]")
        raise SystemExit(1)

    print("OK: adversarial review artifact present and consistent")

def validate_freshness_evidence(
    manifest: dict[str, Any],
    report_task: Any,
    manifest_entries_by_path: dict[str, dict[str, Any]],
) -> None:
    if not should_validate_freshness_evidence():
        return

    fres_entry: dict[str, Any] | None = None
    for path, entry in manifest_entries_by_path.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("artifact_role") == "freshness_evidence" or Path(path).name == "repo-task-freshness-evidence.json":
            fres_entry = entry
            break

    if fres_entry is None:
        print("MISSING FRESHNESS EVIDENCE: manifest lacks a freshness_evidence entry")
        raise SystemExit(1)

    fres_path_text = str(fres_entry.get("artifact_path"))
    if not Path(fres_path_text).is_file():
        print(f"MISSING FRESHNESS EVIDENCE ARTIFACT: {fres_path_text}")
        raise SystemExit(1)

    fres = require_json_object(Path(fres_path_text), "FRESHNESS EVIDENCE")

    required_fields = ["task", "generated_at", "source_inputs", "consumed_by_stages"]
    missing_fields = [f for f in required_fields if f not in fres]
    if missing_fields:
        print("INVALID FRESHNESS EVIDENCE: missing keys:", missing_fields)
        raise SystemExit(1)

    if fres.get("task") != report_task:
        print("INVALID FRESHNESS EVIDENCE: task mismatch")
        raise SystemExit(1)

    source_inputs = fres.get("source_inputs")
    if not isinstance(source_inputs, list):
        print("INVALID FRESHNESS EVIDENCE: source_inputs must be a list")
        raise SystemExit(1)

    # Require that the freshness evidence references docs lookup plan or docs evidence
    allowed = {REPO_DOCS_LOOKUP_PLAN_JSON, REPO_DOCS_EVIDENCE_JSONL}
    if not any(str(inp) in allowed or Path(str(inp)).name in allowed for inp in source_inputs):
        print("INVALID FRESHNESS EVIDENCE: source_inputs must include docs lookup plan or docs evidence")
        raise SystemExit(1)

    consumed = fres.get("consumed_by_stages")
    if not isinstance(consumed, list) or not consumed:
        print("INVALID FRESHNESS EVIDENCE: consumed_by_stages must be a non-empty list")
        raise SystemExit(1)

    print("OK: freshness evidence artifact present and consistent")


def validate_artifact_family_manifest(
    report_task: Any,
    validated_stages: list[object],
    evidence_names: set[str],
) -> None:
    if not should_validate_artifact_family_manifest():
        return

    if not ARTIFACT_FAMILY_MANIFEST_PATH.exists():
        print("MISSING ARTIFACT FAMILY MANIFEST: jack/repo-task-artifact-family-manifest.json")
        raise SystemExit(1)

    manifest = require_json_object(ARTIFACT_FAMILY_MANIFEST_PATH, "ARTIFACT FAMILY MANIFEST")
    validate_artifact_family_top_level(manifest, report_task)

    entries = manifest.get("artifact_family_entries")
    if not isinstance(entries, list) or not entries:
        print("INVALID ARTIFACT FAMILY MANIFEST: artifact_family_entries must be a non-empty list")
        raise SystemExit(1)

    validated_stage_names = {str(stage) for stage in validated_stages}
    required_paths_in_manifest, manifest_entries_by_path = collect_artifact_family_entries(
        cast(list[object], entries),
        validated_stage_names,
    )
    validate_artifact_family_required_paths(required_paths_in_manifest)
    validate_artifact_family_evidence_coverage(evidence_names)
    validate_artifact_family_ledger_alignment(manifest_entries_by_path)
    if should_validate_adversarial_review():
        validate_adversarial_review(manifest, report_task, manifest_entries_by_path)
    if should_validate_freshness_evidence():
        validate_freshness_evidence(manifest, report_task, manifest_entries_by_path)

p = Path("jack/repo-task-validation-report.json")
if not p.exists():
    print("MISSING: jack/repo-task-validation-report.json")
    raise SystemExit(1)
try:
    data = cast(dict[str, Any], json.loads(p.read_text(encoding="utf-8")))
except Exception as e:
    print("INVALID JSON:", e)
    raise SystemExit(1)

required = ["validated", "methods", "evidence_links", "verifier_version"]
missing = [k for k in required if k not in data]
if missing:
    print("MISSING KEYS:", missing)
    raise SystemExit(1)

evidence_links: list[object] = cast(list[object], data.get("evidence_links", []))
if not evidence_links:
    print("MISSING OR EMPTY EVIDENCE LINKS")
    raise SystemExit(1)

missing_links: list[str] = []
for link in evidence_links:
    if not isinstance(link, str) or not link.strip():
        missing_links.append(str(link))
        continue
    if not Path(link).is_file():
        missing_links.append(link)

if missing_links:
    print("MISSING EVIDENCE ARTIFACTS:")
    for link in missing_links:
        print(f" - {link}")
    raise SystemExit(1)

evidence_names = {Path(link).name for link in evidence_links if isinstance(link, str) and link.strip()}
missing_evidence_names = sorted(REQUIRED_EVIDENCE_LINKS - evidence_names)
unexpected_evidence_names = sorted(evidence_names - REQUIRED_EVIDENCE_LINKS)
if missing_evidence_names or unexpected_evidence_names:
    print("INVALID EVIDENCE BUNDLE:")
    if missing_evidence_names:
        print(" - missing required:")
        for name in missing_evidence_names:
            print(f"   - {name}")
    if unexpected_evidence_names:
        print(" - unexpected:")
        for name in unexpected_evidence_names:
            print(f"   - {name}")
    raise SystemExit(1)

invalid_artifacts: list[str] = []
report_task = data.get("task")
for link in evidence_links:
    if not isinstance(link, str):
        invalid_artifacts.append(f"{link!r} (not a string path)")
        continue
    artifact_path = Path(link)
    required_fields = MINIMAL_ARTIFACT_REQUIREMENTS.get(artifact_path.name)
    if required_fields is None:
        invalid_artifacts.append(f"{link} (unrecognized JACK artifact)")
        continue
    try:
        artifact_json = json.loads(artifact_path.read_text(encoding="utf-8"))
    except Exception as e:
        invalid_artifacts.append(f"{link} (invalid JSON: {e})")
        continue
    if not isinstance(artifact_json, dict):
        invalid_artifacts.append(f"{link} (not a JSON object)")
        continue
    artifact_data = cast(dict[str, Any], artifact_json)
    missing_fields = [field for field in required_fields if not artifact_data.get(field)]
    if missing_fields:
        invalid_artifacts.append(
            f"{link} (missing required fields: {', '.join(missing_fields)})"
        )
        continue
    if artifact_data.get("task") != report_task:
        invalid_artifacts.append(
            f"{link} (task mismatch: {artifact_data.get('task')!r} != {report_task!r})"
        )

if invalid_artifacts:
    print("INVALID EVIDENCE ARTIFACTS:")
    for link in invalid_artifacts:
        print(f" - {link}")
    raise SystemExit(1)

validated_stages: list[object] = cast(list[object], data.get("validated", []))
if not validated_stages:
    print("MISSING OR EMPTY VALIDATED STAGES")
    raise SystemExit(1)

unknown_validated_stages = [stage for stage in validated_stages if stage not in KNOWN_VALIDATED_STAGES]
missing_required_stages = [stage for stage in REQUIRED_VALIDATED_STAGES if stage not in validated_stages]
if unknown_validated_stages or missing_required_stages:
    print("INVALID VALIDATED STAGES:")
    if unknown_validated_stages:
        print(" - unknown:")
        for stage in unknown_validated_stages:
            print(f"   - {stage}")
    if missing_required_stages:
        print(" - missing required:")
        for stage in missing_required_stages:
            print(f"   - {stage}")
    raise SystemExit(1)

expected_validated_sequence: list[str] = [*TRANSITION_REQUIRED_STAGE_SEQUENCE]
if Path("scripts/repo_task_patch_sketch.py").is_file():
    expected_validated_sequence.append(TRANSITION_OPTIONAL_STAGE)

if validated_stages != expected_validated_sequence:
    print("INVALID VALIDATED STAGE SEQUENCE")
    print(" - expected:")
    for stage in expected_validated_sequence:
        print(f"   - {stage}")
    print(" - actual:")
    for stage in validated_stages:
        print(f"   - {stage}")
    raise SystemExit(1)

validate_transition_ledger(report_task, validated_stages)

methods: list[object] = cast(list[object], data.get("methods", []))
if not methods:
    print("MISSING OR EMPTY METHODS")
    raise SystemExit(1)

report_task_text = str(report_task)
if not any(
    isinstance(method, str) and "run_repo_task_flow.py" in method and report_task_text in method
    for method in methods
):
    print("INVALID METHODS: missing current flow runner/task reference")
    raise SystemExit(1)

assumptions = cast(list[object], data.get("assumptions", []))
expected_assumptions = {
    ".github/skills/doublecheck/SKILL.md present",
    "validation_report generated by run_repo_task_flow.py (conservative, not a replacement for human review)",
}
if not assumptions:
    print("MISSING OR EMPTY ASSUMPTIONS")
    raise SystemExit(1)

assumption_values = {assumption for assumption in assumptions if isinstance(assumption, str)}
if assumption_values != expected_assumptions:
    print("INVALID ASSUMPTIONS: expected exact JACK provenance markers")
    raise SystemExit(1)

not_validated = data.get("not_validated", [])
if not isinstance(not_validated, list) or not_validated:
    print("UNRESOLVED VALIDATION GAPS")
    raise SystemExit(1)

print("OK: validation report present and contains required keys")
print("validated:", data.get("validated"))
if os.environ.get("JACK_REQUIRE_TRANSITION_LEDGER") == "1":
    print("OK: transition ledger present and consistent")
if os.environ.get("JACK_REQUIRE_ARTIFACT_FAMILY_MANIFEST") == "1":
    print("OK: artifact family manifest present and consistent")
raise SystemExit(0)
