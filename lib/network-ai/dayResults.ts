import { createHash } from "node:crypto";
import { existsSync, readdirSync, readFileSync, statSync } from "node:fs";
import path from "node:path";
import type { DayResult, DayResultKind, Vendor } from "./schemas";

const REPORT_DIRS = ["reports", "summary"];
const SUPPORTED_EXTENSIONS = new Set([".json", ".txt"]);

function workspacePath(...segments: string[]) {
  return path.join(process.cwd(), ...segments);
}

function walkFiles(directory: string): string[] {
  if (!existsSync(directory)) {
    return [];
  }

  const entries = readdirSync(directory, { withFileTypes: true });
  return entries.flatMap((entry) => {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      return walkFiles(fullPath);
    }
    return [fullPath];
  });
}

function hashId(value: string) {
  return createHash("sha256").update(value).digest("hex").slice(0, 16);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringField(record: Record<string, unknown>, fields: string[]) {
  for (const field of fields) {
    const value = record[field];
    if (typeof value === "string" && value.trim()) {
      return value.trim();
    }
  }

  return null;
}

function inferSourceDay(filePath: string, raw: unknown): string | null {
  const record = isRecord(raw) ? raw : {};
  const explicitDay = stringField(record, ["sourceDay", "day_id", "dayId"]);
  if (explicitDay) {
    return explicitDay;
  }

  if (typeof record.day === "number" && Number.isFinite(record.day)) {
    return `Day${record.day}`;
  }

  const fromPath = filePath.match(/day[_-]?(\d{1,3})/i);
  if (fromPath) {
    return `Day${fromPath[1]}`;
  }

  return null;
}

function normalizeVendor(value: string): Vendor {
  const normalized = value.toLowerCase();
  if (normalized.includes("mikrotik") || normalized.includes("routeros")) {
    return "mikrotik";
  }
  if (normalized.includes("cisco") || normalized === "ios" || normalized.includes("cisco ios")) {
    return "cisco";
  }
  return "unknown";
}

function inferVendor(text: string, raw: unknown): Vendor {
  const record = isRecord(raw) ? raw : {};
  const explicitVendor = stringField(record, ["vendor", "platformVendor", "osVendor"]);
  if (explicitVendor) {
    return normalizeVendor(explicitVendor);
  }

  const haystack = `${text} ${JSON.stringify(raw ?? {})}`.toLowerCase();
  if (haystack.includes("mikrotik") || haystack.includes("routeros")) {
    return "mikrotik";
  }
  if (haystack.includes("cisco") || haystack.includes("ios")) {
    return "cisco";
  }
  return "unknown";
}

function inferReportTitle(filePath: string, raw: unknown) {
  const record = isRecord(raw) ? raw : {};
  const title = stringField(record, ["title", "task", "phase", "check", "type", "reportType"]);
  if (title) {
    return title;
  }

  const baseName = path.basename(filePath, path.extname(filePath));
  return baseName || null;
}

function hasExplicitDeviceIdentity(raw: unknown, vendor: Vendor) {
  if (!isRecord(raw)) {
    return false;
  }

  return Boolean(
    stringField(raw, ["deviceName", "device", "hostname", "targetDevice"]) || vendor !== "unknown"
  );
}

function inferResultKind(filePath: string, raw: unknown, vendor: Vendor): DayResultKind {
  const record = isRecord(raw) ? raw : {};
  const pathDescriptor = filePath
    .split(/[\\/]/)
    .filter((segment) => {
      const normalized = segment.toLowerCase();
      return (
        normalized === "reports" ||
        normalized === "summary" ||
        normalized === "lab-summary" ||
        (/\.(json|txt)$/i.test(segment) && normalized.includes("summary")) ||
        /^day[_-]?\d{1,3}/i.test(segment)
      );
    })
    .join(" ");
  const descriptor = [
    pathDescriptor || path.basename(filePath),
    stringField(record, ["task"]) ?? "",
    stringField(record, ["title"]) ?? "",
    stringField(record, ["phase"]) ?? ""
  ]
    .join(" ")
    .toLowerCase();

  if (
    descriptor.includes("phase-gate") ||
    descriptor.includes("phase_gate") ||
    descriptor.includes("review") ||
    descriptor.includes("readiness")
  ) {
    return "phase_gate_report";
  }

  if (descriptor.includes("summary")) {
    return "summary_report";
  }

  if (hasExplicitDeviceIdentity(raw, vendor)) {
    return "device_report";
  }

  if (
    descriptor.includes("pytest") ||
    descriptor.includes("test") ||
    descriptor.includes("coverage")
  ) {
    return "test_report";
  }

  return "unknown";
}

function inferDeviceName(raw: unknown, resultKind: DayResultKind): string | null {
  if (resultKind !== "device_report" || !isRecord(raw)) {
    return null;
  }

  return stringField(raw, ["deviceName", "device", "hostname", "targetDevice"]);
}

function inferStatus(text: string, raw: unknown): string {
  if (isRecord(raw)) {
    const status = stringField(raw, [
      "status",
      "overall_status",
      "overallStatus",
      "result",
      "summaryStatus"
    ]);
    if (status) {
      return status.toUpperCase();
    }
  }

  const upper = text.toUpperCase();
  if (upper.includes("FAIL")) {
    return "FAIL";
  }
  if (upper.includes("WARN") || upper.includes("WARNING")) {
    return "WARN";
  }
  if (upper.includes("PASS") || upper.includes("OK")) {
    return "PASS";
  }
  return "UNKNOWN";
}

function inferCheckType(filePath: string, raw: unknown): string {
  if (isRecord(raw)) {
    const checkType = stringField(raw, [
      "checkType",
      "task",
      "check",
      "type",
      "check_type",
      "task_name",
      "reportType"
    ]);
    if (checkType) {
      return checkType;
    }
  }

  const baseName = path.basename(filePath, path.extname(filePath)).toLowerCase();
  if (baseName.includes("wan") || baseName.includes("lan")) {
    return "wan_lan";
  }
  if (baseName.includes("interface")) {
    return "interface_status";
  }
  if (baseName.includes("baseline")) {
    return "baseline";
  }
  if (baseName.includes("topology")) {
    return "topology";
  }
  return "report";
}

export function normalizeDayResult(input: {
  filePath: string;
  rawOutput: string;
  parsedResult: unknown;
  createdAt?: string;
  mtimeMs?: number;
}): DayResult {
  const stats = statSync(input.filePath);
  const relativePath = path.relative(process.cwd(), input.filePath);
  const vendor = inferVendor(input.rawOutput, input.parsedResult);
  const resultKind = inferResultKind(relativePath, input.parsedResult, vendor);
  const sourceDay = inferSourceDay(relativePath, input.parsedResult);

  return {
    id: hashId(`${relativePath}:${input.mtimeMs ?? stats.mtimeMs}`),
    sourceDay,
    dayLabel: sourceDay ?? "Unknown Day",
    resultKind,
    deviceName: inferDeviceName(input.parsedResult, resultKind),
    reportTitle: inferReportTitle(relativePath, input.parsedResult),
    vendor,
    checkType: inferCheckType(relativePath, input.parsedResult),
    status: inferStatus(input.rawOutput, input.parsedResult),
    rawOutput: input.rawOutput,
    parsedResult: input.parsedResult,
    createdAt: input.createdAt ?? stats.mtime.toISOString(),
    sourcePath: relativePath
  };
}

function parseReport(filePath: string): DayResult {
  const rawOutput = readFileSync(filePath, "utf8");
  const extension = path.extname(filePath).toLowerCase();
  let parsedResult: unknown = null;

  if (extension === ".json") {
    try {
      parsedResult = JSON.parse(rawOutput);
    } catch {
      parsedResult = { parseWarning: "JSON report could not be parsed.", sourceFormat: "json" };
    }
  } else {
    parsedResult = { sourceFormat: "txt", lineCount: rawOutput.split(/\r?\n/).length };
  }

  return normalizeDayResult({ filePath, rawOutput, parsedResult });
}

export function importDayResults(): DayResult[] {
  const files = REPORT_DIRS.flatMap((directory) => walkFiles(workspacePath(directory)))
    .filter((filePath) => SUPPORTED_EXTENSIONS.has(path.extname(filePath).toLowerCase()))
    .sort((left, right) => left.localeCompare(right));

  return files.map(parseReport);
}

export function findDayResult(id: string) {
  return importDayResults().find((result) => result.id === id) ?? null;
}
