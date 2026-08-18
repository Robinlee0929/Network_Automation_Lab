import type { DayResultKind } from "@/lib/network-ai/schemas";

export type SafeRecordedStatus =
  | "PASS"
  | "WARN"
  | "FAIL"
  | "BLOCKED"
  | "REVIEW"
  | "UNKNOWN";

export type SafeTone = "success" | "warning" | "danger" | "neutral";

export type SafeEvidenceCategory =
  | "Device Check Report"
  | "Readiness Gate Review"
  | "Test Evidence"
  | "Project Summary"
  | "Uncategorized Evidence";

export type SafeEvidenceItem = {
  internalId: string;
  category: SafeEvidenceCategory;
  categoryRank: number;
  dayLabel: string;
  dayNumber: number;
  status: SafeRecordedStatus;
  statusTone: SafeTone;
  recordedDate: string;
  recordedTimestamp: number;
  malformed: boolean;
};

export type SafeCollectionState = "AVAILABLE" | "EMPTY" | "ERROR";

export type SafeEvidenceCollection = {
  state: SafeCollectionState;
  items: SafeEvidenceItem[];
  rejectedCount: number;
};

export type SafeAnalysisProjection =
  | { state: "EMPTY" | "REJECTED" }
  | {
      state: "AVAILABLE";
      risk: string;
      approvalFlag: string;
      humanReviewFlag: string;
      jobEligibility: string;
      recordedDate: string;
    };

export type SafeCatalogItem = {
  id: SafeActionId;
  label: string;
  reviewerCopy: string;
  readOnly: string;
  configurationCapability: string;
  risk: string;
};

export type SafeParseProjection =
  | { state: "EMPTY" }
  | { state: "REJECTED" }
  | {
      state: "AVAILABLE";
      intent: string;
      recommendation: string;
      missingFields: string[];
      risk: string;
      approvalFlag: string;
      safetyResult: string;
      jobEligibility: string;
      reason: string;
      recordedDate: string;
      safeOutcome: SafeOutcomeProjection;
    };

export type SafeOutcomeProjection =
  | {
      state: "READ_ONLY_RESULT";
      heading: "WAN/LAN Result";
      interfaces: [
        { role: "WAN"; name: "ether1"; status: "RUNNING" },
        { role: "LAN"; name: "bridge-lan"; status: "RUNNING" }
      ];
      source: "Deterministic synthetic Stage-0 data";
      syntheticLabel: "SYNTHETIC / DEMO / NON-LIVE";
      liveDeviceContacted: "NO";
    }
  | {
      state: "CONFIGURATION_PREVIEW_AVAILABLE";
      heading: "Configuration Guidance";
      vendor: "MikroTik";
      platform: "RouterOS 7";
      requestedChange: "ether2 → VLAN 20";
      preview: readonly string[];
      source: "SERVER-OWNED TEMPLATE";
      templateId: "routeros_bridge_access_vlan_v1";
      status: "PREVIEW ONLY";
      execution: "NOT EXECUTED";
      approval: "REQUIRED";
      safety: "BLOCKED";
      jobEligibility: "NO";
    }
  | {
      state: "CONFIGURATION_PREVIEW_UNAVAILABLE";
      heading: "Configuration Guidance";
      reason: "Missing required server-owned synthetic context";
      status: "PREVIEW ONLY";
      execution: "NOT EXECUTED";
      approval: "REQUIRED";
      safety: "BLOCKED";
      jobEligibility: "NO";
    }
  | {
      state: "BLOCKED_NO_OUTCOME";
      heading: "No Safe Outcome Available";
      reason: "No safe outcome is available for this request.";
      jobCreated: "NO";
      execution: "NOT EXECUTED";
    };

export type SafeJobProjection = {
  internalKey: string;
  visibleId: string;
  action: string;
  platform: string;
  status: string;
  reason: string;
  risk: string;
  approvalFlag: string;
  readOnly: string;
  recordedDate: string;
};

export type SafeJobsCollection = {
  state: SafeCollectionState;
  items: SafeJobProjection[];
  rejectedCount: number;
};

