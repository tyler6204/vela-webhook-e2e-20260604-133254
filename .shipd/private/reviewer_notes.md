# Reviewer notes

This file is private. Solvers should not see it.

## Task family

This task belongs to **SWE / CI integration / webhook handling**, not training debugging.

The solver fixes GitHub webhook signature verification and push-event parsing for a Vela build
trigger. There is no model training, checkpointing, optimizer state, or loss-curve analysis.

## Originality

This task was authored for the disposable `vela-webhook-e2e-20260604-133254` repository. It is
not a relabeled checkpoint-resume or training-debugging problem.

What makes it distinct:

- The broken code is a webhook handler (`webhook/github.py`), not training infrastructure.
- The fix requires HMAC-SHA256 verification of `X-Hub-Signature-256` plus extraction of Vela
  trigger fields (`repo`, `ref`, `commit`) from a push payload.
- Verification is local and fixture-driven (`tests/fixtures/push.json`), with no GitHub network
  calls.
- Required solver outputs are webhook-specific metrics (`invalid_signature_rejected`,
  `push_fields_extracted`), not training-loss deltas.

No prior related submission in this repository reuses the same prompt, patch target, verifier
checks, or rubric wording.

## Expected solution

`verify_signature` in `webhook/github.py` should:

- Return `False` when the signature header is missing or does not start with `sha256=`
- Compute `HMAC-SHA256(secret, raw_body)` and compare it to the header value with
  `hmac.compare_digest`

`parse_push_event` should return:

- `repo` from `payload["repository"]["full_name"]`
- `ref` from `payload["ref"]`
- `commit` from `payload["after"]`

Tests should prove that a valid signature is accepted, an invalid signature is rejected, and a
push fixture is parsed into the three fields above.

## Hidden test plan

- Require `metrics.json` and `report.md`
- Require numeric `tests_passed` and `tests_total` with `tests_passed == tests_total`
- Require `invalid_signature_rejected` and `push_fields_extracted` to be true
- Require `report.md` to mention webhook signature validation
- Re-run `pytest tests/test_github_webhook.py` privately and fail if it does not pass

## Common bad solutions

- Skipping signature verification or accepting any non-empty header
- Parsing only part of the push payload (for example repo name without ref or commit)
- Hardcoding metric values without running tests
- Adding network calls to GitHub instead of using local fixtures and HMAC generation
- Changing the public function signatures in `webhook/github.py`
