export const NETWORK_AI_DRAFT_NOTICE =
  "AI Network Automation Node output. Review before creating or approving any job.";

export const riskLevels = ["low", "medium", "high"] as const;
export const vendors = ["mikrotik", "cisco", "unknown"] as const;
export const dayResultKinds = [
  "device_report",
  "phase_gate_report",
  "summary_report",
  "test_report",
  "unknown"
] as const;
export const networkIntents = [
  "run_check",
  "analyze_report",
  "change_access_vlan",
  "update_description",
  "backup_config",
  "troubleshooting",
  "unknown"
] as const;

export type RiskLevel = (typeof riskLevels)[number];
export type Vendor = (typeof vendors)[number];
export type DayResultKind = (typeof dayResultKinds)[number];
export type NetworkIntent = (typeof networkIntents)[number];

export type AvailableAction = {
  id: string;
  label: string;
  description: string;
  checkType: string;
  readOnly: boolean;
  configChange: boolean;
  riskLevel: RiskLevel;
  allowedVendors: Vendor[];
};

export type DayResult = {
  id: string;
  sourceDay: string | null;
  dayLabel: string;
  resultKind: DayResultKind;
  deviceName: string | null;
  reportTitle: string | null;
  vendor: Vendor;
  checkType: string;
  status: string;
  rawOutput: string;
  parsedResult: unknown;
  createdAt: string;
  sourcePath: string;
};

export type AnalyzeReportOutput = {
  summary: string;
  findings: string[];
  warnings: string[];
  possibleCauses: string[];
  recommendedActions: string[];
  recommendedExistingActionIds: string[];
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  needsHumanReview: boolean;
};

export type AnalysisSafety = {
  recommendedActionIdsSanitized: boolean;
  jobCreationAllowed: boolean;
  reason: string | null;
};

export type AnalysisRecord = {
  id: string;
  reportId: string;
  sourceDay: string | null;
  resultKind: DayResultKind;
  targetDevice: string | null;
  checkType: string | null;
  model: string;
  promptVersion: string;
  inputHash: string;
  output: AnalyzeReportOutput;
  safety: AnalysisSafety;
  createdAt: string;
};

export type ParseRequestOutput = {
  intent: NetworkIntent;
  targetDevice: string | null;
  vendor: Vendor;
  interfaceName: string | null;
  vlanId: number | null;
  recommendedActionId: string | null;
  missingFields: string[];
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  blocked: boolean;
  jobCreationAllowed: boolean;
  blockedReason: string | null;
  notes: string[];
};

export type NetworkJob = {
  id: string;
  actionId: string;
  targetDevice: string | null;
  vendor?: Vendor;
  params: Record<string, unknown>;
  status: "ready" | "pending_approval" | "blocked";
  blockedReason?: string;
  riskLevel: RiskLevel;
  requiresApproval: boolean;
  readOnly: boolean;
  source?: string | null;
  parseResultId?: string | null;
  createdAt: string;
};

export type ParseResultRecord = {
  id: string;
  userRequest: string;
  deviceInventoryHash: string;
  deviceInventorySnapshot: Record<string, unknown> | null;
  output: ParseRequestOutput;
  createdAt: string;
};

type ValidationResult<T> =
  | {
      ok: true;
      value: T;
    }
  | {
      ok: false;
      error: string;
    };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function enumValue<TValue extends string>(
  value: unknown,
  allowed: readonly TValue[]
): value is TValue {
  return typeof value === "string" && allowed.includes(value as TValue);
}

export const analyzeReportOutputJsonSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "summary",
    "findings",
    "warnings",
    "possibleCauses",
    "recommendedActions",
    "recommendedExistingActionIds",
    "riskLevel",
    "requiresApproval",
    "needsHumanReview"
  ],
  properties: {
    summary: { type: "string" },
    findings: { type: "array", items: { type: "string" } },
    warnings: { type: "array", items: { type: "string" } },
    possibleCauses: { type: "array", items: { type: "string" } },
    recommendedActions: { type: "array", items: { type: "string" } },
    recommendedExistingActionIds: { type: "array", items: { type: "string" } },
    riskLevel: { type: "string", enum: riskLevels },
    requiresApproval: { type: "boolean" },
    needsHumanReview: { type: "boolean" }
  }
} as const;

export const parseRequestOutputJsonSchema = {
  type: "object",
  additionalProperties: false,
  required: [
    "intent",
    "targetDevice",
    "vendor",
    "interfaceName",
    "vlanId",
    "recommendedActionId",
    "missingFields",
    "riskLevel",
    "requiresApproval",
    "blocked",
    "jobCreationAllowed",
    "blockedReason",
    "notes"
  ],
  properties: {
    intent: { type: "string", enum: networkIntents },
    targetDevice: { type: ["string", "null"] },
    vendor: { type: "string", enum: vendors },
    interfaceName: { type: ["string", "null"] },
    vlanId: { type: ["number", "null"] },
    recommendedActionId: { type: ["string", "null"] },
    missingFields: { type: "array", items: { type: "string" } },
    riskLevel: { type: "string", enum: riskLevels },
    requiresApproval: { type: "boolean" },
    blocked: { type: "boolean" },
    jobCreationAllowed: { type: "boolean" },
    blockedReason: { type: ["string", "null"] },
    notes: { type: "array", items: { type: "string" } }
  }
} as const;

export function validateAnalyzeReportOutput(value: unknown): ValidationResult<AnalyzeReportOutput> {
  if (!isRecord(value)) {
    return { ok: false, error: "AI report analyzer output must be a JSON object." };
  }

  const requiredArrays = [
    "findings",
    "warnings",
    "possibleCauses",
    "recommendedActions",
    "recommendedExistingActionIds"
  ];

  for (const field of requiredArrays) {
    if (!stringArray(value[field])) {
      return { ok: false, error: `AI report analyzer field '${field}' must be a string array.` };
    }
  }

  if (
    typeof value.summary !== "string" ||
    !enumValue(value.riskLevel, riskLevels) ||
    typeof value.requiresApproval !== "boolean" ||
    typeof value.needsHumanReview !== "boolean"
  ) {
    return { ok: false, error: "AI report analyzer output failed JSON Schema validation." };
  }

  return { ok: true, value: value as AnalyzeReportOutput };
}

export function validateParseRequestOutput(value: unknown): ValidationResult<ParseRequestOutput> {
  if (!isRecord(value)) {
    return { ok: false, error: "AI request parser output must be a JSON object." };
  }

  const nullableStrings = ["targetDevice", "interfaceName", "recommendedActionId"];
  for (const field of nullableStrings) {
    const fieldValue = value[field];
    if (fieldValue !== null && typeof fieldValue !== "string") {
      return { ok: false, error: `AI request parser field '${field}' must be string or null.` };
    }
  }

  if (
    !enumValue(value.intent, networkIntents) ||
    !enumValue(value.vendor, vendors) ||
    !enumValue(value.riskLevel, riskLevels) ||
    !stringArray(value.missingFields) ||
    !stringArray(value.notes) ||
    typeof value.requiresApproval !== "boolean" ||
    typeof value.blocked !== "boolean" ||
    typeof value.jobCreationAllowed !== "boolean" ||
    (value.blockedReason !== null && typeof value.blockedReason !== "string")
  ) {
    return { ok: false, error: "AI request parser output failed JSON Schema validation." };
  }

  if (value.vlanId !== null && typeof value.vlanId !== "number") {
    return { ok: false, error: "AI request parser field 'vlanId' must be number or null." };
  }

  return { ok: true, value: value as ParseRequestOutput };
}
