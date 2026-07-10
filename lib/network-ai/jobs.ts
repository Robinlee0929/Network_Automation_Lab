import { randomUUID } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { findAvailableAction } from "./actions";
import { evaluateJobCreateReadiness } from "./readiness";
import type { NetworkJob, Vendor } from "./schemas";

const STORE_PATH =
  process.env.NETWORK_AI_JOB_STORE_PATH ??
  path.join(process.cwd(), "data", "network-ai", "jobs.json");

function createJobId() {
  return `job_${randomUUID()}`;
}

function ensureStoreDirectory() {
  mkdirSync(path.dirname(STORE_PATH), { recursive: true });
}

function readStore(): NetworkJob[] {
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
    return Array.isArray(parsed) ? (parsed as NetworkJob[]) : [];
  } catch {
    return [];
  }
}

function writeStore(jobs: NetworkJob[]) {
  ensureStoreDirectory();
  writeFileSync(STORE_PATH, `${JSON.stringify(jobs, null, 2)}\n`, "utf8");
}

function stringParam(params: Record<string, unknown> | undefined, key: string) {
  const value = params?.[key];
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function normalizeVendor(value: unknown): Vendor {
  if (typeof value !== "string") {
    return "unknown";
  }
  const normalized = value.toLowerCase();
  if (normalized === "mikrotik" || normalized.includes("routeros")) {
    return "mikrotik";
  }
  if (normalized === "cisco" || normalized === "ios" || normalized.includes("cisco ios")) {
    return "cisco";
  }
  return "unknown";
}

export function listNetworkJobs() {
  return readStore().sort((left, right) => right.createdAt.localeCompare(left.createdAt));
}

export function createNetworkJob(input: {
  actionId: string;
  targetDevice?: string | null;
  vendor?: unknown;
  deviceInventory?: unknown;
  params?: Record<string, unknown>;
}) {
  const intent = input.params?.intent;
  const readiness = evaluateJobCreateReadiness({
    actionId: input.actionId,
    targetDevice: input.targetDevice,
    deviceInventory: input.deviceInventory,
    intent
  });
  const action = readiness.action ?? findAvailableAction(input.actionId);
  const job: NetworkJob = {
    id: createJobId(),
    actionId: action?.id ?? input.actionId,
    targetDevice: readiness.targetDevice,
    vendor: normalizeVendor(input.vendor ?? input.params?.vendor),
    params: input.params ?? {},
    status: readiness.status,
    blockedReason: readiness.blockedReason ?? undefined,
    riskLevel: action?.riskLevel ?? "high",
    requiresApproval: readiness.requiresApproval,
    readOnly: action?.readOnly ?? false,
    source: stringParam(input.params, "source"),
    parseResultId: stringParam(input.params, "parseResultId"),
    createdAt: new Date().toISOString()
  };

  const jobs = readStore();
  jobs.unshift(job);
  writeStore(jobs);
  return {
    ok: true as const,
    job
  };
}

export function clearNetworkJobStoreForTests() {
  writeStore([]);
}
