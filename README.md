# vela-webhook-e2e-20260604-133254

Disposable repository for Vela GitHub webhook integration testing.

## Layout

- `webhook/github.py` — GitHub webhook signature verification and push parsing
- `tests/test_github_webhook.py` — local webhook handler tests
- `.shipd/` — task definition, verifier, and reference solution for reviewers

## Local setup

```bash
bash .shipd/public/setup.sh
python -m pytest tests/test_github_webhook.py
```
