# Prometheus task files

This folder tells Prometheus how to run and review your task. You do not need to understand every
system detail. Edit the files below, commit them, then click "Refresh repo" in Prometheus.

## Edit these files

1. .shipd/task.toml
   The table of contents. Only commands/setup, commands/verify, commands/apply_reference,
   rubrics/rubric_tree, agent/instruction, and outputs/required are required. Proposal metadata is
   for humans and can stay minimal.

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

## Quick rule

If a file has bracketed edit prompts, replace them with task-specific content.
If you are not using a file, delete the prompt or make it accurate.
Do not invent a paper URL, metric, or estimate just to fill a field.
