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
  priority: "High" | "Medium" | "Low";
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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(value: Record<string, unknown>, allowedKeys: readonly string[]) {
  const actualKeys = Object.keys(value);
  return (
    actualKeys.length === allowedKeys.length &&
    actualKeys.every((key) => allowedKeys.includes(key))
  );
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isMeetingSummaryTask(value: unknown): value is MeetingSummaryTask {
  return (
    isRecord(value) &&
    hasExactKeys(value, ["title", "owner", "dueDate", "status"]) &&
    typeof value.title === "string" &&
    typeof value.owner === "string" &&
    typeof value.dueDate === "string" &&
    typeof value.status === "string"
  );
}

function validateMeetingSummaryOutput(value: unknown): value is MeetingSummaryNodeOutput {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "summary",
      "decisions",
      "tasks",
      "risks",
      "followUpQuestions",
      "needsHumanReview"
    ]) &&
    typeof value.summary === "string" &&
    isStringArray(value.decisions) &&
    Array.isArray(value.tasks) &&
    value.tasks.every(isMeetingSummaryTask) &&
    isStringArray(value.risks) &&
    isStringArray(value.followUpQuestions) &&
    typeof value.needsHumanReview === "boolean"
  );
}

function validateRequirementAnalysisOutput(
  value: unknown
): value is RequirementAnalysisNodeOutput {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "summary",
      "modules",
      "userStories",
      "acceptanceCriteria",
      "missingInfo",
      "priority",
      "risks",
      "needsHumanReview"
    ]) &&
    typeof value.summary === "string" &&
    isStringArray(value.modules) &&
    isStringArray(value.userStories) &&
    isStringArray(value.acceptanceCriteria) &&
    isStringArray(value.missingInfo) &&
    ["High", "Medium", "Low"].includes(value.priority as string) &&
    isStringArray(value.risks) &&
    typeof value.needsHumanReview === "boolean"
  );
}

function validateKnowledgeQaOutput(value: unknown): value is KnowledgeQaNodeOutput {
  return (
    isRecord(value) &&
    hasExactKeys(value, [
      "answer",
      "evidence",
      "insufficientInfo",
      "suggestedNextStep",
      "needsHumanReview"
    ]) &&
    typeof value.answer === "string" &&
    isStringArray(value.evidence) &&
    typeof value.insufficientInfo === "boolean" &&
    typeof value.suggestedNextStep === "string" &&
    typeof value.needsHumanReview === "boolean"
  );
}

export function validateAiNodeOutput<TOutput extends { needsHumanReview: boolean }>(
  nodeType: string,
  value: unknown
): TOutput {
  const valid =
    (nodeType === "MeetingSummaryNode" && validateMeetingSummaryOutput(value)) ||
    (nodeType === "RequirementAnalysisNode" && validateRequirementAnalysisOutput(value)) ||
    (nodeType === "KnowledgeQaNode" && validateKnowledgeQaOutput(value));

  if (!valid) {
    throw new Error("AI node output failed strict schema validation.");
  }

  return value as unknown as TOutput;
}
