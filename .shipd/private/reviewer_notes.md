# Reviewer notes

This file is private. Solvers should not see it.

Use it to explain what reviewers should expect from a correct solution.

## Expected solution

TODO: Describe the intended fix or implementation in plain English.

Example:
The checkpoint loader should restore model weights, optimizer state, scheduler state, and RNG state.

## Hidden test plan

TODO: Describe what hidden tests should cover.

Example:
- Resume from different checkpoint intervals.
- Run with at least two random seeds.
- Fail if resume_loss_delta is greater than 0.02.

## Common bad solutions

TODO: List shortcuts or incomplete fixes reviewers should reject.

Example:
- Only lowering the learning rate instead of restoring optimizer state.
- Hardcoding expected metric values.
- Changing the CLI in a way that breaks existing users.
