import { getOpenAIClient, getOpenAIModel } from "@/lib/ai/openaiClient";
import { getAvailableActions, isAvailableActionId } from "./actions";
import { sanitizeParseRequestResult } from "./readiness";
import {
  NETWORK_AI_DRAFT_NOTICE,
  type AnalysisSafety,
  type AnalyzeReportOutput,
  type DayResultKind,
  analyzeReportOutputJsonSchema,
  parseRequestOutputJsonSchema,
  validateAnalyzeReportOutput,
  validateParseRequestOutput
} from "./schemas";

export const NETWORK_ANALYZE_PROMPT_VERSION = "network-analyze-report-v2";

function extractJsonObject(text: string) {
  const trimmed = text.trim();
  const fencedMatch = trimmed.match(/^```(?:json)?\s*([\s\S]*?)\s*```$/i);
  if (fencedMatch) {
    return fencedMatch[1].trim();
  }

  const firstBrace = trimmed.indexOf("{");
  const lastBrace = trimmed.lastIndexOf("}");
  if (firstBrace >= 0 && lastBrace > firstBrace) {
    return trimmed.slice(firstBrace, lastBrace + 1);
  }

  return trimmed;
}

async function generateNetworkJson(systemPrompt: string, userPayload: unknown) {
  const client = getOpenAIClient();
  const model = getOpenAIModel();
  const response = await client.responses.create({
    model,
    input: [
      { role: "system", content: systemPrompt },
      { role: "user", content: JSON.stringify(userPayload, null, 2) }
    ]
  });

  const text = response.output_text?.trim();
  if (!text) {
    throw new Error("OpenAI response did not include JSON output.");
  }

  const rawJson = extractJsonObject(text);
  try {
    return {
      model,
      rawJson,
      parsed: JSON.parse(rawJson) as unknown
    };
  } catch {
    throw new Error("OpenAI response was not valid JSON.");
  }
}

