import type { AvailableAction } from "./schemas";

export const availableNetworkActions: AvailableAction[] = [
  {
    id: "baseline_check",
    label: "Baseline Check",
    description: "Run existing read-only baseline validation for a supported router or switch.",
    checkType: "baseline",
    readOnly: true,
    configChange: false,
    riskLevel: "low",
    allowedVendors: ["mikrotik", "cisco", "unknown"]
  },
  {
    id: "wan_lan_check",
    label: "WAN/LAN Check",
    description: "Review WAN and LAN status evidence from existing MikroTik-oriented checks.",
    checkType: "wan_lan",
    readOnly: true,
    configChange: false,
    riskLevel: "low",
    allowedVendors: ["mikrotik", "unknown"]
  },
  {
    id: "interface_status_check",
    label: "Interface Status Check",
    description: "Run or prepare a read-only interface status validation workflow.",
    checkType: "interface_status",
    readOnly: true,
    configChange: false,
    riskLevel: "low",
    allowedVendors: ["mikrotik", "cisco", "unknown"]
  },
  {
    id: "backup_config",
    label: "Backup Config",
    description: "Create a job request for a guarded configuration backup workflow.",
    checkType: "backup",
    readOnly: true,
    configChange: false,
    riskLevel: "medium",
    allowedVendors: ["mikrotik", "cisco", "unknown"]
  },
  {
    id: "environment_check",
    label: "Environment Check",
    description: "Validate local platform readiness, report visibility, and non-live runtime context.",
    checkType: "environment",
    readOnly: true,
    configChange: false,
    riskLevel: "low",
    allowedVendors: ["mikrotik", "cisco", "unknown"]
  }
];

export function getAvailableActions() {
  return availableNetworkActions;
}

export function findAvailableAction(actionId: string) {
  return availableNetworkActions.find((action) => action.id === actionId) ?? null;
}

export function isAvailableActionId(actionId: string | null | undefined) {
  if (!actionId) {
    return false;
  }

  return availableNetworkActions.some((action) => action.id === actionId);
}
