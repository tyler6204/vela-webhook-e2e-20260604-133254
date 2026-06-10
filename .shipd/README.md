# Task files

Edit these files, commit them, then run setup checks.

## Start here

- `.shipd/prompt.md` is the task the solver reads. Write it like a concise issue for another engineer.
- `.shipd/task.ts` is the typed checklist. It points at files and contains the scoring rubric.
- `.shipd/private/` is reviewer-only. Solvers should not see those files.

## Files

- `.shipd/task.ts` - typed task manifest.
- `.shipd/prompt.md` - solver prompt.
- `.shipd/public/setup.sh` - public setup command.
- `.shipd/private/reference.patch` - reviewer-only reference solution.
- `.shipd/private/hidden_tests/verifier.py` - reviewer-only verifier.
- `.shipd/private/reviewer_notes.md` - reviewer notes.
- `.shipd/.types/shipd.d.ts` - local editor types. Do not edit unless the task contract changes.

## Rule

Replace starter text with task-specific content. If a file still describes checkpoint examples,
it is not ready.
