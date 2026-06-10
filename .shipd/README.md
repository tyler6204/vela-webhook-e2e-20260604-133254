# Prometheus task files

This folder tells Prometheus how to run and review your task. You do not need to understand every
system detail. Edit the files below, commit them, then click "Refresh repo" in Prometheus.

## Edit these files

1. .shipd/task.ts
   The typed table of contents. Fill out proposal, workspace, agent, commands, rubrics, and outputs.
   Your editor can hover fields for descriptions from .shipd/.types/shipd.d.ts.

2. .shipd/prompt.md
   The prompt a solver will read first. Write it like a concise issue for another engineer.

3. .shipd/public/setup.sh
   A simple script that installs dependencies from the repo root.

4. .shipd/private/hidden_tests/verifier.py
   Reviewer-only checks. This should fail bad solutions and pass good ones.

5. .shipd/private/reference.patch
   A reviewer-only example solution patch. It proves the task is solvable.

6. .shipd/private/reviewer_notes.md
   Notes for reviewers: expected solution, edge cases, and what the hidden verifier is checking.

7. .shipd/rubrics/rubric_tree.yaml
   How reviewers should score the work.

8. .shipd/.types/shipd.d.ts
   Local TypeScript declarations for editor help. Do not edit this unless Shipd changes the contract.

## Visibility

- Solvers can see prompt.md and public/.
- Solvers should not see private/.

## Quick rule

If a file has bracketed edit prompts, replace them with task-specific content.
If you are not using a file, delete the prompt or make it accurate.
Do not invent a paper URL, metric, or estimate just to fill a field.
