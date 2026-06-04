# Day31 HA / VRRP Safety Model

## Purpose

Day31 defines the safety language for future HA / VRRP work before any automation is added. It gives Day32 a clear boundary for designing a read-only VRRP precheck runner while keeping live RouterOS configuration untouched.

This is a documentation-only safety model. It does not add runner tasks, dashboard routes, RouterOS commands, generated reports, or live failover behavior.

## Safety Levels

### report-only

Reads committed documentation or already-generated local evidence. It may generate Markdown, JSON, or HTML reports from local data, but it must not connect to routers or change lab devices.

### read-only

Connects to devices only to inspect state. It may read identity, interfaces, IP addresses, routes, and VRRP status if available. It must not change RouterOS configuration or trigger topology events.

### dry-run

Builds a plan and explains what would be checked or changed in a future workflow. It may validate inputs and render planned actions, but it must not execute configuration changes.

### guarded-live

Reserved for future workflows that may affect live lab state only after explicit human authorization, narrow scope checks, and reviewed guardrails. Guarded-live is not allowed for Day31 and should not be introduced for VRRP until the read-only precheck model is complete.

### destructive-disabled

Represents actions that are intentionally blocked from automation. Anything that can remove configuration, reset devices, reboot devices, disable connectivity, or force failover belongs in this category unless a future human-run manual lab procedure explicitly documents it outside automation.

## Allowed By Default

The following actions are allowed by default for the HA / VRRP planning foundation:

- Read device identity.
- Read interface status.
- Read IP address state.
- Read route state.
- Read VRRP status if available.
- Generate Markdown reports.
- Generate JSON reports.
- Generate HTML reports.
- Document topology and safety model.

Allowed-by-default actions must still avoid secrets and must not include RouterOS configuration changes.

## Forbidden By Default

The following actions are forbidden by default for HA / VRRP automation planning:

- Modify RouterOS configuration.
- Add a VRRP interface.
- Change LAN IP addressing.
- Change DHCP server behavior.
- Change firewall behavior.
- Shut down an interface.
- Reboot a router.
- Reset configuration.
- Trigger failover automatically.
- Commit real configuration files.
- Commit secrets.
- Commit exports or backups.
- Commit generated reports.

These restrictions apply even when a command could be useful for troubleshooting. Day31 and Day32 should prefer documentation, read-only evidence, and human-reviewed lab notes.

## Day31 Documentation Boundary

Day31 is limited to:

- Documenting the HA / VRRP topology plan.
- Documenting safety levels and default permissions.
- Recording that current `lab01` and `lab02` LAN networks may differ.
- Recording that future VRRP testing usually needs both routers on the same HA LAN segment.
- Preparing Day32 to design a read-only precheck runner.

Day31 must not:

- Implement VRRP automation.
- Modify runtime code.
- Modify runner behavior.
- Modify dashboard behavior.
- Modify live MikroTik configuration.
- Add commands that can shut down, reboot, reset, or change RouterOS configuration.

## Day32 Read-only Precheck Direction

Day32 can safely build on this model by designing a read-only precheck runner that collects inventory and state evidence. The first version should remain focused on inspection and reporting:

- Identify `lab01` and `lab02`.
- Inspect interface status.
- Inspect IP address and route state.
- Inspect VRRP status when present.
- Compare observed state against the documented HA topology assumptions.
- Report blockers without attempting to fix them.

Any future transition from read-only precheck to dry-run planning or guarded-live execution should require a separate design review and explicit safety checklist.
