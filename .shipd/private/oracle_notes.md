# TODO: evaluator-only oracle notes

Use this file for reviewer-only hints, expected failure modes, and hidden-test rationale.

Example:

- Expected root cause: checkpoint restore reloads model weights but drops optimizer,
  scheduler, or RNG state.
- Hidden tests should vary seed, checkpoint interval, and batch ordering.
- Passing threshold: resume_loss_delta <= 0.02.
