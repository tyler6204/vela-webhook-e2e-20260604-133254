#!/usr/bin/env python3
"""Private verifier for the GitHub webhook submission task."""

import json
import subprocess
from pathlib import Path
from typing import Optional

METRICS_PATH = Path("metrics.json")
REPORT_PATH = Path("report.md")


def fail(message: str, checks: Optional[dict] = None) -> None:
    payload = {"ok": False, "score": 0, "error": message}
    if checks is not None:
        payload["checks"] = checks
    print(json.dumps(payload))
    raise SystemExit(1)


if not METRICS_PATH.exists():
    fail("metrics.json is required")
if not REPORT_PATH.exists():
    fail("report.md is required")

try:
    metrics = json.loads(METRICS_PATH.read_text())
except json.JSONDecodeError as exc:
    fail(f"metrics.json is not valid JSON: {exc}")

required_metrics = [
    "tests_passed",
    "tests_total",
    "invalid_signature_rejected",
    "push_fields_extracted",
]
missing = [key for key in required_metrics if key not in metrics]
if missing:
    fail(f"Missing required metrics: {missing}")

tests_passed = int(metrics["tests_passed"])
tests_total = int(metrics["tests_total"])
invalid_signature_rejected = bool(metrics["invalid_signature_rejected"])
push_fields_extracted = bool(metrics["push_fields_extracted"])

report_text = REPORT_PATH.read_text().lower()

checks = {
    "tests_passed_equals_total": tests_passed == tests_total and tests_total > 0,
    "invalid_signature_rejected": invalid_signature_rejected,
    "push_fields_extracted": push_fields_extracted,
    "report_mentions_signature": "signature" in report_text,
    "report_mentions_webhook": "webhook" in report_text,
}

pytest_result = subprocess.run(
    ["python", "-m", "pytest", "tests/test_github_webhook.py", "-q"],
    capture_output=True,
    text=True,
)
checks["pytest_passes"] = pytest_result.returncode == 0

if not all(checks.values()):
    payload = {"ok": False, "score": 0, "checks": checks}
    if pytest_result.stdout:
        payload["pytest_stdout"] = pytest_result.stdout[-2000:]
    if pytest_result.stderr:
        payload["pytest_stderr"] = pytest_result.stderr[-2000:]
    print(json.dumps(payload))
    raise SystemExit(1)

print(json.dumps({"ok": True, "score": 1, "checks": checks}))
