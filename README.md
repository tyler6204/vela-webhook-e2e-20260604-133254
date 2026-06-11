# vela-webhook-e2e-20260604-133254

Disposable repository for Vela GitHub webhook delivery processing.

## Layout

- `webhook/github.py` — authentication, strict JSON decoding, event normalization, and policy
- `webhook/replay.py` — bounded thread-safe delivery replay protection
- `webhook/processor.py` — end-to-end request processing
- `tests/test_github_webhook.py` — local security and delivery tests
- `.shipd/` — task definition, verifier, and reference solution for reviewers

## Local setup

```bash
bash .shipd/public/setup.sh
python -m pytest tests/test_github_webhook.py
```
