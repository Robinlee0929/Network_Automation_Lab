import { NextResponse } from "next/server";
import { validationError } from "@/lib/ai/routeHandler";
import { createNetworkJob } from "@/lib/network-ai/jobs";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export async function POST(request: Request) {
  const body = (await request.json()) as {
    actionId?: unknown;
    targetDevice?: unknown;
    vendor?: unknown;
    deviceInventory?: unknown;
    params?: unknown;
    command?: unknown;
    scriptPath?: unknown;
  };

  if (typeof body.actionId !== "string" || !body.actionId.trim()) {
    return validationError("actionId is required.");
  }

  if (body.command !== undefined || body.scriptPath !== undefined) {
    return validationError("command and scriptPath are not accepted by Phase 1 job creation.");
  }

  if (
    body.targetDevice !== undefined &&
    body.targetDevice !== null &&
    typeof body.targetDevice !== "string"
  ) {
    return validationError("targetDevice must be a string when provided.");
  }

  if (body.params !== undefined && !isRecord(body.params)) {
    return validationError("params must be an object when provided.");
  }

  if (body.vendor !== undefined && typeof body.vendor !== "string") {
    return validationError("vendor must be a string when provided.");
  }

  const params = body.params as Record<string, unknown> | undefined;
  if (params && ("command" in params || "scriptPath" in params)) {
    return validationError("params.command and params.scriptPath are not accepted.");
  }

  const result = createNetworkJob({
    actionId: body.actionId.trim(),
    targetDevice: typeof body.targetDevice === "string" ? body.targetDevice.trim() : null,
    vendor: body.vendor,
    deviceInventory: body.deviceInventory,
    params
  });

  return NextResponse.json({ job: result.job });
}
