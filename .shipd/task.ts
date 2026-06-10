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

  commands: {
    setup: "bash .shipd/public/setup.sh",
    verify: "python .shipd/private/hidden_tests/verifier.py",
    applyReference: "git apply .shipd/private/reference.patch",
  },

  rubrics: {
    rubricTree: ".shipd/rubrics/rubric_tree.yaml",
  },

  outputs: {
    required: ["metrics.json", "report.md"],
  },
});