const categoryDefinitions: Record<
  DayResultKind,
  { label: SafeEvidenceCategory; rank: number }
> = {
  device_report: { label: "Device Check Report", rank: 1 },
  phase_gate_report: { label: "Readiness Gate Review", rank: 2 },
  test_report: { label: "Test Evidence", rank: 3 },
  summary_report: { label: "Project Summary", rank: 4 },
  unknown: { label: "Uncategorized Evidence", rank: 5 }
};

const safeActionDefinitions = {
  baseline_check: {
    label: "Baseline Check",
    reviewerCopy: "Static catalog reference · request and execution unavailable."
  },
  wan_lan_check: {
    label: "WAN/LAN Check",
    reviewerCopy: "Static catalog reference · device access unavailable."
  },
  interface_status_check: {
    label: "Interface Status Check",
    reviewerCopy: "Static catalog reference · request and execution unavailable."
  },
  backup_config: {
    label: "Backup Config",
    reviewerCopy: "Static catalog reference · configuration backup unavailable."
  },
  environment_check: {
    label: "Environment Check",
    reviewerCopy: "Static catalog reference · provider and execution unavailable."
  }
} as const;

export type SafeActionId = keyof typeof safeActionDefinitions;

const intentLabels: Record<string, string> = {
  run_check: "Recorded intent category: read-only check reference",
  analyze_report: "Recorded intent category: analysis reference",
  change_access_vlan: "Recorded intent category: configuration change reference · unavailable",
  update_description: "Recorded intent category: configuration change reference · unavailable",
  backup_config: "Recorded intent category: configuration backup reference · unavailable",
  troubleshooting: "Recorded intent category: troubleshooting reference",
  unknown: "Recorded intent category: UNKNOWN"
};

const missingFieldLabels: Record<string, string> = {
  targetDevice: "Target reference required",
  deviceInventoryMatch: "Inventory match required",
  recommendedActionId: "Catalog reference required",
  interfaceName: "Interface reference required",
  vlanId: "VLAN reference required"
};

const blockedReasonLabels: Record<string, string> = {
  "Target device not found in inventory or missing connection details":
    "Recorded reason: device readiness unavailable",
  "backup_config requires approval because it may expose sensitive configuration":
    "Recorded reason: configuration backup requires review",
  "Config change requires approval and is not executable in Phase 1":
    "Recorded reason: configuration change unavailable",
  "Unknown actionId": "Recorded reason: unknown action",
  "Missing targetDevice": "Recorded reason: missing target"
};

const safeJobKeys = new Set([
  "id",
  "actionId",
  "targetDevice",
  "vendor",
  "params",
  "status",
  "blockedReason",
  "riskLevel",
  "requiresApproval",
  "readOnly",
  "source",
  "parseResultId",
  "createdAt"
]);

const safeConfigurationPreview = [
  "/interface bridge port",
  'set [find where bridge="bridge-lan" and interface="ether2"] pvid=20 ingress-filtering=yes frame-types=admit-only-untagged-and-priority-tagged',
  "/interface bridge vlan",
  'add bridge="bridge-lan" vlan-ids=20 tagged="bridge-lan" untagged="ether2"'
] as const;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function hasExactKeys(value: Record<string, unknown>, expected: readonly string[]) {
  const keys = Object.keys(value);
  return keys.length === expected.length && keys.every((key) => expected.includes(key));
}

function hasExactPreview(value: unknown) {
  return (
    Array.isArray(value) &&
    value.length === safeConfigurationPreview.length &&
    value.every((line, index) => line === safeConfigurationPreview[index])
  );
}

function safeInternalId(value: unknown) {
  if (typeof value !== "string") {
    return null;
  }
  const trimmed = value.trim();
  return /^[a-zA-Z0-9._:-]{1,200}$/.test(trimmed) ? trimmed : null;
}

function safeCategory(value: unknown) {
  if (typeof value === "string" && value in categoryDefinitions) {
    return categoryDefinitions[value as DayResultKind];
  }
  return categoryDefinitions.unknown;
}