function normalizeActionIds(actionIds: string[]) {
  return actionIds.filter(isAvailableActionId);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function contextString(context: unknown, fields: string[]) {
  if (!isRecord(context)) {
    return null;
  }

  for (const field of fields) {
    const value = context[field];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return null;
}

function analyzeContext(input: unknown) {
  const resultKind = contextString(input, ["resultKind"]) as DayResultKind | null;
  const targetDevice = contextString(input, ["targetDevice", "deviceName"]);
  const hasTargetDevice = Boolean(targetDevice && targetDevice.toUpperCase() !== "N/A");

  return {
    resultKind,
    targetDevice,
    isDeviceReport: resultKind === "device_report",
    hasTargetDevice
  };
}

function withParseReadinessDefaults(value: unknown) {
  if (!isRecord(value)) {
    return value;
  }

  return {
    jobCreationAllowed: false,
    blockedReason: null,
    ...value
  };
}

export const NON_DEVICE_ACTION_WARNING =
  "Non-device report or missing target device: existing automation actionIds were removed and job creation is not allowed.";

export function sanitizeAnalyzeReportResult(
  output: AnalyzeReportOutput,
  deviceContext?: unknown
): {
  output: AnalyzeReportOutput;
  safety: AnalysisSafety;
} {
  const context = analyzeContext(deviceContext);
  const recommendedExistingActionIds = normalizeActionIds(output.recommendedExistingActionIds);
  const riskLevel = output.riskLevel;
  const riskRequiresApproval = riskLevel === "medium" || riskLevel === "high";
  const mustRemoveActions = !context.isDeviceReport || !context.hasTargetDevice;
  const hadRemovedActionIds =
    output.recommendedExistingActionIds.length !== recommendedExistingActionIds.length;
  const warnings = [...output.warnings];

  if (mustRemoveActions && !warnings.includes(NON_DEVICE_ACTION_WARNING)) {
    warnings.push(NON_DEVICE_ACTION_WARNING);
  }

  const sanitizedOutput = {
    ...output,
    warnings,
    recommendedExistingActionIds: mustRemoveActions ? [] : recommendedExistingActionIds,
    requiresApproval: output.requiresApproval || riskRequiresApproval,
    needsHumanReview: true
  };

  return {
    output: sanitizedOutput,
    safety: {
      recommendedActionIdsSanitized: mustRemoveActions || hadRemovedActionIds,
      jobCreationAllowed: context.isDeviceReport && context.hasTargetDevice,
      reason: mustRemoveActions ? NON_DEVICE_ACTION_WARNING : null
    }
  };
}

export function sanitizeAnalyzeReportOutput(
  output: AnalyzeReportOutput,
  deviceContext?: unknown
): AnalyzeReportOutput {
  return sanitizeAnalyzeReportResult(output, deviceContext).output;
}

export async function analyzeReportWithAi(input: {
  reportText: string;
  deviceContext?: unknown;
}) {
  const actions = getAvailableActions();
  const systemPrompt = [
    "You are a Network Automation AI Node for a Router/Switch automation platform.",
    "You analyze existing report evidence and return only one JSON object.",
    "Do not produce CLI commands. Do not claim to execute SSH, API calls, or device operations.",
    "Recommend only action IDs from the availableActions list. If none match, use an empty recommendedExistingActionIds array.",
    "recommendedExistingActionIds only means existing action IDs that may be converted into platform jobs.",
    "If reportKind/resultKind is not device_report, do not fill recommendedExistingActionIds.",
    "If targetDevice/deviceName is unknown, null, empty, or N/A, do not fill recommendedExistingActionIds.",
    "phase_gate_report, summary_report, and test_report may only receive reviewer recommendations, not executable action IDs.",
    "Configuration-changing work must require approval. Read-only checks may be low risk.",
    `Output JSON Schema: ${JSON.stringify(analyzeReportOutputJsonSchema)}`
  ].join("\n");

  const generated = await generateNetworkJson(systemPrompt, {
    reportText: input.reportText,
    deviceContext: input.deviceContext ?? null,
    availableActions: actions
  });

  const validation = validateAnalyzeReportOutput(generated.parsed);
  if (!validation.ok) {
    throw new Error(validation.error);
  }

  const sanitized = sanitizeAnalyzeReportResult(validation.value, input.deviceContext);
  return {
    nodeType: "network_report_analyzer",
    draftNotice: NETWORK_AI_DRAFT_NOTICE,
    model: generated.model,
    promptVersion: NETWORK_ANALYZE_PROMPT_VERSION,
    output: sanitized.output,
    safety: sanitized.safety,
    rawJson: JSON.stringify(sanitized.output, null, 2)
  };
}

export async function parseNetworkRequestWithAi(input: {
  userRequest: string;
  deviceInventory?: unknown;
}) {
  const actions = getAvailableActions();
  const systemPrompt = [
    "You are a Network Automation AI Node that parses requests into structured platform intent.",
    "Return only one JSON object and never execute, simulate execution, or generate arbitrary CLI commands.",
    "recommendedActionId must be exactly one ID from availableActions or null.",
    "Do not add generic missing fields such as evidence. Required fields are action-specific.",
    "baseline_check, wan_lan_check, and environment_check require targetDevice and inventory/connection readiness only; they do not require interfaceName, vlanId, or evidence.",
    "interface_status_check requires interfaceName only when the user explicitly names a specific port or interface.",
    "change_access_vlan requires targetDevice, interfaceName, vlanId, and inventory match.",
    "backup_config requires approval because it may expose sensitive configuration.",
    "Return jobCreationAllowed and blockedReason, but the server will validate them again.",
    "Config changes such as VLAN changes and interface descriptions must set requiresApproval true.",
    "If no safe matching action exists, use intent unknown when appropriate, recommendedActionId null, and blocked true.",
    `Output JSON Schema: ${JSON.stringify(parseRequestOutputJsonSchema)}`
  ].join("\n");

  const generated = await generateNetworkJson(systemPrompt, {
    userRequest: input.userRequest,
    deviceInventory: input.deviceInventory ?? null,
    availableActions: actions
  });

  const validation = validateParseRequestOutput(withParseReadinessDefaults(generated.parsed));
  if (!validation.ok) {
    throw new Error(validation.error);
  }

  const output = sanitizeParseRequestResult({
    output: validation.value,
    userRequest: input.userRequest,
    deviceInventory: input.deviceInventory
  });
  return {
    nodeType: "network_request_parser",
    draftNotice: NETWORK_AI_DRAFT_NOTICE,
    model: generated.model,
    output,
    rawJson: JSON.stringify(output, null, 2)
  };
}
