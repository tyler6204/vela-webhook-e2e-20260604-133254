import { defineTask } from "./.types/shipd";

export default defineTask({
  proposal: {
    title: "New Submission",

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
    label: "Task",
    totalPoints: 10,
    children: [
      {
        label: "Understands the problem",
        points: 3,
        children: [
          { label: "Explains the actual bug or missing feature", points: 2, kind: "qualitative" },
          { label: "Explains why the chosen approach should work", points: 1, kind: "qualitative" },
        ],
      },
      {
        label: "Correct implementation",
        points: 4,
        children: [
          { label: "Fixes or implements the requested behavior", points: 3, kind: "deterministic" },
          { label: "Does not break existing public behavior", points: 1, kind: "deterministic" },
        ],
      },
      {
        label: "Evidence",
        points: 2,
        children: [
          { label: "Adds or updates a meaningful test", points: 1, kind: "deterministic" },
          { label: "Provides required metrics or report output", points: 1, kind: "deterministic" },
        ],
      },
      {
        label: "Communication",
        points: 1,
        children: [{ label: "report.md is concise and reproducible", points: 1, kind: "qualitative" }],
      },
    ],
  },

  outputs: {
    required: ["metrics.json", "report.md"],
  },
});
