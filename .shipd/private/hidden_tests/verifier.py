#!/usr/bin/env python3
"""Private verifier for reviewers.

Edit this file so it checks the real outputs for your task.

How it is used:
- A solver works on the repo and produces outputs like metrics.json and report.md.
- Prometheus runs this script privately.
- Exit 0 means the solution passed.
- Exit 1 means the solution failed.

The checks below are examples. Replace the metric names and thresholds with the ones your task
actually needs.
"""

import json
import math
from pathlib import Path

METRICS_PATH = Path("metrics.json")
REPORT_PATH = Path("report.md")


def fail(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}))
    raise SystemExit(1)


if not METRICS_PATH.exists():
    fail("metrics.json is required")
if not REPORT_PATH.exists():
    fail("report.md is required")

try:
    metrics = json.loads(METRICS_PATH.read_text())
except json.JSONDecodeError as exc:
    fail(f"metrics.json is not valid JSON: {exc}")

required_metrics = ["resume_loss_delta", "clean_loss", "resumed_loss"]  # edit these
missing = [key for key in required_metrics if key not in metrics]
if missing:
    fail(f"Missing required metrics: {missing}")

resume_delta = float(metrics["resume_loss_delta"])
clean_loss = float(metrics["clean_loss"])
resumed_loss = float(metrics["resumed_loss"])

checks = {
    "resume_loss_delta": resume_delta <= 0.02,  # edit this threshold
    "clean_loss_finite": math.isfinite(clean_loss) and clean_loss < 10,
    "resumed_loss_finite": math.isfinite(resumed_loss) and resumed_loss < 10,
    "report_mentions_checkpoint": "checkpoint" in REPORT_PATH.read_text().lower(),
}

if not all(checks.values()):
    fail(f"Hidden verifier checks failed: {checks}")

print(json.dumps({"ok": True, "checks": checks}))
