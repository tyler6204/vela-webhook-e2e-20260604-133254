# Prometheus task files

This folder tells Prometheus how to run and review your task. You do not need to understand every
system detail. Edit the files below, commit them, then click "Refresh repo" in Prometheus.

## Edit these files

1. .shipd/task.toml
   The table of contents. It explains what every field means and points Prometheus at the other files.

2. .shipd/instruction.md
   The instructions a solver will read. Write this like you are assigning work to another engineer.

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

## Visibility

- Solvers can see instruction.md and public/.
- Solvers should not see private/.
- Optional public smoke tests can be added later with commands.smoke, but they are not required.

## Quick rule

If a file says TODO, edit it. If you are not using a file, delete its TODO text or make it accurate.
