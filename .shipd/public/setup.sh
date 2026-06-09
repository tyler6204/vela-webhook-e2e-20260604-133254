#!/usr/bin/env bash
set -euo pipefail

# Replace this with the real environment bootstrap for this repo.

python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
  python -m pip install -r requirements.txt
elif [ -f pyproject.toml ]; then
  python -m pip install -e ".[test]" || python -m pip install -e .
else
  python -m pip install numpy pytest
fi

printf "Environment ready. Edit .shipd/private/hidden_tests/verifier.py for evaluator checks.\n"
