# [task title]

Write this like a short issue you would hand to a strong engineer. Keep it concrete and human.
Do not describe the review system here; describe the work inside this repo.

## Task

[Explain what is broken, missing, or worth building in one or two paragraphs.]

Example:
The training code can save checkpoints, but resumed training produces a different loss curve than
an uninterrupted run.

Fix checkpoint loading so resumed training restores the optimizer, scheduler, and RNG state needed
for deterministic continuation.

## Expected outcome

[Describe the behavior a correct solution should have.]

Example:
A resumed run from a saved checkpoint should match the uninterrupted run within the tolerance used
by the tests, and existing training entry points should keep working.

## How to check it

[Give the shortest useful local check.]

Example:
```bash
bash .shipd/public/setup.sh
python -m pytest tests/test_checkpoint_resume.py
```

## Notes

[Mention only constraints a solver genuinely needs to know.]

Examples:
- Do not change the public CLI flags.
- Do not require network access during tests.
