import { createHash, randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import type { ParseRequestOutput, ParseResultRecord } from "./schemas";

const STORE_PATH =
  process.env.NETWORK_AI_PARSE_RESULT_STORE_PATH ??
  path.join(process.cwd(), "data", "network-ai", "parse-results.json");

function ensureStoreDirectory() {
  mkdirSync(path.dirname(STORE_PATH), { recursive: true });
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalizeInventorySnapshot(deviceInventory: unknown) {
  return isRecord(deviceInventory) ? deviceInventory : null;
}

function readStore(): ParseResultRecord[] {
  if (!existsSync(STORE_PATH)) {
    writeStore([]);
    return [];
  }

  try {
    const content = readFileSync(STORE_PATH, "utf8").trim();
    if (!content) {
      return [];
    }
    const parsed = JSON.parse(content) as unknown;
    return Array.isArray(parsed) ? (parsed as ParseResultRecord[]) : [];
  } catch {
    return [];
  }
}

function writeStore(records: ParseResultRecord[]) {
  ensureStoreDirectory();
  writeFileSync(STORE_PATH, `${JSON.stringify(records, null, 2)}\n`, "utf8");
}

export function hashDeviceInventory(deviceInventory: unknown) {
  return createHash("sha256")
    .update(JSON.stringify(normalizeInventorySnapshot(deviceInventory)))
    .digest("hex");
}

export function createParseResultRecord(input: {
  userRequest: string;
  deviceInventory?: unknown;
  output: ParseRequestOutput;
}) {
  const record: ParseResultRecord = {
    id: `parse_${randomUUID()}`,
    userRequest: input.userRequest,
    deviceInventoryHash: hashDeviceInventory(input.deviceInventory),
    deviceInventorySnapshot: normalizeInventorySnapshot(input.deviceInventory),
    output: input.output,
    createdAt: new Date().toISOString()
  };

  const records = readStore();
  records.push(record);
  writeStore(records);
  return record;
}

export function listParseResultRecords(limit = 25) {
  return readStore()
    .sort((left, right) => right.createdAt.localeCompare(left.createdAt))
    .slice(0, limit);
}

export function getLatestParseResultRecord() {
  return listParseResultRecords(1)[0] ?? null;
}

export function selectParseResultPresentationFields(
  record: ParseResultRecord | null
) {
  if (!record) {
    return null;
  }

  const output = record.output;
  return {
    output: {
      intent: output.intent,
      recommendedActionId: output.recommendedActionId,
      missingFields: output.missingFields,
      riskLevel: output.riskLevel,
      requiresApproval: output.requiresApproval,
      blocked: output.blocked,
      jobCreationAllowed: output.jobCreationAllowed,
      blockedReason: output.blockedReason
    },
    createdAt: record.createdAt
  };
}

export function clearParseResultStoreForTests() {
  writeStore([]);
}
