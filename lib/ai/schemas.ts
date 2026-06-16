export type AiNodeResponse<TOutput> = {
  nodeType: string;
  draftNotice: string;
  model: string;
  output: TOutput;
  rawJson: string;
};

export type MeetingSummaryTask = {
  title: string;
  owner: string;
  dueDate: string;
  status: string;
};

export type MeetingSummaryNodeOutput = {
  summary: string;
  decisions: string[];
  tasks: MeetingSummaryTask[];
  risks: string[];
  followUpQuestions: string[];
  needsHumanReview: boolean;
};

export type RequirementAnalysisNodeOutput = {
  summary: string;
  modules: string[];
  userStories: string[];
  acceptanceCriteria: string[];
  missingInfo: string[];
  priority: "High" | "Medium" | "Low" | string;
  risks: string[];
  needsHumanReview: boolean;
};

export type KnowledgeQaNodeOutput = {
  answer: string;
  evidence: string[];
  insufficientInfo: boolean;
  suggestedNextStep: string;
  needsHumanReview: boolean;
};

export function ensureHumanReview<TOutput extends { needsHumanReview: boolean }>(
  output: TOutput
): TOutput {
  return {
    ...output,
    needsHumanReview: true
  };
}
