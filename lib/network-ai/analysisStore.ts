import { createHash, randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import type {
  AnalysisRecord,
  AnalysisSafety,
  AnalyzeReportOutput,
  DayResultKind
} from "./schemas";

const STORE_PATH =
  process.env.NETWORK_AI_ANALYSIS_STORE_PATH ??
  path.join(process.cwd(), "data", "network-ai", "analyses.json");

function ensureStoreDirectory() {
  mkdirSync(path.dirname(STORE_PATH), { recursive: true });
}

function readStore(): AnalysisRecord[] {
  if (!existsSync(STORE_PATH)) {
    return [];
  }

  try {
    const content = readFileSync(STORE_PATH, "utf8").trim();
    if (!content) {
      return [];
    }
    const parsed = JSON.parse(content) as unknown;
    return Array.isArray(parsed) ? (parsed as AnalysisRecord[]) : [];
  } catch {
    return [];
  }
}

function writeStore(records: AnalysisRecord[]) {
  ensureStoreDirectory();
  writeFileSync(STORE_PATH, `${JSON.stringify(records, null, 2)}\n`, "utf8");
}

function contextString(context: unknown, fields: string[]) {
  if (typeof context !== "object" || context === null || Array.isArray(context)) {
    return null;
  }

  const record = context as Record<string, unknown>;
  for (const field of fields) {
    const value = record[field];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return null;
}

function contextResultKind(context: unknown): DayResultKind {
  const resultKind = contextString(context, ["resultKind"]);
  if (
    resultKind === "device_report" ||
    resultKind === "phase_gate_report" ||
    resultKind === "summary_report" ||
    resultKind === "test_report" ||
    resultKind === "unknown"
  ) {
    return resultKind;
  }

  return "unknown";
}

export function hashAnalysisInput(reportText: string, deviceContext: unknown) {
  return createHash("sha256")
    .update(reportText)
    .update(JSON.stringify(deviceContext ?? null))
    .digest("hex");
}

export function createAnalysisRecord(input: {
  reportId: string;
  reportText: string;
  deviceContext?: unknown;
  model: string;
  promptVersion: string;
  output: AnalyzeReportOutput;
  safety: AnalysisSafety;
}) {
  const targetDevice = contextString(input.deviceContext, ["targetDevice", "deviceName"]);
  const record: AnalysisRecord = {
    id: `analysis_${randomUUID()}`,
    reportId: input.reportId,
    sourceDay: contextString(input.deviceContext, ["sourceDay"]),
    resultKind: contextResultKind(input.deviceContext),
    targetDevice: targetDevice && targetDevice.toUpperCase() !== "N/A" ? targetDevice : null,
    checkType: contextString(input.deviceContext, ["checkType"]),
    model: input.model,
    promptVersion: input.promptVersion,
    inputHash: hashAnalysisInput(input.reportText, input.deviceContext),
    output: input.output,
    safety: input.safety,
    createdAt: new Date().toISOString()
  };

  const records = readStore();
  records.push(record);
  writeStore(records);
  return record;
}

export function listAnalysesForReport(reportId: string) {
  return readStore()
    .filter((record) => record.reportId === reportId)
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt));
}

export function getLatestAnalysisForReport(reportId: string) {
  return listAnalysesForReport(reportId)[0] ?? null;
}

export function clearAnalysisStoreForTests() {
  writeStore([]);
}
