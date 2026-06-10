import { defineTask } from "./.types/shipd";

export default defineTask({
  proposal: {
    title: "Test Submission",
    sourceUrl: "https://docs.github.com/en/webhooks/webhook-events-and-payloads#push",
  },

  workspace: {
    root: ".",
  },

  prompt: ".shipd/prompt.md",
  privateFiles: [".shipd/private"],

  review: {
    notes: ".shipd/private/reviewer_notes.md",
  },

  commands: {
    setup: "bash .shipd/public/setup.sh",
    verify: "python .shipd/private/hidden_tests/verifier.py",
    applyReference: "git apply .shipd/private/reference.patch",
  },

  rubric: {
    label: "GitHub webhook submission handling",
    totalPoints: 10,
    children: [
      {
        label: "Understands the webhook gap",
        points: 3,
        children: [
          {
            label: "Explains that signature verification always passes and push fields are empty",
            points: 2,
            kind: "qualitative",
          },
          {
            label: "Explains why HMAC-SHA256 verification with compare_digest restores trust",
            points: 1,
            kind: "qualitative",
          },
        ],
      },
      {
        label: "Webhook handler implementation",
        points: 4,
        children: [
          {
            label: "verify_signature rejects missing and invalid X-Hub-Signature-256 headers",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "parse_push_event returns repo, ref, and commit from a push payload",
            points: 1,
            kind: "deterministic",
          },
          {
            label: "Keeps the public function signatures in webhook/github.py unchanged",
            points: 1,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "Verification evidence",
        points: 2,
        children: [
          {
            label: "tests/test_github_webhook.py covers valid signatures, rejections, and push parsing",
            points: 1,
            kind: "deterministic",
          },
          {
            label: "metrics.json includes tests_passed, tests_total, invalid_signature_rejected, and push_fields_extracted",
            points: 1,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "Submission report",
        points: 1,
        children: [
          {
            label: "report.md documents setup, the pytest command, and expected webhook behavior",
            points: 1,
            kind: "qualitative",
          },
        ],
      },
    ],
  },

  outputs: {
    required: ["metrics.json", "report.md"],
  },
});
