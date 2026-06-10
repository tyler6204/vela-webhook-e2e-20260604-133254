import { defineTask } from "./.types/shipd";

export default defineTask({
  proposal: {
    title: "Test",
    description: `Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 `,
    whyThisMatters: `Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 Test 1 2 3 `,

    // Optional context. Fill these only when they are true for this task.
    sourceType: "public_repo",
    family: "training_debugger",
  },

  workspace: {
    root: ".",
  },

  agent: {
    prompt: ".shipd/prompt.md",
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
