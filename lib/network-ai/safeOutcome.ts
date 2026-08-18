import type { ParseRequestOutput } from "./schemas";

export const SAFE_OUTCOME_READ_ONLY_REQUEST =
  "Check WAN and LAN status for LAB-DEMO-ROUTER.";
export const SAFE_OUTCOME_CONFIGURATION_REQUEST =
  "Change interface ether2 on LAB-DEMO-ROUTER to VLAN 20.";
export const SAFE_OUTCOME_CONFIGURATION_TEMPLATE_ID =
  "routeros_bridge_access_vlan_v1";
export const SAFE_OUTCOME_CONTEXT_UNAVAILABLE_REASON =
  "Missing required server-owned synthetic context";

export const SAFE_OUTCOME_CONFIGURATION_PREVIEW = [
  "/interface bridge port",
  'set [find where bridge="bridge-lan" and interface="ether2"] pvid=20 ingress-filtering=yes frame-types=admit-only-untagged-and-priority-tagged',
  "/interface bridge vlan",
  'add bridge="bridge-lan" vlan-ids=20 tagged="bridge-lan" untagged="ether2"'
] as const;

export type SafeOutcome =
  | {
      type: "READ_ONLY_RESULT";
      title: "WAN/LAN Check Result";
      interfaces: [
        { role: "WAN"; name: "ether1"; status: "RUNNING" },
        { role: "LAN"; name: "bridge-lan"; status: "RUNNING" }
      ];
      source: "Deterministic synthetic Stage-0 data";
      synthetic: true;
      liveDeviceContacted: false;
    }
  | {
      type: "CONFIGURATION_PREVIEW";
      state: "AVAILABLE";
      vendor: "MikroTik";
      platform: "RouterOS 7";
      requestedChange: "ether2 → VLAN 20";
      preview: readonly string[];
      source: "SERVER-OWNED TEMPLATE";
      templateId: "routeros_bridge_access_vlan_v1";
      previewOnly: true;
      executed: false;
      approvalRequired: true;
      safety: "BLOCKED";
      jobEligible: false;
    }
  | {
      type: "CONFIGURATION_PREVIEW";
      state: "UNAVAILABLE";
      reason: "Missing required server-owned synthetic context";
      previewOnly: true;
      executed: false;
      approvalRequired: true;
      safety: "BLOCKED";
      jobEligible: false;
    }
  | {
      type: "BLOCKED_NO_OUTCOME";
      reason: "No safe outcome is available for this request.";
      jobCreated: false;
      executed: false;
    };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isExactStringArray(value: unknown, expected: readonly string[]) {
  return (
    Array.isArray(value) &&
    value.length === expected.length &&
    value.every((item, index) => item === expected[index])
  );
}

function findCanonicalDevice(deviceInventory: unknown) {
  if (
    !isRecord(deviceInventory) ||
    deviceInventory.context !== "synthetic-local-demo-only" ||
    deviceInventory.synthetic !== true ||
    deviceInventory.liveDeviceContacted !== false ||
    !Array.isArray(deviceInventory.devices)
  ) {
    return null;
  }

  return (
    deviceInventory.devices.find(
      (device) => isRecord(device) && device.name === "LAB-DEMO-ROUTER"
    ) ?? null
  );
}

function hasExactReadOnlySafety(output: ParseRequestOutput) {
  return (
    output.intent === "run_check" &&
    output.targetDevice === "LAB-DEMO-ROUTER" &&
    output.vendor === "mikrotik" &&
    output.interfaceName === null &&
    output.vlanId === null &&
    output.recommendedActionId === "wan_lan_check" &&
    output.missingFields.length === 0 &&
    output.riskLevel === "low" &&
    output.requiresApproval === false &&
    output.blocked === false &&
    output.jobCreationAllowed === true &&
    output.blockedReason === null
  );
}

function hasAuthoritativeConfigurationSafety(output: ParseRequestOutput) {
  return (
    (output.riskLevel === "medium" || output.riskLevel === "high") &&
    output.requiresApproval === true &&
    output.blocked === true &&
    output.jobCreationAllowed === false
  );
}

