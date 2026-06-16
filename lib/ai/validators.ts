export const MAX_INPUT_CHARS = 20000;

export type ValidationResult =
  | { ok: true }
  | {
      ok: false;
      error: string;
    };

export function validateRequiredText(value: unknown, fieldLabel: string): ValidationResult {
  if (typeof value !== "string" || value.trim().length === 0) {
    return { ok: false, error: `${fieldLabel}不可為空。` };
  }

  if (value.length > MAX_INPUT_CHARS) {
    return {
      ok: false,
      error: `${fieldLabel}不可超過 ${MAX_INPUT_CHARS.toLocaleString()} characters。`
    };
  }

  return { ok: true };
}

export function validateMeetingPayload(body: unknown): ValidationResult {
  if (!body || typeof body !== "object") {
    return { ok: false, error: "請提供會議內容。" };
  }

  return validateRequiredText((body as { content?: unknown }).content, "會議內容");
}

export function validateRequirementPayload(body: unknown): ValidationResult {
  if (!body || typeof body !== "object") {
    return { ok: false, error: "請提供原始需求。" };
  }

  return validateRequiredText((body as { content?: unknown }).content, "原始需求");
}

export function validateKnowledgePayload(body: unknown): ValidationResult {
  if (!body || typeof body !== "object") {
    return { ok: false, error: "請提供文件內容與問題。" };
  }

  const payload = body as { document?: unknown; question?: unknown };
  const documentResult = validateRequiredText(payload.document, "文件內容");
  if (!documentResult.ok) {
    return documentResult;
  }

  return validateRequiredText(payload.question, "使用者問題");
}

export function validateAutomationMeetingPayload(body: unknown): ValidationResult {
  if (!body || typeof body !== "object") {
    return { ok: false, error: "請提供 meetingText。" };
  }

  return validateRequiredText((body as { meetingText?: unknown }).meetingText, "meetingText");
}

export function validateAutomationRequirementPayload(body: unknown): ValidationResult {
  if (!body || typeof body !== "object") {
    return { ok: false, error: "請提供 requirementText。" };
  }

  return validateRequiredText((body as { requirementText?: unknown }).requirementText, "requirementText");
}

export function validateAutomationKnowledgePayload(body: unknown): ValidationResult {
  if (!body || typeof body !== "object") {
    return { ok: false, error: "請提供 documentText 與 question。" };
  }

  const payload = body as { documentText?: unknown; question?: unknown };
  const documentResult = validateRequiredText(payload.documentText, "documentText");
  if (!documentResult.ok) {
    return documentResult;
  }

  return validateRequiredText(payload.question, "question");
}
