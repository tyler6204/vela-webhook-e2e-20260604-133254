export declare function defineTask(task: Task): Task;

export type Task = {
  /** Task metadata. Keep the full task wording in prompt.md. */
  proposal: TaskProposal;

  /** Repository-relative workspace settings. */
  workspace: WorkspaceConfig;

  /** Markdown file the solver reads first. */
  prompt: string;

  /** Files or folders that are only for reviewers and checks. */
  privateFiles: string[];

  /** Commands used to set up, verify, and apply the reference solution. */
  commands: CommandConfig;

  /** Reviewer scoring rubric locations. */
  rubrics: RubricConfig;

  /** Files a solver is expected to produce by the end of the task. */
  outputs: OutputConfig;
};

export type TaskProposal = {
  /** Clear task title. Replace bracketed starter text before running checks. */
  title: string;

  /** Optional paper, issue, or design document URL. Leave it out when there is no source. */
  sourceUrl?: string;
};

export type WorkspaceConfig = {
  /** Repository-relative workspace root. Use "." when the repo root is the task root. */
  root: ".";
};

export type CommandConfig = {
  /** Public setup command that works from the repo root. */
  setup: string;

  /** Private verifier command that checks the final solver output. */
  verify: string;

  /** Private reference solution command. Usually applies .shipd/private/reference.patch. */
  applyReference: string;
};

export type RubricConfig = {
  /** YAML rubric tree used by reviewers. */
  rubricTree: string;
};

export type OutputConfig = {
  /** Required output files produced by a solver or checked by the verifier. */
  required: string[];
};