export function normalizeRecordedStatus(value: unknown): SafeRecordedStatus {
  if (typeof value !== "string") {
    return "UNKNOWN";
  }
  const normalized = value.trim().toLowerCase();
  if (normalized === "pass" || normalized === "success" || normalized === "ok") {
    return "PASS";
  }
  if (normalized === "warn" || normalized === "warning") {
    return "WARN";
  }
  if (normalized === "fail") {
    return "FAIL";
  }
  if (normalized === "block" || normalized === "blocked") {
    return "BLOCKED";
  }
  if (normalized === "review") {
    return "REVIEW";
  }
  return "UNKNOWN";
}

export function safeStatusTone(status: SafeRecordedStatus): SafeTone {
  if (status === "PASS") {
    return "success";
  }
  if (status === "WARN" || status === "REVIEW") {
    return "warning";
  }
  if (status === "FAIL" || status === "BLOCKED") {
    return "danger";
  }
  return "neutral";
}

export function normalizeSourceDay(value: unknown) {
  if (typeof value !== "string") {
    return { label: "Unspecified day", number: -1 };
  }
  const match = value.trim().match(/^day[-_ ]?([0-9]{1,3})$/i);
  if (!match) {
    return { label: "Unspecified day", number: -1 };
  }
  const number = Number(match[1]);
  return { label: `Day ${number}`, number };
}

export function normalizeRecordedDate(value: unknown) {
  if (typeof value !== "string") {
    return { label: "Unknown date", timestamp: Number.NEGATIVE_INFINITY };
  }
  const timestamp = Date.parse(value);
  if (!Number.isFinite(timestamp)) {
    return { label: "Unknown date", timestamp: Number.NEGATIVE_INFINITY };
  }
  return {
    label: new Date(timestamp).toISOString().slice(0, 10),
    timestamp
  };
}

function isExactParseWarning(value: unknown) {
  return (
    isRecord(value) &&
    value.parseWarning === "JSON report could not be parsed."
  );
}

function projectEvidenceItem(value: unknown): SafeEvidenceItem | null {
  if (!isRecord(value)) {
    return null;
  }
  const internalId = safeInternalId(value.id);
  if (!internalId) {
    return null;
  }
  const category = safeCategory(value.resultKind);
  const day = normalizeSourceDay(value.sourceDay);
  const status = normalizeRecordedStatus(value.status);
  const recorded = normalizeRecordedDate(value.createdAt);
  return {
    internalId,
    category: category.label,
    categoryRank: category.rank,
    dayLabel: day.label,
    dayNumber: day.number,
    status,
    statusTone: safeStatusTone(status),
    recordedDate: recorded.label,
    recordedTimestamp: recorded.timestamp,
    malformed: isExactParseWarning(value.parsedResult)
  };
}

export function projectEvidenceCollection(value: unknown): SafeEvidenceCollection {
  if (!Array.isArray(value)) {
    return { state: "ERROR", items: [], rejectedCount: 0 };
  }
  const projected = value.map(projectEvidenceItem);
  const items = projected.filter((item): item is SafeEvidenceItem => item !== null);
  const rejectedCount = value.length - items.length;
  items.sort((left, right) => {
    const categoryDelta = left.categoryRank - right.categoryRank;
    if (categoryDelta !== 0) {
      return categoryDelta;
    }
    const dayDelta = right.dayNumber - left.dayNumber;
    if (dayDelta !== 0) {
      return dayDelta;
    }
    const dateDelta = right.recordedTimestamp - left.recordedTimestamp;
    if (Number.isFinite(dateDelta) && dateDelta !== 0) {
      return dateDelta;
    }
    return left.internalId.localeCompare(right.internalId);
  });
  return {
    state: items.length ? "AVAILABLE" : value.length ? "ERROR" : "EMPTY",
    items,
    rejectedCount
  };
}

export function projectReportsCollection(value: unknown): SafeEvidenceCollection {
  return projectEvidenceCollection(value);
}

function riskLabel(value: unknown, prefix: string) {
  if (value === "low" || value === "medium" || value === "high") {
    return `${prefix}: ${value.toUpperCase()}`;
  }
  return `${prefix}: UNKNOWN`;
}

