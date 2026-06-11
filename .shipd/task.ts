import { defineTask } from "./.types/prometheus";

export default defineTask({
  proposal: {
    title: "Production-Grade GitHub Webhook Delivery Pipeline for Vela",
    category: "other_research_engineering",
    sourceType: "production_spec",
    sourceUrl: "https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries",
    idea:
      "Implement a secure, deterministic GitHub webhook delivery pipeline for Vela with rotating-secret HMAC authentication, strict JSON parsing, multi-event normalization, policy evaluation, and bounded thread-safe replay protection."
  },

  workspace: {
    root: ".",
  },

  execution: {
    profile: "cpu_standard",
  },

  prompt: ".shipd/prompt.md",
  privateFiles: [".shipd/private"],

  review: {
    notes: ".shipd/private/reviewer_notes.md",
  },

  commands: {
    setup: "bash .shipd/public/setup.sh",
    verify: ".venv/bin/python .shipd/private/hidden_tests/verifier.py",
    applyReference: "git apply --unidiff-zero .shipd/private/reference.patch",
  },

  rubric: {
    label: "GitHub webhook delivery pipeline",
    totalPoints: 20,
    children: [
      {
        label: "Authentication and decoding",
        points: 4,
        children: [
          {
            label: "Canonical HMAC-SHA256 verification checks every rotating secret",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "Strict UTF-8 JSON rejects duplicates, non-finite values, and deep payloads",
            points: 2,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "Event normalization",
        points: 5,
        children: [
          {
            label: "Push actions, SHAs, commits, messages, and changed files are normalized",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "Pull request refs, fork state, actions, and merged SHA are normalized",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "Merge group actions and queue/base refs are normalized",
            points: 1,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "Policy evaluation",
        points: 3,
        children: [
          {
            label: "Repository, ref, sender, and skip-token precedence is exact",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "Deletion, pull request, fork, draft, and merge-group rules are enforced",
            points: 1,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "Replay protection",
        points: 4,
        children: [
          {
            label: "Reserve, duplicate, conflict, commit, abort, and expiry states are correct",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "Capacity, stale generations, deterministic eviction, and concurrency are safe",
            points: 2,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "End-to-end processor",
        points: 3,
        children: [
          {
            label: "Headers, content type, UUID, size, and raw-body ordering are validated",
            points: 2,
            kind: "deterministic",
          },
          {
            label: "Results, rejected decisions, exact duplicates, conflicts, and retries compose",
            points: 1,
            kind: "deterministic",
          },
        ],
      },
      {
        label: "Evidence",
        points: 1,
        children: [
          {
            label: "Metrics and report accurately document a reproducible passing implementation",
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
