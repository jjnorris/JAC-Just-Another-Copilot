#!/usr/bin/env python3
"""
Generate or update a detect-secrets baseline for the repository.

Usage:
  python scripts/generate_secrets_baseline.py [--baseline PATH]

This script attempts to run the `detect-secrets` CLI and write the
output to the baseline file. If the CLI is not available, it prints
instructions instead of failing noisily.

Security note: Inspect baseline output carefully. Do NOT commit real
secrets into the baseline; redact or remove any real credentials before
committing.
"""

from __future__ import annotations
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate detect-secrets baseline")
    parser.add_argument("--baseline", "-b", default=".secrets.baseline", help="Baseline output path")
    args = parser.parse_args()

    baseline_path = Path(args.baseline)

    if shutil.which("detect-secrets") is None:
        print("detect-secrets not found. Install with: python -m pip install detect-secrets", file=sys.stderr)
        print(f"Then run: detect-secrets scan > {baseline_path}")
        return 1

    cmd = ["detect-secrets", "scan", "--all-files"]
    try:
        print("Running:", " ".join(cmd))
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, text=True)
        baseline_path.write_text(proc.stdout, encoding="utf-8")
        print(f"Wrote baseline to {baseline_path}")
        return 0
    except subprocess.CalledProcessError as exc:
        print("detect-secrets failed:", exc.stderr, file=sys.stderr)
        return exc.returncode
    except Exception as exc:  # pragma: no cover - operational
        print("Unexpected error while generating baseline:", exc, file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
