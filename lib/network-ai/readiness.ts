import { findAvailableAction, isAvailableActionId } from "./actions";
import type { ParseRequestOutput, Vendor } from "./schemas";

export const DEVICE_READINESS_BLOCKED_REASON =
  "Target device not found in inventory or missing connection details";
export const BACKUP_CONFIG_BLOCKED_REASON =
  "backup_config requires approval because it may expose sensitive configuration";
export const CONFIG_CHANGE_BLOCKED_REASON =
  "Config change requires approval and is not executable in Phase 1";

const deviceNameFields = ["name", "hostname", "deviceName", "targetDevice", "id"];
const connectionFields = ["managementIp", "ip", "host", "accessMethod"];

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function normalize(value: string) {
  return value.trim().toLowerCase();
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

function hasConnectionInfo(value: unknown) {
  return isRecord(value) && Boolean(stringField(value, connectionFields));
}

function inventoryDevices(deviceInventory: unknown) {
  if (!isRecord(deviceInventory)) {
    return [];
  }

  if (Array.isArray(deviceInventory.devices)) {
    return deviceInventory.devices.filter(isRecord);
  }

  return [];
}

export function findInventoryDevice(targetDevice: string | null, deviceInventory: unknown) {
  if (!targetDevice) {
    return null;
  }

  const normalizedTarget = normalize(targetDevice);
  return (
    inventoryDevices(deviceInventory).find((device) =>
      deviceNameFields.some((field) => {
        const value = device[field];
        return typeof value === "string" && normalize(value) === normalizedTarget;
      })
    ) ?? null
  );
}

export function hasDeviceConnection(targetDevice: string | null, deviceInventory: unknown) {
  const matchedDevice = findInventoryDevice(targetDevice, deviceInventory);
  return Boolean(hasConnectionInfo(matchedDevice) || hasConnectionInfo(deviceInventory));
}

export function evaluateDeviceReadiness(targetDevice: string | null, deviceInventory: unknown) {
  const matchedDevice = findInventoryDevice(targetDevice, deviceInventory);
  const deviceConnection = hasDeviceConnection(targetDevice, deviceInventory);

  return {
    matchedDevice,
    deviceInventoryMatch: Boolean(matchedDevice),
    deviceConnection,
    ready: Boolean(targetDevice && (matchedDevice || deviceConnection))
  };
}

function inferInventoryVendor(matchedDevice: Record<string, unknown> | null) {
  const vendor = matchedDevice ? stringField(matchedDevice, ["vendor", "platformVendor", "osVendor"]) : null;
  const normalized = vendor?.toLowerCase();
  if (normalized?.includes("mikrotik") || normalized?.includes("routeros")) {
    return "mikrotik";
  }
  if (normalized?.includes("cisco") || normalized === "ios" || normalized?.includes("cisco ios")) {
    return "cisco";
  }
  return null;
}

function userRequestMentionsSpecificInterface(userRequest: string) {
  return /\b(?:gi|gigabitethernet|fa|fastethernet|te|ether|ethernet)\s*\d+(?:\/\d+)*(?:\.\d+)?\b/i.test(
    userRequest
  ) || /\bport\s+\d+\b/i.test(userRequest);
}

function addMissing(missingFields: Set<string>, field: string) {
  missingFields.add(field);
}

export function sanitizeParseRequestResult(input: {
  output: ParseRequestOutput;
  userRequest: string;
  deviceInventory?: unknown;
}): ParseRequestOutput {
  const output = input.output;
  const knownActionId = isAvailableActionId(output.recommendedActionId)
    ? output.recommendedActionId
    : null;
  const action = knownActionId ? findAvailableAction(knownActionId) : null;
  const readiness = evaluateDeviceReadiness(output.targetDevice, input.deviceInventory);
  const inventoryVendor = inferInventoryVendor(readiness.matchedDevice);
  const configChangeIntent =
    output.intent === "change_access_vlan" || output.intent === "update_description";
  const missingFields = new Set<string>();

  if (!output.targetDevice) {
    addMissing(missingFields, "targetDevice");
  }

  if (output.targetDevice && !readiness.ready) {
    addMissing(missingFields, "deviceInventoryMatch");
  }

  if (!knownActionId && !configChangeIntent) {
    addMissing(missingFields, "recommendedActionId");
  }

  if (output.intent === "change_access_vlan") {
    if (!output.interfaceName) {
      addMissing(missingFields, "interfaceName");
    }
    if (output.vlanId === null) {
      addMissing(missingFields, "vlanId");
    }
    if (!readiness.deviceInventoryMatch) {
      addMissing(missingFields, "deviceInventoryMatch");
    }
  }

  if (
    knownActionId === "interface_status_check" &&
    userRequestMentionsSpecificInterface(input.userRequest) &&
    !output.interfaceName
  ) {
    addMissing(missingFields, "interfaceName");
  }

  let blockedReason: string | null = null;
  let requiresApproval = output.requiresApproval || configChangeIntent;
  let jobCreationAllowed = false;
  let riskLevel = output.riskLevel;

  if (!readiness.ready) {
    blockedReason = DEVICE_READINESS_BLOCKED_REASON;
  }

  if (knownActionId === "backup_config") {
    requiresApproval = true;
    riskLevel = "medium";
    blockedReason = blockedReason ?? BACKUP_CONFIG_BLOCKED_REASON;
  }

  if (configChangeIntent) {
    requiresApproval = true;
    riskLevel = riskLevel === "low" ? "medium" : riskLevel;
    blockedReason = blockedReason ?? CONFIG_CHANGE_BLOCKED_REASON;
  }

  if (action && action.riskLevel !== "low") {
    requiresApproval = true;
    riskLevel = action.riskLevel;
  }

  if (action && action.readOnly && action.riskLevel === "low" && readiness.ready && !configChangeIntent) {
    jobCreationAllowed = true;
  }

  if (knownActionId === "backup_config" || requiresApproval || missingFields.size > 0) {
    jobCreationAllowed = false;
  }

  const blocked = !jobCreationAllowed;

  return {
    intent: output.intent,
    targetDevice: output.targetDevice,
    vendor: (inventoryVendor ?? output.vendor) as Vendor,
    interfaceName: output.interfaceName,
    vlanId: output.vlanId,
    recommendedActionId: knownActionId,
    missingFields: Array.from(missingFields),
    riskLevel,
    requiresApproval,
    blocked,
    jobCreationAllowed,
    blockedReason,
    notes: [
      ...output.notes,
      "AI recommendations are limited to Phase 1 job creation readiness and never execute device commands."
    ]
  };
}

export function evaluateJobCreateReadiness(input: {
  actionId: string;
  targetDevice?: string | null;
  deviceInventory?: unknown;
  intent?: unknown;
}) {
  const action = findAvailableAction(input.actionId);
  const targetDevice = input.targetDevice?.trim() || null;
  const readiness = evaluateDeviceReadiness(targetDevice, input.deviceInventory);
  const intent = typeof input.intent === "string" ? input.intent : null;
  const configChangeIntent = intent === "change_access_vlan" || intent === "update_description";

  if (!action) {
    return {
      action,
      status: "blocked" as const,
      blockedReason: "Unknown actionId",
      requiresApproval: true,
      targetDevice
    };
  }

  if (!targetDevice) {
    return {
      action,
      status: "blocked" as const,
      blockedReason: "Missing targetDevice",
      requiresApproval: true,
      targetDevice: null
    };
  }

  if (!readiness.ready) {
    return {
      action,
      status: "blocked" as const,
      blockedReason: DEVICE_READINESS_BLOCKED_REASON,
      requiresApproval: true,
      targetDevice
    };
  }

  if (input.actionId === "backup_config") {
    return {
      action,
      status: "pending_approval" as const,
      blockedReason: BACKUP_CONFIG_BLOCKED_REASON,
      requiresApproval: true,
      targetDevice
    };
  }

  if (configChangeIntent || action.configChange || action.riskLevel !== "low") {
    return {
      action,
      status: "pending_approval" as const,
      blockedReason: configChangeIntent ? CONFIG_CHANGE_BLOCKED_REASON : null,
      requiresApproval: true,
      targetDevice
    };
  }

  return {
    action,
    status: "ready" as const,
    blockedReason: null,
    requiresApproval: false,
    targetDevice
  };
}
