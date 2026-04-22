#!/usr/bin/env python3
"""Minimal spec intake normalizer with omission detection.

Reads freeform project descriptions and emits a structured JSON summary
including detected omissions and recommended clarifying questions.

Usage:
  python3 scripts/spec_intake.py --text "..." [--stack fastapi] [--jurisdiction US] [--out spec.json]
Or read from stdin when --text omitted.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Dict, List, Any


STACK_KEYWORDS = {
    "python": ["python"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "typescript": ["typescript", "ts"],
    "react": ["react"],
    "nextjs": ["nextjs", "next.js", "next js"],
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def infer_project_type(text: str) -> str:
    t = text.lower()
    if any(
        k in t for k in ("web app", "webapp", "web application", "web site", "website")
    ):
        return "webapp"
    if any(k in t for k in ("api", "rest", "endpoint", "service")):
        return "api"
    if any(k in t for k in ("library", "sdk", "package")):
        return "library"
    if any(k in t for k in ("cli", "command line")):
        return "cli"
    if any(k in t for k in ("pipeline", "etl", "data pipeline")):
        return "data-pipeline"
    return "application"


def detect_stack_hint(text: str, explicit_stack: str | None) -> str | None:
    if explicit_stack:
        return explicit_stack
    t = text.lower()
    for stack, keys in STACK_KEYWORDS.items():
        for k in keys:
            if k in t:
                return stack
    return None


def detect_omissions(text: str) -> Dict[str, Any]:
    t = text.lower()
    has_auth = any(
        k in t
        for k in (
            "auth",
            "authentication",
            "oauth",
            "oauth2",
            "jwt",
            "login",
            "sso",
            "access control",
            "access-control",
        )
    )
    has_storage = any(
        k in t
        for k in (
            "database",
            "db",
            "postgres",
            "mysql",
            "s3",
            "bucket",
            "storage",
            "upload",
            "file",
        )
    )
    has_secrets = any(
        k in t
        for k in ("secret", "env", "vault", "kms", "key management", "key-management")
    )
    has_deploy = any(
        k in t
        for k in (
            "aws",
            "gcp",
            "azure",
            "ecs",
            "kubernetes",
            "k8s",
            "lambda",
            "serverless",
            "deploy",
            "deployment",
            "host on",
        )
    )
    has_observability = any(
        k in t
        for k in (
            "logging",
            "metrics",
            "prometheus",
            "sentry",
            "monitor",
            "monitoring",
            "tracing",
            "alerts",
        )
    )
    has_privacy = any(
        k in t
        for k in (
            "pii",
            "personal data",
            "personal information",
            "health",
            "patient",
            "medical",
            "ssn",
            "social security",
            "hipaa",
            "phi",
            "pci",
        )
    )
    has_license = any(
        k in t
        for k in (
            "license",
            "mit",
            "gpl",
            "bsd",
            "commercial",
            "proprietary",
            "third-party",
        )
    )
    has_abuse = any(
        k in t
        for k in (
            "spam",
            "abuse",
            "malicious",
            "illegal",
            "fraud",
            "exfiltrate",
            "attack",
        )
    )

    omissions = {
        "auth": not has_auth,
        "storage": not has_storage,
        "secrets_handling": not has_secrets,
        "deployment_target": not has_deploy,
        "observability": not has_observability,
        "privacy_or_regulated_data": has_privacy,
        "licensing": not has_license,
        "abuse_misuse": has_abuse,
    }
    return omissions


def recommended_questions(omissions: Dict[str, Any]) -> List[str]:
    q: List[str] = []
    if omissions.get("auth"):
        q.append(
            "What authentication or access control is required (OAuth2, API keys, SSO, none)?"
        )
    if omissions.get("storage"):
        q.append(
            "Where should data be stored (database type, cloud storage, local filesystem)?"
        )
    if omissions.get("secrets_handling"):
        q.append("How should secrets/credentials be managed (env vars, KMS, Vault)?")
    if omissions.get("deployment_target"):
        q.append(
            "Where will this be deployed or hosted (AWS/GCP/Azure/Kubernetes/other)?"
        )
    if omissions.get("observability"):
        q.append("What logging/metrics/tracing/alerts are expected for observability?")
    if omissions.get("licensing"):
        q.append(
            "Are there licensing constraints or 3rd-party dependency policies to follow?"
        )
    if omissions.get("privacy_or_regulated_data"):
        q.append(
            "Does this process personal or regulated data (PII, health, payments)? If so, which jurisdiction/regulation applies?"
        )
    if omissions.get("abuse_misuse"):
        q.append(
            "Are there abuse or misuse risks we should mitigate (spam, fraud, exfiltration)?"
        )
    return q


def security_considerations_from_omissions(omissions: Dict[str, Any]) -> List[str]:
    s: List[str] = []
    if omissions.get("auth"):
        s.append("Ensure strong authentication and least-privilege access controls.")
    if omissions.get("secrets_handling"):
        s.append("Plan for encrypted secret storage and rotation (KMS/Vault).")
    if omissions.get("storage"):
        s.append(
            "Validate and sanitize uploads; enforce size/type limits; use encryption at rest."
        )
    if omissions.get("abuse_misuse"):
        s.append("Rate-limit and monitor endpoints to mitigate abuse and exfiltration.")
    return s


def privacy_considerations(omissions: Dict[str, Any]) -> List[str]:
    p: List[str] = []
    if omissions.get("privacy_or_regulated_data"):
        p.append(
            "Personal or health data detected; identify jurisdiction and apply appropriate controls (encryption, data minimization, access rules)."
        )
    return p


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--text", help="Freeform project description; if omitted read from stdin"
    )
    ap.add_argument("--stack", help="Optional stack hint")
    ap.add_argument("--jurisdiction", help="Optional jurisdiction or location text")
    ap.add_argument("--out", help="Output JSON file", default="spec_intake.json")
    args = ap.parse_args(argv)

    if args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    norm = normalize_text(text)
    proj_type = infer_project_type(norm)
    candidate_stack = detect_stack_hint(norm, args.stack)
    omissions = detect_omissions(norm)
    assumptions: List[str] = []
    if "internal" in norm or "team" in norm or "internal use" in norm:
        assumptions.append("internal_use")
    if "open source" in norm or "oss" in norm:
        assumptions.append("open_source")

    missing = [
        k
        for k, v in omissions.items()
        if (isinstance(v, bool) and v) or (k == "privacy_or_regulated_data" and v)
    ]

    questions = recommended_questions(omissions)
    security = security_considerations_from_omissions(omissions)
    privacy = privacy_considerations(omissions)

    # compliance flags (simple heuristics)
    compliance_flags: List[str] = []
    if "hipaa" in norm or "health" in norm or "patient" in norm:
        compliance_flags.append("health-data")
    if "pci" in norm or "payment" in norm:
        compliance_flags.append("payment-data")

    result: Dict[str, Any] = {
        "project_summary": norm[:1000],
        "normalized_goal": (norm.split(".", 1)[0] if "." in norm else norm)[:400],
        "project_type": proj_type,
        "candidate_stack": candidate_stack or "unspecified",
        "assumptions_detected": assumptions,
        "missing_required_details": missing,
        "recommended_clarifying_questions": questions,
        "security_considerations": security,
        "privacy_considerations": privacy,
        "deployment_considerations": (
            ["Specify deployment target"] if omissions.get("deployment_target") else []
        ),
        "observability_considerations": (
            ["Add logging/metrics/tracing"] if omissions.get("observability") else []
        ),
        "compliance_or_policy_flags": compliance_flags,
    }

    # human readable summary
    summary_lines: List[str] = []
    summary_lines.append(f"Goal: {result['normalized_goal']}")
    summary_lines.append(f"Type: {result['project_type']}")
    summary_lines.append(f"Stack: {result['candidate_stack']}")
    if missing:
        summary_lines.append("Missing details: " + ", ".join(missing))
    if questions:
        summary_lines.append("Clarifying questions: " + " | ".join(questions[:3]))

    human_summary = " \n".join(summary_lines)

    # write JSON
    try:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error: failed to write {args.out}: {e}", file=sys.stderr)
        return 2

    print(human_summary)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