function booleanLabel(value: unknown) {
  if (value === true) {
    return "yes";
  }
  if (value === false) {
    return "no";
  }
  return "Unknown";
}

export function projectAnalysisRecord(value: unknown): SafeAnalysisProjection {
  if (value === null || value === undefined) {
    return { state: "EMPTY" };
  }
  if (!isRecord(value) || !isRecord(value.output) || !isRecord(value.safety)) {
    return { state: "REJECTED" };
  }
  const recorded = normalizeRecordedDate(value.createdAt);
  return {
    state: "AVAILABLE",
    risk: riskLabel(value.output.riskLevel, "Recorded risk"),
    approvalFlag: `Recorded approval flag: ${booleanLabel(value.output.requiresApproval)}`,
    humanReviewFlag: `Recorded human-review flag: ${booleanLabel(
      value.output.needsHumanReview
    )}`,
    jobEligibility: `Recorded job eligibility: ${booleanLabel(
      value.safety.jobCreationAllowed
    )} · job creation unavailable in Stage 0`,
    recordedDate: `Recorded analysis date: ${recorded.label}`
  };
}

function safeActionId(value: unknown): SafeActionId | null {
  return typeof value === "string" && value in safeActionDefinitions
    ? (value as SafeActionId)
    : null;
}

export function projectActionCatalog(value: unknown): SafeCatalogItem[] {
  if (!Array.isArray(value)) {
    return [];
  }
  const seen = new Set<SafeActionId>();
  const items: SafeCatalogItem[] = [];
  for (const candidate of value) {
    if (!isRecord(candidate)) {
      continue;
    }
    const id = safeActionId(candidate.id);
    if (!id || seen.has(id)) {
      continue;
    }
    seen.add(id);
    const definition = safeActionDefinitions[id];
    items.push({
      id,
      label: definition.label,
      reviewerCopy: definition.reviewerCopy,
      readOnly: `Catalog property: read-only ${booleanLabel(
        candidate.readOnly
      )} · execution unavailable`,
      configurationCapability: "Configuration-changing capability: unavailable",
      risk: riskLabel(candidate.riskLevel, "Catalog risk")
    });
  }
  return items;
}

function actionRecommendation(value: unknown) {
  if (value === null || value === undefined) {
    return "No recorded recommendation";
  }
  const id = safeActionId(value);
  return id
    ? `Recorded recommendation: ${safeActionDefinitions[id].label}`
    : "Unknown catalog reference";
}

function projectMissingFields(value: unknown) {
  if (!Array.isArray(value) || value.length === 0) {
    return ["No recorded missing-field flags"];
  }
  const labels: string[] = [];
  let unknownSeen = false;
  for (const field of value) {
    if (typeof field === "string" && field in missingFieldLabels) {
      const label = missingFieldLabels[field];
      if (!labels.includes(label)) {
        labels.push(label);
      }
    } else {
      unknownSeen = true;
    }
  }
  if (unknownSeen) {
    labels.push("Other required information withheld");
  }
  return labels.length ? labels : ["No recorded missing-field flags"];
}

function reasonLabel(value: unknown) {
  if (value === null || value === undefined || value === "") {
    return "No recorded reason";
  }
  return typeof value === "string" && value in blockedReasonLabels
    ? blockedReasonLabels[value]
    : "Recorded reason withheld";
}

function blockedNoOutcomeProjection(): SafeOutcomeProjection {
  return {
    state: "BLOCKED_NO_OUTCOME",
    heading: "No Safe Outcome Available",
    reason: "No safe outcome is available for this request.",
    jobCreated: "NO",
    execution: "NOT EXECUTED"
  };
}

