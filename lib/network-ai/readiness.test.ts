import { describe, expect, it } from "vitest";

import type { ParseRequestOutput } from "./schemas";
import { evaluateJobCreateReadiness, sanitizeParseRequestResult } from "./readiness";

const readyInventory = {
  devices: [
    {
      name: "router-01",
      managementIp: "192.0.2.10",
    },
  ],
};

const readyDemoInventory = {
  devices: [
    {
      name: "LAB-DEMO-ROUTER",
      vendor: "mikrotik",
      managementIp: "192.0.2.20",
    },
  ],
};

function falseSafeModelOutput(
  overrides: Partial<ParseRequestOutput> = {}
): ParseRequestOutput {
  return {
    intent: "run_check",
    targetDevice: "LAB-DEMO-ROUTER",
    vendor: "mikrotik",
    interfaceName: null,
    vlanId: null,
    recommendedActionId: "wan_lan_check",
    missingFields: [],
    riskLevel: "low",
    requiresApproval: false,
    blocked: false,
    jobCreationAllowed: true,
    blockedReason: null,
    notes: [],
    ...overrides,
  };
}

describe("evaluateJobCreateReadiness", () => {
  it("blocks an unknown action ID and requires approval", () => {
    expect(
      evaluateJobCreateReadiness({
        actionId: "unknown_action",
        targetDevice: "router-01",
        deviceInventory: readyInventory,
      })
    ).toMatchObject({
      action: null,
      status: "blocked",
      blockedReason: "Unknown actionId",
      requiresApproval: true,
      targetDevice: "router-01",
    });
  });

  it.each([undefined, null, "   "])(
    "blocks a missing or whitespace-only target device %#",
    (targetDevice) => {
      expect(
        evaluateJobCreateReadiness({
          actionId: "baseline_check",
          targetDevice,
          deviceInventory: readyInventory,
        })
      ).toMatchObject({
        status: "blocked",
        blockedReason: "Missing targetDevice",
        requiresApproval: true,
        targetDevice: null,
      });
    }
  );

  it("blocks when synthetic inventory cannot prove target-device readiness", () => {
    expect(
      evaluateJobCreateReadiness({
        actionId: "baseline_check",
        targetDevice: "router-01",
        deviceInventory: {
          devices: [{ name: "router-02" }],
        },
      })
    ).toMatchObject({
      status: "blocked",
      blockedReason: "Target device not found in inventory or missing connection details",
      requiresApproval: true,
      targetDevice: "router-01",
    });
  });

  it("keeps backup_config pending approval for a ready synthetic device", () => {
    expect(
      evaluateJobCreateReadiness({
        actionId: "backup_config",
        targetDevice: "router-01",
        deviceInventory: readyInventory,
      })
    ).toMatchObject({
      status: "pending_approval",
      blockedReason: "backup_config requires approval because it may expose sensitive configuration",
      requiresApproval: true,
      targetDevice: "router-01",
    });
  });

  it.each(["change_access_vlan", "update_description"])(
    "keeps the %s intent pending approval for a ready synthetic device",
    (intent) => {
      expect(
        evaluateJobCreateReadiness({
          actionId: "baseline_check",
          targetDevice: "router-01",
          deviceInventory: readyInventory,
          intent,
        })
      ).toMatchObject({
        status: "pending_approval",
        blockedReason: "Config change requires approval and is not executable in Phase 1",
        requiresApproval: true,
        targetDevice: "router-01",
      });
    }
  );

  it("marks a low-risk read-only action ready and trims the target device", () => {
    expect(
      evaluateJobCreateReadiness({
        actionId: "baseline_check",
        targetDevice: "  router-01  ",
        deviceInventory: readyInventory,
      })
    ).toMatchObject({
      status: "ready",
      blockedReason: null,
      requiresApproval: false,
      targetDevice: "router-01",
    });
  });
});

describe("sanitizeParseRequestResult original-request safety guard", () => {
  it("blocks a mixed read/write request despite false-safe model output", () => {
    const sanitized = sanitizeParseRequestResult({
      output: falseSafeModelOutput(),
      userRequest:
        "Check WAN and LAN status for LAB-DEMO-ROUTER, then change ether2 to VLAN 20.",
      deviceInventory: readyDemoInventory,
    });

    expect(sanitized).toMatchObject({
      intent: "run_check",
      recommendedActionId: "wan_lan_check",
      riskLevel: "medium",
      requiresApproval: true,
      blocked: true,
      jobCreationAllowed: false,
      blockedReason: "Config change requires approval and is not executable in Phase 1",
    });
  });

  it.each([
    "Check WAN and LAN status for LAB-DEMO-ROUTER.",
    "Can you check whether WAN and LAN are up on LAB-DEMO-ROUTER?",
    "Check whether WAN status changed on LAB-DEMO-ROUTER.",
    "Show configuration changes for LAB-DEMO-ROUTER.",
    "Review the last change record for LAB-DEMO-ROUTER.",
  ])("does not overblock read-only wording: %s", (userRequest) => {
    const sanitized = sanitizeParseRequestResult({
      output: falseSafeModelOutput(),
      userRequest,
      deviceInventory: readyDemoInventory,
    });

    expect(sanitized).toMatchObject({
      riskLevel: "low",
      requiresApproval: false,
      blocked: false,
      jobCreationAllowed: true,
      blockedReason: null,
    });
  });

  it.each([
    "Change interface ether2 on LAB-DEMO-ROUTER to VLAN 20.",
    "Set ether2 VLAN 20 on LAB-DEMO-ROUTER.",
    "Move ether2 to VLAN 20 on LAB-DEMO-ROUTER.",
    "Assign ether2 VLAN 20 on LAB-DEMO-ROUTER.",
    "Change interface ether2 on LAB-DEMO-ROUTER to VLAN 30.",
  ])("fails closed for explicit VLAN mutation wording: %s", (userRequest) => {
    const sanitized = sanitizeParseRequestResult({
      output: falseSafeModelOutput({
        intent: "unknown",
        recommendedActionId: null,
      }),
      userRequest,
      deviceInventory: readyDemoInventory,
    });

    expect(sanitized.riskLevel).not.toBe("low");
    expect(sanitized.requiresApproval).toBe(true);
    expect(sanitized.blocked).toBe(true);
    expect(sanitized.jobCreationAllowed).toBe(false);
  });

  it("never lowers an existing high risk for a detected mutation", () => {
    const sanitized = sanitizeParseRequestResult({
      output: falseSafeModelOutput({
        recommendedActionId: "backup_config",
        riskLevel: "high",
      }),
      userRequest: "Change interface ether2 on LAB-DEMO-ROUTER to VLAN 20.",
      deviceInventory: readyDemoInventory,
    });

    expect(sanitized).toMatchObject({
      riskLevel: "high",
      requiresApproval: true,
      blocked: true,
      jobCreationAllowed: false,
    });
  });
});
