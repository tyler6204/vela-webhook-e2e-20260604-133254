# TODO: task title

This is the main file a solver reads. Do not describe Shipd or Prometheus here. Describe the work
inside this repo.

## Background

TODO: Explain the repo and the problem in plain English.

Example:
The training code can save checkpoints, but resumed training produces a different loss curve than
an uninterrupted run.

## Goal

TODO: Say exactly what the solver should change.

Example:
Fix checkpoint loading so resumed training restores all state needed for deterministic continuation.

## What to submit

TODO: List the files or outputs the solver must produce.

Recommended default:
- Code changes that fix the issue.
- metrics.json with the required numbers.
- report.md explaining the fix and how it was tested.

## How to check your work

TODO: Give the command a solver should run locally before submitting.

Example:
```bash
bash .shipd/public/setup.sh
python -m pytest tests/test_checkpoint_resume.py
```

## Constraints

TODO: List anything the solver must not change or must preserve.

Examples:
- Do not change the public CLI flags.
- Do not require network access during tests.
- Keep runtime under 5 minutes on a laptop.
