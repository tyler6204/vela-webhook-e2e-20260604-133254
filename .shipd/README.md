# Task files

Edit these files, commit them, then run setup checks against a branch, tag, or full commit SHA.

## Start here

- `.shipd/prompt.md` is the task the solver reads. Write it like a concise issue for another engineer.
- `.shipd/task.ts` is the typed checklist. It points at files and contains the scoring rubric.
- `.shipd/private/` is reviewer-only. Solvers should not see those files.
- `.shipd/public/` contains setup inputs that are visible to solvers.

## Files

- `.shipd/task.ts` - typed task manifest.
- `.shipd/prompt.md` - solver prompt.
- `.shipd/public/setup.sh` - public setup command.
- `.shipd/private/reference.patch` - reviewer-only reference solution.
- `.shipd/private/hidden_tests/verifier.py` - reviewer-only verifier.
- `.shipd/private/reviewer_notes.md` - reviewer notes.
- `.shipd/.types/prometheus.d.ts` - generated local editor types. Re-run the installer to refresh it.

Re-running the installer keeps authored task files and refreshes only generated
support files such as this README and `.shipd/.types/prometheus.d.ts`.

## Prometheus submission metadata

The `proposal` object in `.shipd/task.ts` is authoritative after the
repository is connected. It contains the title, challenge family, source type,
optional source URL, idea, expected skill, and expected horizon. Commit changes,
then refresh setup checks to sync them into Prometheus.

Repository URL and branch or tag remain setup inputs because Prometheus needs
them before it can read `.shipd/task.ts`. Re-running the installer preserves
the authored manifest.

## Path and privacy rules

- Use repository-relative paths with `/`. Do not use absolute paths, Windows drive paths, NUL bytes, or `..` segments.
- Keep reviewer notes, the reference patch, and every file used by `commands.verify` under a declared `privateFiles` path.
- Keep the prompt, public setup inputs, and required outputs outside `.shipd/private`.
- Do not overlap public and private roots. The usual declaration is `privateFiles: [".shipd/private"]`.
- `commands.applyReference` must name exactly one private `.patch` file.

## Required outputs

- Every `outputs.required` entry must be a unique repository-relative file path, not a directory.
- Required outputs must not be private.
- Name each exact required output path in `.shipd/prompt.md` so the solver knows what to produce.
- Verifier checks require every output to exist as a regular file after the reference solution runs.

## What the checks do

Setup begins with static checks. They resolve the Git ref to one commit, parse `.shipd/task.ts` without
executing it, validate paths and boundaries, inspect the patch, and hash every declared prompt, setup, verifier,
notes, and reference input. Prometheus then runs task-quality and task-difficulty reviews before verifier checks.

Verifier checks execute the pinned commit once in a sandbox:

1. Run `commands.setup`.
2. Run `commands.verify` before the reference patch; it must fail.
3. Check and run `commands.applyReference`.
4. Run `commands.verify` twice; both runs must succeed with the same normalized result.
5. Check required output files.
6. Copy the solver view, remove every declared private path, and verify no private file remains.
7. Require the verifier's JSON result to include a finite `score` from 0 to 1. The reference
   solution must receive a full score of `1`.

A pinned commit can enter verifier execution only once. To run verifier checks
again, push or select a new commit and run setup checks to pin that new SHA.

Setup may use network access to install dependencies. Do not rely on verifier network isolation.

## Before you commit

Replace starter text with task-specific content. If a file still describes checkpoint examples,
it is not ready.

Also confirm:

- the reference patch is a normal text Git patch with at least one hunk and no private-path changes
- the verifier fails on the unmodified repository and passes on the reference solution
- every rubric leaf is marked `deterministic` or `qualitative`, with child points adding up correctly
- required outputs are documented in the prompt and produced by the reference solution
