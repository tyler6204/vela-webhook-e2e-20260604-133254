/**
 * AUTO-GENERATED PROMETHEUS EDITOR TYPES. DO NOT EDIT.
 *
 * Edit .shipd/task.ts, .shipd/prompt.md, and .shipd/private/reviewer_notes.md instead.
 * Reinstalling or refreshing the .shipd scaffold can overwrite this file.
 */

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

  /** Reviewer-only notes and review settings. */
  review: ReviewConfig;

  /** Commands used to set up, verify, and apply the reference solution. */
  commands: CommandConfig;

  /** Reviewer scoring rubric. Branch points must equal their child point total. */
  rubric: RubricTree;

  /** Files a solver is expected to produce by the end of the task. */
  outputs: OutputConfig;
};

export type TaskProposal = {
  /** Clear task title. Replace bracketed starter text before running checks. */
  title: string;

  /** Prometheus challenge family. Setup refresh syncs this value to the submission. */
  family:
    | "paper_implementation"
    | "training_debugger"
    | "inference_optimizer"
    | "grader_forensics"
    | "dataset_forensics"
    | "synthetic_data"
    | "other_research_engineering";

  /** Primary source category used by idea and task-quality review. */
  sourceType:
    | "paper"
    | "public_repo"
    | "production_spec"
    | "private_project"
    | "internal_style_spec"
    | "other";

  /** Optional paper, issue, or design document URL. Leave it out when there is no source. */
  sourceUrl?: string;

  /** The complete submission idea: problem, motivation, and intended outcome. */
  idea: string;

  /** Expected solver experience. */
  expectedSkill: "intermediate" | "senior" | "staff" | "specialist";

  /** Expected time for a qualified solver. */
  expectedHorizon:
    | "two_hours"
    | "four_hours"
    | "eight_hours"
    | "one_day"
    | "two_days"
    | "forty_hours";
};

export type WorkspaceConfig = {
  /** Repository-relative workspace root. Use "." when the repo root is the task root. */
  root: ".";
};

export type ReviewConfig = {
  /** Private Markdown notes for reviewers. Keep this under privateFiles. */
  notes: string;
};

export type CommandConfig = {
  /** Public setup command that works from the repo root. */
  setup: string;

  /** Private verifier command that checks the final solver output. */
  verify: string;

  /** Private reference solution command. Usually applies .shipd/private/reference.patch. */
  applyReference: string;
};

export type RubricTree = {
  /** Human-readable root label for the rubric. */
  label: string;

  /** Total points available. Child points must add up to this value. */
  totalPoints: number;

  /** Top-level scoring criteria. */
  children: RubricNode[];
};

export type RubricNode = RubricBranch | RubricLeaf;

export type RubricBranch = {
  /** Human-readable criterion label. */
  label: string;

  /** Points available for this criterion. Children must add up to this value. */
  points: number;

  /** Child criteria that split this criterion's points. */
  children: RubricNode[];
};

export type RubricLeaf = {
  /** Human-readable scoring item. */
  label: string;

  /** Points available for this scoring item. */
  points: number;

  /** Use deterministic when verifier evidence can prove it, otherwise qualitative. */
  kind: "deterministic" | "qualitative";
};

export type OutputConfig = {
  /** Required output files produced by a solver or checked by the verifier. */
  required: string[];
};
