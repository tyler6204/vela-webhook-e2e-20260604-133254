export declare function defineTask(task: PrometheusTask): PrometheusTask;

export type PrometheusTask = {
  /** Human-readable task name. Usually copied from your Shipd submission. */
  proposal: TaskProposal;

  /** Workspace settings. Keep root as "." for Prometheus v0. */
  workspace: WorkspaceConfig;

  /** Solver-facing prompt and visibility settings. */
  agent: AgentConfig;

  /** Commands Prometheus uses to set up, verify, and prove the task. */
  commands: CommandConfig;

  /** Reviewer scoring rubric locations. */
  rubrics: RubricConfig;

  /** Files a solver is expected to produce by the end of the task. */
  outputs: OutputConfig;
};

export type TaskProposal = {
  /** Clear title reviewers can scan in lists. Replace bracketed starter text before refreshing Git. */
  title: string;

  /** One short paragraph explaining the concrete work a solver should perform. */
  description: string;

  /** The evidence that a good solution proves, such as a metric, benchmark, or verifier signal. */
  whyThisMatters: string;

  /** Optional source material for the task, such as a paper, issue, or design doc. */
  sourceUrl?: string;

  /** Optional source category for reviewer triage. */
  sourceType?: "paper" | "public_repo" | "production_spec" | "private_project" | "internal_style_spec" | "other";

  /** Optional expected solver horizon. */
  estimatedSolverTime?: "two_hours" | "four_hours" | "eight_hours" | "one_day" | "two_days" | "forty_hours";

  /** Optional task family. */
  family?: "training_debugger" | "paper_implementation" | "inference_optimizer" | "grader_forensics" | "dataset_forensics" | "synthetic_data" | "other_research_engineering";
};

export type WorkspaceConfig = {
  /** Repository-relative workspace root. Prometheus v0 expects ".". */
  root: ".";
};

export type AgentConfig = {
  /** Markdown prompt the solver reads first. Keep it concise, concrete, and task-specific. */
  prompt: string;

  /** .shipd-relative paths hidden from solvers. Keep "private" unless reviewers explicitly change the layout. */
  hide: string[];
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