function buildReadOnlyResult(device: Record<string, unknown>): SafeOutcome | null {
  if (
    device.vendor !== "mikrotik" ||
    device.platform !== "routeros" ||
    device.synthetic !== true ||
    device.liveDeviceContacted !== false ||
    !Array.isArray(device.interfaces)
  ) {
    return null;
  }

  const wan = device.interfaces.find(
    (item) =>
      isRecord(item) &&
      item.name === "ether1" &&
      item.role === "WAN" &&
      item.syntheticStatus === "running"
  );
  const lan = device.interfaces.find(
    (item) =>
      isRecord(item) &&
      item.name === "bridge-lan" &&
      item.role === "LAN" &&
      item.syntheticStatus === "running"
  );

  if (!wan || !lan) {
    return null;
  }

  return {
    type: "READ_ONLY_RESULT",
    title: "WAN/LAN Check Result",
    interfaces: [
      { role: "WAN", name: "ether1", status: "RUNNING" },
      { role: "LAN", name: "bridge-lan", status: "RUNNING" }
    ],
    source: "Deterministic synthetic Stage-0 data",
    synthetic: true,
    liveDeviceContacted: false
  };
}

function hasConfigurationContext(device: Record<string, unknown>) {
  if (
    device.vendor !== "mikrotik" ||
    device.platform !== "routeros" ||
    device.routerOsMajorVersion !== 7 ||
    device.synthetic !== true ||
    device.liveDeviceContacted !== false ||
    !isRecord(device.configurationContext)
  ) {
    return false;
  }

  const context = device.configurationContext;
  if (!isRecord(context.vlanEntry)) {
    return false;
  }
  const vlanEntry = context.vlanEntry;

  return (
    context.synthetic === true &&
    context.serverOwned === true &&
    context.templateId === SAFE_OUTCOME_CONFIGURATION_TEMPLATE_ID &&
    context.bridgeName === "bridge-lan" &&
    context.interfaceName === "ether2" &&
    context.interfaceBelongsToBridge === true &&
    context.currentPvid === 1 &&
    context.expectedPortMode === "access" &&
    context.vlanFilteringEnabled === true &&
    context.ingressFilteringEnabled === true &&
    context.frameTypes === "admit-only-untagged-and-priority-tagged" &&
    context.cpuBridgePort === "bridge-lan" &&
    isExactStringArray(context.targetTaggedInterfaces, ["bridge-lan"]) &&
    isExactStringArray(context.targetUntaggedInterfaces, ["ether2"]) &&
    vlanEntry.vlanId === 20 &&
    vlanEntry.exists === false
  );
}

function unavailableConfigurationPreview(): SafeOutcome {
  return {
    type: "CONFIGURATION_PREVIEW",
    state: "UNAVAILABLE",
    reason: SAFE_OUTCOME_CONTEXT_UNAVAILABLE_REASON,
    previewOnly: true,
    executed: false,
    approvalRequired: true,
    safety: "BLOCKED",
    jobEligible: false
  };
}

function blockedNoOutcome(): SafeOutcome {
  return {
    type: "BLOCKED_NO_OUTCOME",
    reason: "No safe outcome is available for this request.",
    jobCreated: false,
    executed: false
  };
}

export function buildSafeOutcome(input: {
  userRequest: string;
  output: ParseRequestOutput;
  deviceInventory: unknown;
}): SafeOutcome {
  const device = findCanonicalDevice(input.deviceInventory);

  if (
    input.userRequest === SAFE_OUTCOME_READ_ONLY_REQUEST &&
    hasExactReadOnlySafety(input.output) &&
    device
  ) {
    return buildReadOnlyResult(device) ?? blockedNoOutcome();
  }

  if (input.userRequest === SAFE_OUTCOME_CONFIGURATION_REQUEST) {
    if (!hasAuthoritativeConfigurationSafety(input.output)) {
      return blockedNoOutcome();
    }
    if (!device || !hasConfigurationContext(device)) {
      return unavailableConfigurationPreview();
    }
    return {
      type: "CONFIGURATION_PREVIEW",
      state: "AVAILABLE",
      vendor: "MikroTik",
      platform: "RouterOS 7",
      requestedChange: "ether2 → VLAN 20",
      preview: SAFE_OUTCOME_CONFIGURATION_PREVIEW,
      source: "SERVER-OWNED TEMPLATE",
      templateId: SAFE_OUTCOME_CONFIGURATION_TEMPLATE_ID,
      previewOnly: true,
      executed: false,
      approvalRequired: true,
      safety: "BLOCKED",
      jobEligible: false
    };
  }

  return blockedNoOutcome();
}
