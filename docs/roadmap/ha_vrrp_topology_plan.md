# Day31 HA / VRRP Topology Plan

## Purpose

Day31 creates the planning foundation for a future HA / VRRP lab without changing any live MikroTik configuration. The goal is to document the intended topology, device roles, validation path, and known safety boundaries before Day32 designs a read-only VRRP precheck runner.

This document is planning-only. It does not implement VRRP automation, runner behavior, dashboard behavior, or any RouterOS configuration workflow.

## Target HA / VRRP Topology

```text
ISP Router / Internet
        |
  WAN-side Switch
        |
+-----------------------+
|                       |
MikroTik lab01     MikroTik lab02
|                       |
+-----------------------+
        |
  LAN-side Switch
        |
Automation PC / Client
```

The target topology places both MikroTik routers between a shared WAN-side segment and a shared LAN-side segment. The Automation PC / Client uses the LAN-side network for gateway validation, internet validation, and later failover observation.

Current `lab01` and `lab02` LAN networks may be different, for example `192.168.88.x/24` and `192.168.89.x/24`. For future VRRP testing, both routers usually need LAN-side participation in the same HA LAN segment. Day31 documents that requirement only and does not change any live configuration.

## WAN-side Switch Role

The WAN-side switch provides shared upstream access from the ISP Router / Internet side to both MikroTik routers. In the future HA lab, both `lab01` and `lab02` should be able to reach the upstream network through this side so gateway and internet behavior can be observed from the LAN side.

Day31 does not define switch configuration commands, VLAN changes, or cabling automation. Physical topology confirmation remains a manual lab preparation step.

## LAN-side Switch Role

The LAN-side switch provides the shared HA client segment where the Automation PC / Client connects. Future VRRP validation depends on both routers participating on this LAN-side segment so the client can use a single virtual gateway IP.

The LAN-side switch is also the observation point for client default gateway behavior. It should not require automation changes in Day31.

## MikroTik lab01 Role

`lab01` is the default HA master candidate for planning purposes. In a future VRRP design, `lab01` would normally be expected to own the virtual gateway IP while healthy and preferred.

Day31 does not configure `lab01` as a VRRP master, change its LAN IP, change DHCP behavior, or alter routing/firewall state.

## MikroTik lab02 Role

`lab02` is the default HA backup candidate for planning purposes. In a future VRRP design, `lab02` would normally be expected to observe the shared HA LAN segment and become the active gateway only if the master is unavailable or lower priority.

Day31 does not configure `lab02` as a VRRP backup, add interfaces, change addressing, change DHCP behavior, or alter routing/firewall state.

## Automation PC / Client Role

The Automation PC / Client is the controlled observation host on the LAN-side segment. Its planned responsibilities are:

- Confirm which default gateway is being used.
- Validate reachability to the VRRP virtual gateway IP when a future lab is configured.
- Validate internet reachability through the active gateway.
- Record read-only evidence for gateway, route, interface, and VRRP status.
- Observe future manual failover scenarios without triggering failover automatically.

The client should not run commands that change router configuration as part of the Day31 planning scope.

## VRRP Virtual Gateway IP Concept

The VRRP virtual gateway IP is the stable default gateway address that the Automation PC / Client would use on the shared HA LAN segment. The virtual IP should belong to the shared LAN subnet used by both routers for HA participation.

The virtual gateway IP is a future design concept in Day31. No address is assigned, reserved, configured, or pushed to RouterOS in this task.

## Validation Path

The future validation path should be staged from least invasive to more observational:

1. Confirm physical topology assumptions from documentation and manual lab notes.
2. Read device identity from `lab01` and `lab02`.
3. Read interface status from both routers.
4. Read IP address and route state from both routers.
5. Read VRRP status if available on the device.
6. From the Automation PC / Client, validate the expected gateway path.
7. From the Automation PC / Client, validate internet reachability through the active gateway.
8. In later days only, observe manually initiated failover behavior and record before/after evidence.

Day32 can use this path to design a read-only precheck runner. Any guarded-live or configuration-changing workflow must be designed separately after the read-only evidence model is stable.

## Failure Scenarios Planned For Later Days

Later HA / VRRP work can plan for these scenarios after safety controls are documented and reviewed:

- Master router unavailable.
- Backup router unavailable.
- WAN-side path unavailable for one router.
- LAN-side path unavailable for one router.
- VRRP state mismatch.
- Virtual gateway IP unreachable from the client.
- Client default gateway points to the wrong address.
- Internet reachable through one router but not the other.
- Split-brain risk caused by topology or shared-segment problems.
- Manual failback observation after the preferred router is healthy again.

These scenarios are planned for later days only. Day31 does not trigger or automate failover.

## Non-goals For Day31

- Implementing VRRP automation.
- Adding a VRRP interface.
- Changing LAN IP addressing.
- Changing DHCP server behavior.
- Changing firewall behavior.
- Changing routes.
- Changing runner behavior.
- Changing dashboard behavior.
- Touching live MikroTik configuration.
- Triggering failover automatically.
- Adding shutdown, reboot, reset, or RouterOS configuration commands.
- Committing real configs, secrets, exports, backups, or generated reports.
