import { defineTask } from "./.types/shipd";

export default defineTask({
  proposal: {
    title: "Newer Submission",
    description: `This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test`,
    whyThisMatters: `This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test This is a test`,

    // Optional context. Fill these only when they are true for this task.
    sourceType: "public_repo",
    family: "training_debugger",
  },

  workspace: {
    root: ".",
  },

  agent: {
    instruction: ".shipd/instruction.md",
    hide: ["private"],
  },

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