export function projectSafeOutcome(value: unknown): SafeOutcomeProjection {
  if (!isRecord(value) || typeof value.type !== "string") {
    return blockedNoOutcomeProjection();
  }

  if (
    value.type === "READ_ONLY_RESULT" &&
    hasExactKeys(value, [
      "type",
      "title",
      "interfaces",
      "source",
      "synthetic",
      "liveDeviceContacted"
    ]) &&
    value.title === "WAN/LAN Check Result" &&
    value.source === "Deterministic synthetic Stage-0 data" &&
    value.synthetic === true &&
    value.liveDeviceContacted === false &&
    Array.isArray(value.interfaces) &&
    value.interfaces.length === 2
  ) {
    const [wan, lan] = value.interfaces;
    if (
      isRecord(wan) &&
      hasExactKeys(wan, ["role", "name", "status"]) &&
      wan.role === "WAN" &&
      wan.name === "ether1" &&
      wan.status === "RUNNING" &&
      isRecord(lan) &&
      hasExactKeys(lan, ["role", "name", "status"]) &&
      lan.role === "LAN" &&
      lan.name === "bridge-lan" &&
      lan.status === "RUNNING"
    ) {
      return {
        state: "READ_ONLY_RESULT",
        heading: "WAN/LAN Result",
        interfaces: [
          { role: "WAN", name: "ether1", status: "RUNNING" },
          { role: "LAN", name: "bridge-lan", status: "RUNNING" }
        ],
        source: "Deterministic synthetic Stage-0 data",
        syntheticLabel: "SYNTHETIC / DEMO / NON-LIVE",
        liveDeviceContacted: "NO"
      };
    }
  }

  if (value.type === "CONFIGURATION_PREVIEW" && value.state === "AVAILABLE") {
    if (
      hasExactKeys(value, [
        "type",
        "state",
        "vendor",
        "platform",
        "requestedChange",
        "preview",
        "source",
        "templateId",
        "previewOnly",
        "executed",
        "approvalRequired",
        "safety",
        "jobEligible"
      ]) &&
      value.vendor === "MikroTik" &&
      value.platform === "RouterOS 7" &&
      value.requestedChange === "ether2 → VLAN 20" &&
      hasExactPreview(value.preview) &&
      value.source === "SERVER-OWNED TEMPLATE" &&
      value.templateId === "routeros_bridge_access_vlan_v1" &&
      value.previewOnly === true &&
      value.executed === false &&
      value.approvalRequired === true &&
      value.safety === "BLOCKED" &&
      value.jobEligible === false
    ) {
      return {
        state: "CONFIGURATION_PREVIEW_AVAILABLE",
        heading: "Configuration Guidance",
        vendor: "MikroTik",
        platform: "RouterOS 7",
        requestedChange: "ether2 → VLAN 20",
        preview: safeConfigurationPreview,
        source: "SERVER-OWNED TEMPLATE",
        templateId: "routeros_bridge_access_vlan_v1",
        status: "PREVIEW ONLY",
        execution: "NOT EXECUTED",
        approval: "REQUIRED",
        safety: "BLOCKED",
        jobEligibility: "NO"
      };
    }
  }

  if (
    value.type === "CONFIGURATION_PREVIEW" &&
    value.state === "UNAVAILABLE" &&
    hasExactKeys(value, [
      "type",
      "state",
      "reason",
      "previewOnly",
      "executed",
      "approvalRequired",
      "safety",
      "jobEligible"
    ]) &&
    value.reason === "Missing required server-owned synthetic context" &&
    value.previewOnly === true &&
    value.executed === false &&
    value.approvalRequired === true &&
    value.safety === "BLOCKED" &&
    value.jobEligible === false
  ) {
    return {
      state: "CONFIGURATION_PREVIEW_UNAVAILABLE",
      heading: "Configuration Guidance",
      reason: "Missing required server-owned synthetic context",
      status: "PREVIEW ONLY",
      execution: "NOT EXECUTED",
      approval: "REQUIRED",
      safety: "BLOCKED",
      jobEligibility: "NO"
    };
  }

  if (
    value.type === "BLOCKED_NO_OUTCOME" &&
    hasExactKeys(value, ["type", "reason", "jobCreated", "executed"]) &&
    value.reason === "No safe outcome is available for this request." &&
    value.jobCreated === false &&
    value.executed === false
  ) {
    return blockedNoOutcomeProjection();
  }

  return blockedNoOutcomeProjection();
}

