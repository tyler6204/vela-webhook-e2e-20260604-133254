# GitHub Webhook Integration Test: Vela Compatibility

A Vela webhook integration test needs to be created and/or validated to ensure that webhooks from GitHub are being properly received, parsed, and handled by this repository. Currently, there isn't an automated check confirming that the repository can correctly process typical webhook payloads as expected by Vela's requirements.

The missing functionality is an E2E test or script which sets up the local environment, triggers sample GitHub webhook payloads (either by simulating a webhook or using actual API calls), and verifies that the repo processes these payloads as intended (for example, by checking logs, outputs, or integration API results).

## Task

Implement an E2E test that verifies GitHub webhook payloads are accepted and parsed according to the Vela webhook specification. Ensure this is tested through the main entry point(s) used in production. If not present, set up a minimal test infrastructure to automate this check.

## Expected outcome

A working integration test that can be run locally to confirm:
- GitHub webhook events are received successfully.
- The payloads are parsed and handled as expected.
- There are clear assertions or output on success/failure.
The test should be self-contained and not break existing CI or local setups.

## How to check it

Run the following locally:
```bash
bash .shipd/public/setup.sh
# Replace this placeholder with the actual script or test command, e.g.:
npm test
# or
python -m pytest tests/test_github_webhook.py
```
Ensure the test passes and outputs a summary indicating success.

## Notes

- Do not introduce dependencies that require network access during the test run (mock GitHub if needed).
- Ensure the test is reproducible and idempotent.
- Adhere to any conventions already present in the repo for naming, structure, and testing.
- Document any environment variables or secrets required.
