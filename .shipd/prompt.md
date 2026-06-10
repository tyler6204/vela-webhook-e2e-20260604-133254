[Explain what is broken, missing, or worth building in one or two paragraphs.]

Example:
The training code can save checkpoints, but resumed training produces a different loss curve than
an uninterrupted run.

Fix checkpoint loading so resumed training restores the optimizer, scheduler, and RNG state needed
for deterministic continuation.
