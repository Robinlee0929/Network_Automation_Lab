import { describe, expect, it } from "vitest";

import { evaluateJobCreateReadiness } from "./readiness";

const readyInventory = {
  devices: [
    {
      name: "router-01",
      managementIp: "192.0.2.10",
    },
  ],
};

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
