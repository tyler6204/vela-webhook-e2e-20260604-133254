This repository is meant to validate GitHub webhook payloads for Vela, but the handler in
`webhook/github.py` does not yet meet that bar. Signature verification always succeeds, and
`parse_push_event` returns empty fields instead of the repository, ref, and commit Vela needs
to trigger builds.

Implement proper GitHub webhook handling so push events can be trusted and parsed. The handler
must verify `X-Hub-Signature-256` with HMAC SHA-256, reject missing or invalid signatures, and
extract `repository.full_name`, `ref`, and `after` from a standard push payload.

Add or update tests in `tests/test_github_webhook.py` that cover valid signatures, invalid
signatures, and push payload parsing. Run the test suite after your changes and write the
required outputs:

- `metrics.json` with `tests_passed`, `tests_total`, `invalid_signature_rejected`, and
  `push_fields_extracted`
- `report.md` with concise, reproducible steps for setup, test execution, and expected results

Do not require live network access in tests. Use the fixture in `tests/fixtures/push.json` and
construct signatures locally with a known secret.
