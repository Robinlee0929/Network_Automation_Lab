# Day35 VRRP Failover Validation Plan

Day35 is not a configuration day. Its purpose is to safely prove that when lab01 fails on the LAN side, lab02 can take over the VRRP virtual gateway IP.

## Scope

- Task: `day35-vrrp-failover-validation`
- Profile: `topology_profiles/day35_vrrp_failover_validation.json`
- Runner: `python network_lab.py --task day35-vrrp-failover-validation`
- Reports:
  - `reports/lab-summary/day35_vrrp_failover_validation.json`
  - `reports/lab-summary/day35_vrrp_failover_validation.html`
  - `reports/lab-summary/day35_vrrp_failover_validation.txt`

## Expected Topology

- lab01 LAN IP: `192.168.88.2`
- lab02 LAN IP: `192.168.88.3`
- VRRP VIP: `192.168.88.99`
- Automation PC LAN IP: `192.168.88.100`
- LAN server IP: `192.168.88.254`
- VRID: `88`
- Virtual MAC: `00:00:5E:00:01:58`
- lab01 priority: `150`
- lab02 priority: `100`
- Baseline state: lab01 `MASTER`, lab02 `BACKUP`

## Workflow

1. Load the Day35 topology profile.
2. Run source-specific LAN ping from the Automation PC:
   - `ping -S 192.168.88.100 192.168.88.2`
   - `ping -S 192.168.88.100 192.168.88.3`
   - `ping -S 192.168.88.100 192.168.88.99`
   - `ping -S 192.168.88.100 192.168.88.254`
3. Collect read-only RouterOS evidence from lab01 and lab02.
4. Validate the baseline state.
5. Prompt the operator to disconnect lab01 LAN cable from the LAN switch.
6. Observe failover and confirm lab02 becomes `MASTER`.
7. Prompt the operator to reconnect lab01 LAN cable.
8. Observe recovery and record whether lab01 preemption back to `MASTER` was seen.
9. Generate JSON, HTML, and TXT reports.

## Notes

- The failover trigger is manual and external.
- Automation only observes and reports.
- Day34 remains a staged apply plan and safety gate; it does not trigger failover.
- The Windows LAN ping must use `ping -S 192.168.88.100 <target>`.
- The LAN server Windows firewall must allow ICMPv4 Echo from `192.168.88.0/24`.
