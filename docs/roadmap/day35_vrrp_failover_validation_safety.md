# Day35 VRRP Failover Validation Safety

Day35 validates controlled failover. It is not a RouterOS configuration workflow.

## Allowed Actions

- Read the Day35 topology profile.
- Run source-specific ping from the Automation PC LAN IP:
  - `ping -S 192.168.88.100 <target>`
- Send read-only RouterOS `print` commands:
  - `/system identity print`
  - `/ip address print`
  - `/interface vrrp print detail`
  - `/interface print`
  - `/ip route print`
  - `/ip firewall nat print`
  - `/ip firewall filter print`
- Prompt the operator for manual cable actions.
- Generate JSON, HTML, and TXT reports with sensitive values redacted.

## Blocked Actions

Day35 automation must not:

- Modify RouterOS configuration.
- Enable or disable interfaces.
- Change NAT or firewall rules.
- Add, remove, or change IP addresses.
- Change VRRP priority, VRID, virtual IP, or interface settings.
- Reboot or reset any device.
- Automatically create the failure condition.
- Hide or skip a blocked RouterOS modification attempt.

## Manual Failover Boundary

The only accepted failover trigger is an external operator action:

1. Disconnect lab01 LAN cable from the LAN switch.
2. Press Enter so automation can observe failover.
3. Reconnect lab01 LAN cable.
4. Press Enter so automation can observe recovery.

This boundary keeps the automation from becoming a failure-injection or configuration-change tool.

## Result Rules

PASS requires:

- Baseline is correct.
- lab02 becomes `MASTER` after manual lab01 LAN failure.
- VRRP VIP becomes reachable after convergence.
- LAN server becomes reachable after convergence.
- No RouterOS configuration modification was attempted.

PASS_WITH_NOTES allows:

- Failover succeeds but recovery or preemption behavior differs.
- lab01 does not return to `MASTER` after reconnect.
- Short transient packet loss occurs during convergence.
- lab01 SSH is unavailable while its LAN cable is disconnected, while lab02 still takes over successfully.

FAIL applies when:

- Baseline is wrong.
- lab02 does not become `MASTER`.
- VRRP VIP remains unreachable after the failover window.
- LAN server remains unreachable after the failover window.
- Any blocked RouterOS modification command is attempted.

## Day34 Relationship

Day34 remains read-only/plan-only. It renders a staged apply plan and safety gate, but it does not trigger failover, open SSH for live apply, or execute RouterOS configuration commands.

## LAN Requirements

The Automation PC must have LAN source IP `192.168.88.100`, and Windows route handling must allow `192.168.88.0/24` to stay on-link through the LAN NIC while the default route uses `192.168.0.114`.

The LAN server firewall must allow ICMPv4 Echo from `192.168.88.0/24`, otherwise the Day35 server reachability check can fail even when VRRP failover is working.