export function projectParseResult(value: unknown): SafeParseProjection {
  if (value === null || value === undefined) {
    return { state: "EMPTY" };
  }
  if (!isRecord(value) || !isRecord(value.output)) {
    return { state: "REJECTED" };
  }
  const output = value.output;
  const recorded = normalizeRecordedDate(value.createdAt);
  const intent =
    typeof output.intent === "string" && output.intent in intentLabels
      ? intentLabels[output.intent]
      : "Recorded intent category: UNKNOWN";
  const blocked =
    output.blocked === true
      ? "Recorded safety result: BLOCKED · non-executing"
      : output.blocked === false
        ? "Recorded safety result: NOT BLOCKED · non-executing"
        : "Recorded safety result: UNKNOWN · non-executing";
  return {
    state: "AVAILABLE",
    intent,
    recommendation: actionRecommendation(output.recommendedActionId),
    missingFields: projectMissingFields(output.missingFields),
    risk: riskLabel(output.riskLevel, "Recorded risk"),
    approvalFlag: `Recorded approval flag: ${booleanLabel(output.requiresApproval)}`,
    safetyResult: blocked,
    jobEligibility: `Recorded eligibility: ${booleanLabel(
      output.jobCreationAllowed
    )} · job creation unavailable in Stage 0`,
    reason: reasonLabel(output.blockedReason),
    recordedDate: `Recorded parse date: ${recorded.label}`,
    safeOutcome: projectSafeOutcome(value.safeOutcome)
  };
}

function safeJobStatus(value: unknown) {
  if (value === "ready") {
    return "RECORDED / NEVER EXECUTED";
  }
  if (value === "pending_approval") {
    return "RECORDED / APPROVAL UNAVAILABLE";
  }
  if (value === "blocked") {
    return "RECORDED / BLOCKED";
  }
  return "REJECTED";
}

function safePlatform(value: unknown) {
  if (value === "mikrotik") {
    return "Recorded device platform: MikroTik";
  }
  if (value === "cisco") {
    return "Recorded device platform: Cisco";
  }
  return "Recorded device platform: Unknown";
}

function hasOnlySafeJobKeys(value: Record<string, unknown>) {
  return Object.keys(value).every((key) => safeJobKeys.has(key));
}

function projectJob(value: unknown, index: number): SafeJobProjection | null {
  if (!isRecord(value) || !hasOnlySafeJobKeys(value)) {
    return null;
  }
  if (
    typeof value.id !== "string" ||
    !value.id.trim() ||
    typeof value.actionId !== "string" ||
    !isRecord(value.params) ||
    typeof value.status !== "string" ||
    typeof value.riskLevel !== "string" ||
    typeof value.requiresApproval !== "boolean" ||
    typeof value.readOnly !== "boolean" ||
    typeof value.createdAt !== "string"
  ) {
    return null;
  }
  const actionId = safeActionId(value.actionId);
  const recorded = normalizeRecordedDate(value.createdAt);
  const validJobId =
    value.id.length <= 50 &&
    /^job_[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(
      value.id
    );
  return {
    internalKey: `recorded-job-${index}`,
    visibleId: validJobId ? value.id : "Identifier withheld",
    action: actionId
      ? safeActionDefinitions[actionId].label
      : "Unknown catalog reference",
    platform: safePlatform(value.vendor),
    status: safeJobStatus(value.status),
    reason: reasonLabel(value.blockedReason),
    risk: riskLabel(value.riskLevel, "Recorded risk"),
    approvalFlag: `Recorded approval flag: ${booleanLabel(value.requiresApproval)}`,
    readOnly: `Recorded catalog property: read-only ${booleanLabel(
      value.readOnly
    )} · execution unavailable`,
    recordedDate: `Recorded: ${recorded.label}`
  };
}

export function projectJobsCollection(value: unknown): SafeJobsCollection {
  if (!Array.isArray(value)) {
    return { state: "ERROR", items: [], rejectedCount: 0 };
  }
  const projected = value.map(projectJob);
  const items = projected.filter((item): item is SafeJobProjection => item !== null);
  return {
    state: items.length ? "AVAILABLE" : value.length ? "ERROR" : "EMPTY",
    items,
    rejectedCount: value.length - items.length
  };
}
