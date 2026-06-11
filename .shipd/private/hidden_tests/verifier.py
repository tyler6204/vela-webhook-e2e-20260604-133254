#!/usr/bin/env python3
"""Private verifier for the GitHub webhook delivery processing task."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional

METRICS_PATH = Path("metrics.json")
REPORT_PATH = Path("report.md")
PUBLIC_TEST_PATH = Path("tests/test_github_webhook.py")
HIDDEN_TEST_PATH = Path(".shipd/private/hidden_tests/test_delivery_pipeline.py")


def fail(message: str, checks: Optional[dict] = None, result=None) -> None:
    payload = {"ok": False, "score": 0, "error": message}
    if checks is not None:
        payload["checks"] = checks
    if result is not None:
        if result.stdout:
            payload["pytest_stdout"] = result.stdout[-4000:]
        if result.stderr:
            payload["pytest_stderr"] = result.stderr[-4000:]
    print(json.dumps(payload, sort_keys=True))
    raise SystemExit(1)


if not METRICS_PATH.is_file():
    fail("metrics.json is required")
if not REPORT_PATH.is_file():
    fail("report.md is required")

try:
    metrics = json.loads(METRICS_PATH.read_text())
except (OSError, json.JSONDecodeError) as exc:
    fail(f"metrics.json is not valid JSON: {exc}")

required_metrics = {
    "tests_passed",
    "tests_total",
    "signature_rotation_verified",
    "strict_json_verified",
    "event_normalization_verified",
    "replay_protection_verified",
    "policy_verified",
}
missing = sorted(required_metrics - set(metrics))
if missing:
    fail(f"Missing required metrics: {missing}")

tests_passed = metrics["tests_passed"]
tests_total = metrics["tests_total"]
boolean_metrics = [
    "signature_rotation_verified",
    "strict_json_verified",
    "event_normalization_verified",
    "replay_protection_verified",
    "policy_verified",
]

checks = {
    "test_counts_are_integers": (
        isinstance(tests_passed, int)
        and not isinstance(tests_passed, bool)
        and isinstance(tests_total, int)
        and not isinstance(tests_total, bool)
    ),
    "public_test_count_reported": tests_passed == tests_total and tests_total >= 20,
    "boolean_metrics_are_true": all(metrics[name] is True for name in boolean_metrics),
}

report = REPORT_PATH.read_text().casefold()
for term in [
    "hmac",
    "rotat",
    "duplicate",
    "replay",
    "push",
    "pull_request",
    "merge_group",
    "pytest",
]:
    checks[f"report_mentions_{term}"] = term in report

if not all(checks.values()):
    fail("required outputs are incomplete or inconsistent", checks)

pytest_result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        str(PUBLIC_TEST_PATH),
        str(HIDDEN_TEST_PATH),
        "-q",
    ],
    capture_output=True,
    text=True,
)
checks["public_and_hidden_tests_pass"] = pytest_result.returncode == 0

if not all(checks.values()):
    fail("webhook verification failed", checks, pytest_result)

print(json.dumps({"ok": True, "score": 1, "checks": checks}, sort_keys=True))
