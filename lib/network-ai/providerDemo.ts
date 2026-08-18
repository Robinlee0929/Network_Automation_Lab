export const NETWORK_AI_PROVIDER_DEMO_MAX_REQUEST_LENGTH = 500;

export const LOCAL_DEMO_DEVICE_INVENTORY = {
  context: "synthetic-local-demo-only",
  synthetic: true,
  liveDeviceContacted: false,
  devices: [
    {
      name: "LAB-DEMO-ROUTER",
      vendor: "mikrotik",
      platform: "routeros",
      routerOsMajorVersion: 7,
      managementIp: "192.0.2.10",
      synthetic: true,
      liveDeviceContacted: false,
      interfaces: [
        {
          name: "ether1",
          role: "WAN",
          syntheticStatus: "running"
        },
        {
          name: "bridge-lan",
          role: "LAN",
          syntheticStatus: "running"
        }
      ],
      configurationContext: {
        synthetic: true,
        serverOwned: true,
        templateId: "routeros_bridge_access_vlan_v1",
        bridgeName: "bridge-lan",
        interfaceName: "ether2",
        interfaceBelongsToBridge: true,
        currentPvid: 1,
        expectedPortMode: "access",
        vlanFilteringEnabled: true,
        ingressFilteringEnabled: true,
        frameTypes: "admit-only-untagged-and-priority-tagged",
        cpuBridgePort: "bridge-lan",
        targetTaggedInterfaces: ["bridge-lan"],
        targetUntaggedInterfaces: ["ether2"],
        vlanEntry: {
          vlanId: 20,
          exists: false
        }
      }
    }
  ]
} as const;

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

export function isNetworkAiProviderDemoEnabled() {
  return process.env.NETWORK_AI_PROVIDER_DEMO_ENABLED?.trim() === "1";
}

export function validateNetworkAiProviderDemoRequest(value: unknown) {
  if (!isRecord(value)) {
    return { ok: false as const, error: "Request body must be a JSON object." };
  }

  const keys = Object.keys(value);
  if (keys.some((key) => key !== "userRequest")) {
    return {
      ok: false as const,
      error: "Only userRequest is accepted by the local recommendation preview."
    };
  }

  if (typeof value.userRequest !== "string") {
    return { ok: false as const, error: "userRequest must be a string." };
  }

  const userRequest = value.userRequest.trim();
  if (!userRequest) {
    return { ok: false as const, error: "userRequest is required." };
  }

  if (userRequest.length > NETWORK_AI_PROVIDER_DEMO_MAX_REQUEST_LENGTH) {
    return {
      ok: false as const,
      error: `userRequest must be ${NETWORK_AI_PROVIDER_DEMO_MAX_REQUEST_LENGTH} characters or fewer.`
    };
  }

  return { ok: true as const, userRequest };
}
