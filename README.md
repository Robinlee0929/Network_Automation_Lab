# Network Automation Lab

## Project Overview

Network Automation Lab is a Python-based lab automation project for validating network device configuration, connectivity, topology, and report output across a small multi-vendor lab.

A Python-based network automation and validation lab for MikroTik RouterOS, Cisco switch topology checks, iperf3 performance testing, regression checks, and local report visualization.

The v0.1 portfolio package covers Day 1 through Day 30 post-tag verification. The current project timeline also includes the v0.2 HA / VRRP planning and read-only precheck foundation:

- MikroTik baseline and post-reset validation
- MikroTik Day 2 setup workflow after reset
- MikroTik Day 3 post-setup validation
- MikroTik Day 4 multi-device baseline validation
- Cisco Catalyst switch topology validation
- Day 6 lab-level topology summary report
- Day 8 Router performance automation with iperf3
- Day 9 Router performance regression framework
- Day 10 Local dashboard for report visualization
- Day 11 Dashboard safe command execution and execution log viewer
- Day 12 WireGuard VPN client config export and throughput baseline automation
- Day 13 multi-router WireGuard Client-to-Site validation
- Day 14 unified lab runner and latest lab overview report
- Day 17 runner task catalog and local report visibility index
- Day 18 WireGuard runner safety layer
- Day 19 runner evidence index and portfolio finalization
- Day 20 runner report index and portfolio evidence cleanup
- Day 21 dashboard report viewer and evidence navigation
- Day 22 WireGuard runner documentation and safety review
- Day 23 runner safety metadata and RC readiness review
- Day 24 RC demo flow and portfolio walkthrough polish
- Day 25 v0.1 RC validation evidence
- Day 26 v0.1 release packaging and portfolio polish
- Day 28 portfolio evidence final review
- Day 29 v0.1 release tag preparation
- Day 30 v0.1 post-tag verification
- Day 31 HA / VRRP topology and safety planning
- Day 32 VRRP Read-only Precheck Runner
- Day 33 VRRP Topology Design + Dry-run Command Preview
- Day 34 VRRP Staged Apply Plan and Safety Gate
- Day 35 VRRP Failover Validation
- Day 36 VRRP Failover Evidence Review and Report Hardening
- Day 37 VRRP Report Regression and Evidence Snapshot Policy
- Day 38 Post-VRRP Milestone Review and v0.2 Scope Planning
- Day 39 VRRP Evidence Dashboard Integration
- Day 40 v0.2 Demo Readiness Review and Scope Lock
- Day 41 v0.2 Release Packaging

The project is designed as a practical QA Automation / SDET portfolio project for network infrastructure. It focuses on repeatable validation, structured test evidence, and readable JSON / HTML reports rather than one-off manual checks.

## Why This Project Exists

Network device setup is often validated manually with SSH sessions, screenshots, and copied command output. That works for a single check, but it is difficult to repeat, compare, or present as test evidence.

This project exists to turn a home lab network into an automated testing target:

- Replace manual CLI inspection with repeatable validation scripts.
- Convert device state into structured PASS / FAIL / WARNING evidence.
- Keep MikroTik and Cisco workflows separated but reportable at the lab level.
- Demonstrate automation engineering practices in a network infrastructure context.
- Produce portfolio-ready reports that show test scope, result status, and topology health.

## Key Features

- SSH-based validation for MikroTik RouterOS and Cisco IOS.
- Read-only validation workflows for baseline, post-setup, topology, and lab summary checks.
- MikroTik reset setup workflow with dry-run and conservative apply behavior.
- Multi-device MikroTik baseline validation using device profiles from `config.json`.
- Cisco switch topology validation using a separate Cisco config file.
- Lab-level topology summary based on existing JSON reports.
- WireGuard client config export and VPN throughput baseline evidence.
- JSON and HTML report output for device-level and lab-level evidence.
- Adapter-oriented structure for cross-platform baseline validation experiments.
- Password-safe workflow: runtime password prompts are used, and passwords are not written to reports.

## Supported Devices

| Device | Platform | Current Scope |
| --- | --- | --- |
| MikroTik hEX S 2025 | RouterOS | Reset setup, acceptance check, post-setup validation, multi-device baseline validation |
| Cisco WS-C2960CG-8TC-L | Cisco IOS | Read-only switch topology validation |

Cisco validation is read-only. It runs show commands for topology evidence and does not enter configuration mode, change VLANs, change ports, update IP settings, or save configuration.

## Current Progress Summary

| Day | Scope | Status |
| --- | --- | --- |
| Day 1 | MikroTik baseline acceptance checks | Complete |
| Day 2 | MikroTik reset auto setup workflow with dry-run/apply modes | Complete |
| Day 3 | MikroTik post-setup validation and per-device reports | Complete |
| Day 4 | MikroTik multi-device baseline validation and summary reports | Complete |
| Day 5 | Cisco switch topology validation | Complete |
| Day 6 | Lab-level topology summary generated from existing device reports | Complete |
| Day 7 | Documentation cleanup, user guide, topology notes, and portfolio packaging | Complete |
| Day 8 | RouterOS precheck and iperf3 router performance automation | Complete |
| Day 9 | Repeatable iperf3 router performance regression with JSON / HTML / TXT reports | Complete |
| Day 10 | Local dashboard for viewing reports and safe command examples | Complete |
| Day 11 | Dashboard safe command execution and execution log viewer | Complete |
| Day 12 | WireGuard VPN client config export and throughput baseline automation | Complete |
| Day 13 | Multi-router WireGuard Client-to-Site validation | Complete |
| Day 14 | Unified lab runner and latest lab overview report | Complete |
| Day 17 | Runner task catalog and report visibility index | Complete |
| Day 18 | WireGuard runner safety layer | Complete |
| Day 19 | Runner evidence index and portfolio finalization | Complete |
| Day 20 | Runner report index and portfolio evidence cleanup | Complete |
| Day 21 | Dashboard report viewer and evidence navigation | Complete |
| Day 22 | WireGuard runner documentation and safety review | Complete |
| Day 23 | Runner safety metadata and RC readiness review | Complete |
| Day 24 | RC demo flow and portfolio walkthrough polish | Complete |
| Day 25 | v0.1 RC validation evidence | Complete |
| Day 26 | v0.1 release packaging and portfolio polish | Complete |
| Day 28 | Portfolio evidence final review | Complete |
| Day 29 | v0.1 release tag preparation | Complete |
| Day 30 | v0.1 post-tag verification | Complete |
| Day 31 | HA / VRRP topology and safety planning | Complete |
| Day 32 | VRRP Read-only Precheck Runner | Complete |
| Day 33 | VRRP Topology Design + Dry-run Command Preview | Complete |
| Day 34 | VRRP Staged Apply Plan and Safety Gate | Complete |
| Day 35 | VRRP Failover Validation | Complete |
| Day 36 | VRRP Failover Evidence Review and Report Hardening | Complete |
| Day 37 | VRRP report regression guards and evidence snapshot policy | Complete |
| Day 38 | Post-VRRP milestone review and v0.2 scope planning; documentation/report-planning only with no new live test | Complete |
| Day 39 | VRRP evidence dashboard/report-index integration; report-only with no live test, SSH, or configuration change | Complete |
| Day 40 | v0.2 demo readiness review and scope lock; report-only with no live test, SSH, or configuration change | Complete |
| Day 41 | v0.2 release packaging; documentation/report-only with no live test, SSH, configuration change, voice/AI implementation, or tag creation | Complete |

## Lab Topology

![MikroTik + Cisco Lab Topology v0.2 Final](docs/assets/mikrotik-cisco-lab-topology-v0.2-final.png)

![Lab Topology Day 1-Day 6](docs/assets/lab_topology_day1_day6.png)

This lab uses a Windows Automation PC, a Cisco WS-C2960CG-8TC-L switch, two MikroTik hEX S 2025 routers, and an upstream ISP cable modem or home router. The v0.2 topology adds the HA / VRRP lab plan with VRID 88, VIP `192.168.88.99/32`, lab01 as the higher-priority master candidate, and lab02 as the backup candidate. The Automation PC runs the Python validation workflows, connects to devices over SSH only for explicitly read-only or guarded workflows, and generates JSON / HTML reports at both device and lab level.

More details:

- [User Guide](docs/user_guide.md)
- [Topology Notes](docs/topology.md)

## Project Architecture

The project is organized around small validation workflows that can be run independently and then summarized at the lab level.

```text
Runtime configs
  config.json
  config.cisco.json
  topology_profiles/day6_lab_topology.json

Device workflows
  MikroTik setup and validation scripts
  Cisco topology validation script

Shared parsing and adapter code
  parsers/
  adapters/
  core/

Reports
  reports/<device_name>/
  reports/day4_summary_report.*
  reports/day6_lab_topology_summary.*
```

The MikroTik path remains the stable primary workflow. The cross-platform structure under `core/` and `adapters/` supports the experimental baseline direction without replacing the existing scripts.

## Folder Structure

```text
.
├── adapters/
│   ├── cisco_ios.py
│   └── mikrotik_routeros.py
├── core/
│   ├── device_base.py
│   └── device_factory.py
├── docs/
│   ├── assets/
│   ├── cisco_topology_validation.md
│   ├── topology.md
│   └── user_guide.md
├── parsers/
│   ├── cisco_parser.py
│   └── mikrotik_parser.py
├── tests/
├── topology_profiles/
│   └── day6_lab_topology.json
├── cisco_topology_validation.py
├── day6_lab_topology_summary.py
├── experimental_cross_platform_baseline.py
├── mikrotik_day2_auto_setup.py
├── mikrotik_post_validation.py
├── mikrotik_day4_multi_device_baseline.py
├── topology_summary.py
├── config.example.json
├── config.cisco.example.json
├── requirements.txt
└── README.md
```

Generated runtime files such as `config.json`, `config.cisco.json`, `.venv/`, and `reports/` are local working files and should not be committed.

## Setup Guide

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create runtime config files from the public examples:

```powershell
Copy-Item config.example.json config.json
Copy-Item config.cisco.example.json config.cisco.json
```

Review local config files before running against lab devices:

- Keep MikroTik settings in `config.json`.
- Keep Cisco switch settings in `config.cisco.json`.
- Keep lab summary device mapping in `topology_profiles/day6_lab_topology.json`.
- Leave passwords empty when possible and enter them at runtime.
- Do not commit local config files that contain lab-specific values.

## How to Run

Run MikroTik Day 2 setup workflow:

```powershell
python mikrotik_day2_auto_setup.py --dry-run --device-name Hex-s-2025-lab01
python mikrotik_day2_auto_setup.py --device-name Hex-s-2025-lab01
```

Run MikroTik acceptance and post-setup validation:

```powershell
python mikrotik_acceptance_check.py --device-name Hex-s-2025-lab01
python mikrotik_post_validation.py --device-name Hex-s-2025-lab01
```

Run MikroTik Day 4 multi-device baseline validation:

```powershell
python mikrotik_day4_multi_device_baseline.py
```

Run Cisco switch topology validation:

```powershell
python cisco_topology_validation.py
```

Run Day 6 lab topology summary:

```powershell
python day6_lab_topology_summary.py
```

Run Day 8 iperf3 router performance automation:

```powershell
python performance_test.py
```

Run Day 9 router performance regression:

```powershell
python performance_regression.py --device-name Hex-s-2025-lab01 --direction LAN_TO_WAN_DNAT_REPLY --router-wan-ip 192.168.0.199 --lan-server-ip 192.168.88.254 --duration 40 --parallel 4 --omit 10 --runs 3 --threshold-mbps 800 --baseline-mbps 948 --regression-ratio 0.90
```

Compatibility aliases are also available:

```powershell
python mikrotik_setup.py
python mikrotik_auto_setup.py
python cisco_day5_topology_validation.py
python topology_summary.py
```

## Day 8 iperf3 Router Performance Automation

Day 8 validates router performance with iperf3 and records structured JSON / HTML evidence. The WAN-side PC runs `performance_test.py` and the iperf3 client. The LAN-side PC runs the iperf3 server.

Test topology:

```text
WAN PC 192.168.0.114
-> MikroTik Router WAN IP 192.168.0.199
-> DNAT TCP/5201
-> LAN PC 192.168.88.254
```

Start the LAN-side server:

```powershell
iperf3 -s
```

Example RouterOS DNAT rule:

```text
/ip firewall nat add chain=dstnat in-interface=ether1 protocol=tcp dst-port=5201 action=dst-nat to-addresses=192.168.88.254 to-ports=5201 comment="day8 iperf3 WAN to LAN dst-nat"
```

Example RouterOS firewall allow rule:

```text
/ip firewall filter add chain=forward in-interface=ether1 protocol=tcp dst-address=192.168.88.254 dst-port=5201 action=accept comment="day8 allow iperf3 WAN to LAN"
```

Confirm Router WAN IP on RouterOS:

```text
/ip address print
```

Interactive mode:

```powershell
python performance_test.py
```

WAN_TO_LAN_DNAT:

```powershell
python performance_test.py --device-name Hex-s-2025-lab01 --router-wan-ip 192.168.0.199 --lan-server-ip 192.168.88.254 --direction WAN_TO_LAN_DNAT --router-host 192.168.0.199 --router-username admin
```

LAN_TO_WAN_DNAT_REPLY:

```powershell
python performance_test.py --device-name Hex-s-2025-lab01 --router-wan-ip 192.168.0.199 --lan-server-ip 192.168.88.254 --direction LAN_TO_WAN_DNAT_REPLY --router-host 192.168.0.199 --router-username admin
```

Skip RouterOS precheck:

```powershell
python performance_test.py --device-name Hex-s-2025-lab01 --router-wan-ip 192.168.0.199 --lan-server-ip 192.168.88.254 --direction WAN_TO_LAN_DNAT --skip-router-precheck
```

Important Day 8 notes:

- `router_wan_ip` is the IP that the iperf3 client actually connects to.
- `lan_server_ip` is the LAN PC that runs `iperf3 -s`.
- `WAN_TO_LAN_DNAT` measures DNAT forward throughput from the WAN-side client to the LAN iperf3 server.
- `LAN_TO_WAN_DNAT_REPLY` uses iperf3 `-R` reverse mode over the same DNAT connection. It is reply-direction throughput, not a standard outbound LAN-to-WAN SRCNAT test.
- `-O 10` excludes the first 10 seconds as warm-up.
- The default test duration is 40 seconds, with the first 10 seconds omitted from throughput calculation.
- Throughput Mbps is the primary Day 8 performance evidence.
- The default threshold is 800 Mbps.
- The default warning threshold is 700 Mbps. Results between 700 and 800 Mbps are WARN, not DUT FAIL.
- If required parameters are missing, the script asks for them in PowerShell.
- Day 8 uses SSH for RouterOS precheck by default.
- The first RouterOS precheck version is read-only and does not modify RouterOS.
- If DNAT or firewall filter allow rules are missing, the script provides suggested MikroTik commands.

A true `LAN_TO_WAN_SRCNAT` test requires the iperf3 client to be on the LAN side and the iperf3 server to be on the WAN side. Example topology: LAN PC `192.168.88.x` -> Router -> WAN PC `192.168.0.114` running `iperf3 -s`. The command from the LAN side would be `iperf3 -c 192.168.0.114 -t 40 -P 4 -O 10 -J`, and RouterOS connection tracking should show `s = SRCNAT`. This should be implemented separately and not mixed with DNAT reverse mode.

Day 8 final evidence:

- The original router throughput failure was isolated to endpoint baseline instability, not the MikroTik DNAT path.
- Root cause: `192.168.0.11` used a Realtek RTL8156 USB 2.5GbE adapter with driver `11.19.602.2025`, which caused unstable PC-to-PC reverse baseline throughput of about 772 to 785 Mbps.
- After updating the Realtek RTL8156 driver to `1156.22.20.113`, repeated 180-second PC-to-PC reverse baseline tests recovered to 948 Mbps.
- After the endpoint fix, `LAN_TO_WAN_DNAT_REPLY` passed with 946.35 Mbps against the 800 Mbps threshold.
- Final status: host baseline `PASS`, endpoint issue `FIXED`, DNAT reply-direction `PASS`, router issue `NOT REPRODUCED`.

Day 8 report output:

```text
reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.json
reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.html
reports/Hex-s-2025-lab01/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.json
reports/Hex-s-2025-lab01/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.html
```

Day 8 HTML report uses a dashboard-style layout for portfolio presentation.

## Day 9 Router Performance Regression Framework

Day 9 upgrades the Day 8 single-run iperf3 validation into a repeatable router performance regression framework. It runs the same iperf3 scenario multiple times, compares each run against a required threshold and an optional baseline, calculates aggregate statistics, and writes stable JSON / HTML / TXT reports for later review.

Day 9 keeps Day 8 behavior intact. Day 8 remains the router performance automation and RouterOS precheck workflow; Day 9 focuses on repeatable regression detection and report generation.

Supported directions:

- `WAN_TO_LAN_DNAT`
- `LAN_TO_WAN_DNAT_REPLY`
- `LAN_TO_WAN_ROUTING`

Example command:

```powershell
python performance_regression.py --device-name Hex-s-2025-lab01 --direction LAN_TO_WAN_DNAT_REPLY --router-wan-ip 192.168.0.199 --lan-server-ip 192.168.88.254 --duration 40 --parallel 4 --omit 10 --runs 3 --threshold-mbps 800 --baseline-mbps 948 --regression-ratio 0.90
```

Generated Day 9 report paths:

```text
reports/Hex-s-2025-lab01/day9_performance_regression_report.json
reports/Hex-s-2025-lab01/day9_performance_regression_report.html
reports/Hex-s-2025-lab01/day9_performance_regression_report.txt
```

Result criteria with `--baseline-mbps`:

- `PASS`: throughput is greater than or equal to `threshold_mbps` and greater than or equal to `baseline_mbps * regression_ratio`.
- `WARNING`: throughput is greater than or equal to `threshold_mbps` but below `baseline_mbps * regression_ratio`.
- `FAIL`: throughput is below `threshold_mbps`.

Result criteria without `--baseline-mbps`:

- `PASS`: throughput is greater than or equal to `threshold_mbps`.
- `FAIL`: throughput is below `threshold_mbps`.
- `WARNING` is not used unless baseline comparison is available.

Overall result:

- `FAIL` if any run fails.
- `WARNING` if no run fails but at least one run warns.
- `PASS` if all runs pass.

`reports/` remains ignored and generated Day 9 JSON / HTML / TXT reports should not be committed. The fixed Day 9 JSON schema keeps the top-level keys `metadata`, `config`, `aggregate`, and `runs` for future dashboard aggregation.

## Day 10 Local Dashboard

Day 10 adds a local Web GUI prototype for viewing automation reports. It converts CLI-based automation outputs into a user-readable dashboard, improves demo usability, and keeps execution safe by separating report viewing from command execution.

Purpose:

- Local dashboard for viewing automation reports.
- Show report summary cards for MikroTik baseline, Cisco topology, lab topology summary, iperf3 performance, and performance regression.
- Show PASS / FAIL / WARNING / UNKNOWN status when the JSON report exposes a supported result field.
- Link to existing HTML reports under `reports/`.
- Show safe PowerShell-friendly commands that can be copied and run manually.

Install the dashboard dependency:

```powershell
pip install flask
```

Or install all project dependencies:

```powershell
pip install -r requirements.txt
```

Start the dashboard:

```powershell
python dashboard_app.py
```

Open the local dashboard:

```text
http://127.0.0.1:5000
```

Dashboard pages:

- `/` shows the report summary cards, including Day 9 performance regression visibility.
- `/reports` scans `reports/` recursively for JSON and HTML reports and works even when `reports/` is missing.
- `/commands` shows safe command execution controls, recent execution logs, and copyable command examples.

Current limitation:

- Day 10 dashboard is read/report-oriented.
- It does not execute router configuration commands.
- It does not run performance regression from the web UI.
- It does not run pytest from the web UI.
- Safe command execution is introduced separately in Day 11 with a strict allowlist.

## Day 11 Dashboard Safe Command Execution

Day 11 extends the local Flask dashboard with a safe command runner and execution log viewer. It keeps the Day10 report dashboard intact while adding a limited way to trigger approved local repository commands from the browser.

Safety model:

- The dashboard uses a strict allowlist registry in `dashboard_command_runner.py`.
- The UI never accepts arbitrary shell commands.
- Commands run with `subprocess.run()` argument lists and `shell=False`.
- Unknown command IDs are rejected.
- Missing scripts are marked unavailable instead of replaced with unrelated behavior.
- Commands have timeouts and failures are logged instead of crashing Flask.

Enabled dashboard commands:

- `python -m pytest`
- `python -m pytest tests`
- `python -m pytest tests/test_performance_regression.py`
- `python topology_summary.py`

`topology_summary.py` rebuilds `reports/day6_lab_topology_summary.json` and `.html` from existing report files. It does not rerun Day8 iperf3 or Day9 performance regression tests.

Listed but disabled by default:

- `python performance_regression.py`

The Day9 performance regression script needs explicit lab parameters such as device name, direction, router WAN IP, LAN iperf3 server IP, thresholds, and baseline values. Run it manually with those arguments instead of using a one-click dashboard action.

Forbidden from the dashboard:

- Router or switch SSH command execution.
- Password entry or credential collection.
- MikroTik or Cisco configuration apply workflows.
- Firewall, NAT, reboot, reset, or destructive device actions.
- Arbitrary command text boxes.

Start the dashboard:

```powershell
python dashboard_app.py
```

Open:

```text
http://127.0.0.1:5000/
```

Day 11 routes:

- `/commands` lists safe commands, run buttons, and recent logs.
- `POST /commands/<command_id>/run` executes only registered command IDs.
- `/commands/logs` lists previous command executions.
- `/commands/logs/<log_id>` shows stdout, stderr, status, exit code, and duration.
- `/ai-checklist` lists Day11 review items for confirming safe command execution behavior.

Execution logs are saved as JSON under:

```text
reports/execution_logs/
```

`reports/` is ignored by git, so generated execution logs should remain local.

New Day11 execution logs use the local system time for `started_at`, `finished_at`, and the timestamp prefix in `log_id`.

Run Day11 tests:

```powershell
python -m pytest tests/test_dashboard_command_runner.py tests/test_dashboard_app.py
```

## Day12 WireGuard VPN Automation

Day 12 automates WireGuard client config export and VPN throughput baseline validation for the MikroTik lab. It keeps the real WireGuard client `.conf` local, validates router-side state, checks tunnel connectivity after the client is active, and records forward/reverse iperf3 evidence in JSON and HTML reports.

Purpose:

- Export a Windows WireGuard client config from an existing MikroTik peer.
- Validate `wg0`, peer state, firewall rules, handshake, rx/tx, LAN reachability, TCP 5201, and iperf3 throughput.
- Keep secrets out of Git, reports, README, PRs, and dashboard pages.

Topology:

```text
WAN PC WireGuard Client 10.10.10.2
MikroTik hEX S wg0 10.10.10.1
LAN PC iperf3 Server 192.168.88.254
```

Manual baseline summary:

- WireGuard interface: `wg0`
- MikroTik wg0 IP: `10.10.10.1/24`
- Client IP: `10.10.10.2/32`
- Endpoint host: `192.168.0.199`
- LAN gateway: `192.168.88.1`
- LAN host / iperf3 server: `192.168.88.254`
- Forward iperf manual baseline: `201 Mbps`
- Reverse iperf manual baseline: `272 Mbps`

Run examples:

```powershell
python mikrotik_day12_wireguard_vpn_automation.py --device-name Hex-s-2025-lab01
```

```powershell
python mikrotik_day12_wireguard_vpn_automation.py --device-name Hex-s-2025-lab01 --expect-connected
```

```powershell
python mikrotik_day12_wireguard_vpn_automation.py --device-name Hex-s-2025-lab01 --run-iperf
```

```powershell
python mikrotik_day12_wireguard_vpn_automation.py --device-name Hex-s-2025-lab01 --conf-filename robin-laptop-day12.conf
```

For repeated runs, save a local non-secret Day12 config:

```powershell
python mikrotik_day12_wireguard_vpn_automation.py --device-name Hex-s-2025-lab01 --router-host 192.168.0.199 --conf-filename robin-laptop-day12.conf --save-config
```

Then run:

```powershell
python mikrotik_day12_wireguard_vpn_automation.py --config Set_WireguardVPN_config.json --run-iperf
```

Expected export path:

```text
exports/wireguard/<filename>.conf
```

Report paths:

```text
reports/<device_name>/day12_wireguard_vpn_automation_report.json
reports/<device_name>/day12_wireguard_vpn_automation_report.html
```

iperf3 examples:

```powershell
iperf3 -c 192.168.88.254 -t 40 -O 10 -P 4
```

```powershell
iperf3 -c 192.168.88.254 -t 40 -O 10 -P 4 -R
```

Safety notes:

- Do not upload `.conf` files to GitHub.
- Do not upload QR codes.
- Do not paste `PrivateKey` into README, reports, issues, PRs, or chat.
- `.conf` files contain the client `PrivateKey` and must stay local.
- Reports must show `PrivateKey` as `REDACTED`.
- Dashboard must not display full `.conf` content.
- `reports/`, `exports/`, `.conf`, and local secret config files must stay ignored.

Troubleshooting notes:

- If Windows WireGuard shows connected but MikroTik rx/tx is `0`, check the UDP `13231` input firewall rule before the final input drop rule.
- If `192.168.88.1` is reachable but `192.168.88.254` is not, check the LAN PC firewall and default gateway.
- If iperf3 TCP `5201` fails, check the LAN PC iperf3 server and Windows firewall.
- If `Endpoint` has a duplicated port, make sure `client-endpoint` is host only, not `host:port`, when building the MikroTik peer config.
- If `--run-iperf` fails, first verify:

```powershell
Test-NetConnection 192.168.88.254 -Port 5201
```

## Day13 Multi-router WireGuard Client-to-Site Validation

Day 13 validates that the Day 12 WireGuard client-to-site workflow can be reused across multiple MikroTik routers with independent LAN and WireGuard subnets. It is not site-to-site VPN, router-to-router VPN, or hub-and-spoke VPN.

Initial targets:

- `Hex-s-2025-lab01`: LAN `192.168.88.0/24`, WireGuard `10.10.10.0/24`, client `10.10.10.2/32`.
- `Hex-s-2025-lab02`: LAN `192.168.89.0/24`, WireGuard `10.10.20.0/24`, client `10.10.20.2/32`.

![Day13 WireGuard VPN and iperf3 topology](docs/assets/day13-wireguard-iperf3-topology.png)

Profile and wrapper:

```text
topology_profiles/day13_wireguard_client_to_site_profiles.json
mikrotik_day13_multi_router_wireguard_validation.py
```

Run static profile validation and aggregate reporting:

```powershell
python mikrotik_day13_multi_router_wireguard_validation.py --profile topology_profiles/day13_wireguard_client_to_site_profiles.json
```

Run live WireGuard validation:

```powershell
python mikrotik_day13_multi_router_wireguard_validation.py --profile topology_profiles/day13_wireguard_client_to_site_profiles.json --run-live-validation
```

Run live WireGuard validation with iperf3:

```powershell
python mikrotik_day13_multi_router_wireguard_validation.py --profile topology_profiles/day13_wireguard_client_to_site_profiles.json --run-live-validation --run-iperf
```

Run single-device live validation with iperf3:

```powershell
python mikrotik_day13_multi_router_wireguard_validation.py --profile topology_profiles/day13_wireguard_client_to_site_profiles.json --devices Hex-s-2025-lab01 --run-live-validation --run-iperf
```

`--run-day12` remains available as a backward-compatible alias for `--run-live-validation`.
When multiple devices are selected for live validation, Day 13 reminds you before each next router to move the physical router cable and activate that router's WireGuard client config.

Future lab03/lab04/lab05 profiles should follow the same subnet rule: labNN uses `10.10.(NN*10).0/24`, router WireGuard IP `.1/24`, and Windows client WireGuard IP `.2/32`.

Safety notes:

- Do not commit exported `.conf` files.
- Do not commit generated reports under `reports/`.
- Day 13 timestamped summary snapshots that are intentionally safe to share belong under `summary/`, not `reports/`, when committed as documentation artifacts.
- Do not commit local config files.
- Day 13 reports show exported config paths only; they do not read or render WireGuard `.conf` content.

## Day14 Unified Lab Runner and Report Index

Day14 adds a unified entry point for lab-level tasks and a report index that builds a latest overview from existing JSON reports. It is designed as a portfolio-friendly summary layer and as a foundation for future dashboard integration.

Purpose:

- List implemented and planned lab automation tasks from one command.
- Dry-run the report index so you can see which files will be checked.
- Generate a latest lab overview JSON and HTML page from existing reports.
- Keep live device validation in the existing day-specific scripts.

What it does:

- Reads report paths from `topology_profiles/day14_lab_runner_profile.json`.
- Normalizes common report result fields such as `overall_result`, `result`, `status`, `passed`, and nested summary result fields.
- Handles missing or malformed report JSON without crashing.
- Creates a human-readable HTML overview with links to existing HTML reports.

What it does not do:

- Day14 report-index does not connect to routers.
- It does not run WireGuard validation.
- It does not run iperf3.
- It does not replace Day2 through Day13 scripts.
- Use Day13 `--run-live-validation --run-iperf` first if fresh WireGuard performance data is needed.

Commands:

Interactive safe menu:

```powershell
python network_lab.py
```

```powershell
python network_lab.py --interactive
```

The interactive menu can run `report-index` directly because it only reads local reports and writes the overview. Day4 and Day8 are guarded live tasks that ask for confirmation before delegation. The WireGuard runner uses stable feature-based CLI names and is dry-run by default.

```powershell
python network_lab.py --list-tasks
```

```powershell
python network_lab.py --task report-index --dry-run
```

```powershell
python network_lab.py --task report-index
```

```powershell
python network_lab.py --task report-index --profile topology_profiles/day14_lab_runner_profile.json
```

WireGuard runner dry-run:

```powershell
python network_lab.py --task wireguard-runner --dry-run
```

Blocked WireGuard live example:

```powershell
python network_lab.py --task wireguard-runner
```

Guarded WireGuard live flag:

```powershell
python network_lab.py --task wireguard-runner --allow-live-wireguard
```

Console output uses colored status labels in supported terminals. Set `NO_COLOR=1` if you need plain text output for logs or copy/paste.

Open the generated HTML overview:

```powershell
start reports\lab-summary\latest_lab_overview.html
```

Output files:

```text
reports/lab-summary/latest_lab_overview.json
reports/lab-summary/latest_lab_overview.html
```

`reports/` is ignored by git, so generated Day14 overview output should remain local and should not be committed.

## Day17 Runner Task Catalog and Report Visibility

Day17 cleans up the unified runner as a safer platform entry point. It improves task catalog visibility, adds safety classification, and generates a local report visibility index without adding WireGuard live execution.

List unified runner tasks:

```powershell
python network_lab.py --list-tasks
```

Generate the Day17 report visibility index:

```powershell
python network_lab.py --report-index
```

Open the generated HTML index:

```powershell
start reports\report_index.html
```

Safety levels:

| Safety level | Meaning |
| --- | --- |
| report-only | Local report viewing, summary generation, dry-run output, or existing report indexing. |
| read-only | Live device checks that read state without changing configuration. |
| guarded-live | Live validation delegated only after explicit runner action, confirmation, or guard flag. |
| dry-run | Planned-action preview that does not connect to devices or start live checks. |
| disabled | Placeholder or blocked workflow that is intentionally not available from the runner. |

Day17 report visibility behavior:

- `--list-tasks` prints task ID, day, display name, category, safety level, enabled state, execution mode, live-device requirement, related script, and report paths.
- `--report-index` scans local report paths and writes `reports/report_index.html`.
- Missing expected reports are shown as `MISSING` instead of crashing.
- Existing HTML reports are linked with relative paths when possible.
- Report visibility does not connect to devices, ask for SSH passwords, read `config.json`, or print secrets.
- WireGuard runner integration appears under a stable feature-based task name, while Day18 remains metadata and historical context.

Available guarded runner tasks still include:

```powershell
python network_lab.py --task day4-baseline
python network_lab.py --task iperf3-performance
```

## Day18 WireGuard Runner Safety Layer

Day18 adds the WireGuard Runner Safety Layer to the unified runner. The feature was added in Day18, but the CLI uses stable feature-based names so future users do not need to remember day numbers.

Primary dry-run command:

```powershell
python network_lab.py --task wireguard-runner --dry-run
```

Dry-run with an explicit lab02 WireGuard config:

```powershell
python network_lab.py --task wireguard-runner `
  --wireguard-config Set_WireguardVPN_lab02_config.json `
  --dry-run
```

Blocked live example with an explicit config:

```powershell
python network_lab.py --task wireguard-runner `
  --wireguard-config Set_WireguardVPN_lab02_config.json
```

Guarded live command with an explicit config:

```powershell
python network_lab.py --task wireguard-runner `
  --wireguard-config Set_WireguardVPN_lab02_config.json `
  --allow-live-wireguard
```

Guarded live validation with iperf3:

```powershell
python network_lab.py --task wireguard-runner `
  --wireguard-config Set_WireguardVPN_lab02_config.json `
  --allow-live-wireguard `
  --wireguard-run-iperf
```

Safety behavior:

- Dry-run does not connect to devices.
- Dry-run does not start WireGuard.
- Dry-run does not run ping or iperf.
- Dry-run does not enable VPN tunnels, modify firewall rules, reset routers, reboot routers, or apply config.
- `--wireguard-config` selects the Day12 WireGuard validation config file.
- If `--wireguard-config` is omitted, the runner uses the compatibility default `Set_WireguardVPN_config.json`.
- The selected config path is printed during dry-run, blocked live attempts, and guarded live execution.
- Live WireGuard execution requires explicit `--allow-live-wireguard`.
- Reports and console output must not disclose secrets.
- The runner omits unsafe Day12 flags such as `--recreate-peer` and `--apply-firewall-fixes`.
- The runner does not run iperf by default; use `--wireguard-run-iperf` with `--allow-live-wireguard` when throughput checks are intentionally requested.

Feature report paths:

```text
reports/lab-summary/wireguard_runner_safety_layer.json
reports/lab-summary/wireguard_runner_safety_layer.html
```

Day18 is a runner safety and summary layer. It does not replace `mikrotik_day12_wireguard_vpn_automation.py`; Day12 remains the detailed source of truth for WireGuard validation, exported config handling, tunnel checks, TCP 5201 checks, and iperf3 evidence.

When guarded live execution delegates to Day12, the Day18 runner report stays concise and links back to the Day12 source of truth. It includes the delegated Day12 JSON/HTML report paths, delegated result, final VPN connectivity status, handshake timing status, and iperf forward/reverse Mbps when those fields are available. It does not duplicate the full Day12 report or WireGuard config content.

The runner intentionally delegates only the safe Day12 validation path. Unsafe Day12 write flags such as `--recreate-peer` and `--apply-firewall-fixes` are not included in the runner command.

## Day19 Runner Evidence Index and Portfolio Finalization

Day19 closes the runner portfolio story with a local-only evidence index. It reads the task catalog and report visibility metadata, then writes a portfolio-ready JSON and HTML summary for final review, screenshots, and sharing.

Run the Day19 finalization:

```powershell
python network_lab.py --portfolio-finalize
```

Output files:

```text
reports/portfolio/day19_runner_evidence_index.json
reports/portfolio/day19_runner_evidence_index.html
```

Safety behavior:

- Does not connect to routers, switches, WireGuard clients, or iperf3 endpoints.
- Does not execute live workflow subprocesses.
- Does not read `config.json`, exported WireGuard `.conf` files, or secrets.
- Reuses report visibility metadata and links existing JSON / HTML evidence when present.
- Marks evidence quality as `READY`, `PARTIAL`, `GUARDED`, or `MISSING`.
- Keeps generated portfolio output under ignored `reports/` paths.

## Day20 Runner Report Index and Portfolio Evidence Cleanup

Day20 improves portfolio review clarity without adding new live actions. The report index now shows each evidence row with day, task name, report type, availability, safety label, report paths, and a short description. Missing files remain visible as unavailable evidence instead of causing failures.

See the concise portfolio review guide:

```text
docs/portfolio_evidence.md
```

## Day21 Dashboard Report Viewer and Evidence Navigation

Day21 extends the local Flask dashboard with a portfolio-friendly report viewer. The `/reports` page reuses the unified runner report visibility metadata, groups evidence by day, and shows report title, device or scope, report type, PASS / FAIL / WARN / UNKNOWN / MISSING status, JSON / HTML paths, and a short description.

Run the dashboard:

```powershell
python dashboard_app.py
```

Open the report viewer:

```text
http://127.0.0.1:5000/reports
```

Viewer behavior:

- HTML report links open only files under expected local evidence folders such as `reports/` and `summary/`.
- JSON report links show a readable, redacted preview without assuming every report uses the same schema.
- Missing reports show a clear not-generated-yet state instead of crashing.
- The viewer is read-only. It does not run live VPN validation, router resets, reboots, config changes, SSH commands, or iperf3 tests.

## Day22 WireGuard Runner Documentation and Safety Review

Day22 realigns the WireGuard runner story with the validation-first plan. The runner is a safety and evidence layer around the existing Day12 script, not a new VPN activation engine.

What the WireGuard runner can do:

- Produce a dry-run safety report showing the selected Day12 config, planned validation command, guardrail status, and report paths.
- Block accidental live execution unless `--allow-live-wireguard` is provided from the CLI or a separate interactive confirmation is accepted from the menu.
- When manually authorized, delegate to the existing Day12 validation script with fixed argv execution and without unsafe Day12 write flags.
- Summarize related Day12 evidence when the delegated Day12 JSON/HTML reports already exist.

What it intentionally cannot do:

- It does not automatically enable live VPN tunnels.
- It does not modify router firewall rules.
- It does not reset or reboot routers.
- It does not apply destructive configuration.
- It does not expose WireGuard private keys, `.conf` contents, SSH passwords, or local config secrets.

Evidence relationship:

- Day12 remains the detailed source of truth for WireGuard client config export, tunnel checks, TCP 5201 checks, and iperf3 evidence.
- Day13 summarizes multi-router WireGuard client-to-site validation and links Day12 report paths when available.
- Day18 records runner guardrails and delegated Day12 evidence without duplicating the Day12 report or reading exported `.conf` files.
- Day22 documents the safety boundary so Day25 v0.1 RC review can separate validation evidence from intentionally blocked live automation.

Review WireGuard evidence from the Day21 dashboard at `/reports`. Use grouped evidence cards, redacted JSON preview, and safe HTML report links for already-generated `reports/` or `summary/` evidence. Dashboard evidence browsing is read-only; it must not start live validation, activate VPN clients, apply config, reset routers, reboot routers, or reveal secrets.

## Day23 Runner Safety Metadata and RC Readiness Review

Day23 tightens runner metadata before the Day25 v0.1 RC. The task catalog in `network_lab.py` is the source of truth for user-facing task names, descriptions, safety level, execution mode, report outputs, and notes about dry-run, guarded-live, report-only, or disabled behavior.

Safety metadata is used by `--list-tasks`, report visibility, portfolio evidence, and reviewer documentation. `report-only` tasks read existing evidence, `read-only` tasks inspect live device state without config changes, `guarded-live` tasks require explicit action before delegation, `dry-run` tasks preview planned work, and `disabled` tasks are intentionally blocked from runner execution.

WireGuard runner metadata stays conservative: dry-run is the default posture, guarded live validation requires explicit authorization, and the runner does not add VPN activation, firewall apply logic, reset, reboot, or destructive behavior.

Day25 RC readiness checklist:

- Runner task metadata is complete.
- Safety labels and execution modes are consistent.
- Report outputs are traceable to Day8, Day12, Day13, Day18, Day21, and Day22 evidence or documentation.
- `/reports` viewer remains functional and read-only.
- WireGuard tasks remain dry-run or guarded-live only.
- No new destructive live behavior was introduced.
- Full `python -m pytest` suite passes.

Day25 v0.1 RC validation evidence is recorded in `docs/portfolio_evidence/day25_v0.1_rc_validation.md`.

## Day24 RC Demo Flow and Portfolio Walkthrough Polish

Day24 adds a report-only walkthrough artifact for RC review and portfolio demos. It turns the existing runner metadata, report visibility, dashboard viewer, WireGuard safety boundary, and portfolio evidence index into a clear reviewer path.

Generate the Day24 demo flow:

```powershell
python network_lab.py --task demo-flow
```

Output files:

```text
reports/portfolio/day24_rc_demo_flow.json
reports/portfolio/day24_rc_demo_flow.html
```

Recommended walkthrough order:

1. Open `README.md` to introduce the lab goal, supported devices, and Day1-Day24 scope.
2. Run `python network_lab.py --list-tasks --verbose` to show task safety metadata.
3. Run `python network_lab.py --report-index` and review `reports/report_index.html`.
4. Run `python dashboard_app.py` and open `http://127.0.0.1:5000/reports`.
5. Show `python network_lab.py --task wireguard-runner --dry-run` for the WireGuard guardrail boundary.
6. Open `reports/portfolio/day19_runner_evidence_index.html` and `reports/portfolio/day24_rc_demo_flow.html` for the closeout.

Safety behavior:

- Does not connect to routers, switches, WireGuard clients, or iperf3 endpoints.
- Does not execute live workflow subprocesses.
- Does not read `config.json`, exported WireGuard `.conf` files, or secrets.
- Leaves live validation behind the existing read-only, dry-run, guarded-live, or disabled runner controls.

## Day25 v0.1 RC Validation

Day25 records release-candidate validation for v0.1. It is documentation-only evidence that confirms the runner metadata, safety posture, demo-flow output, dashboard/report paths, ignored artifact posture, and full regression suite were ready for v0.1 review.

Evidence document:

```text
docs/portfolio_evidence/day25_v0.1_rc_validation.md
```

Recorded validation command:

```powershell
python -m pytest --basetemp=.pytest-tmp-day25-rc
```

Recorded result:

```text
401 passed in 1.94s
```

Day25 did not add product behavior, runner behavior, dashboard behavior, live VPN behavior, SSH execution behavior, generated reports, exports, real configs, caches, or secrets.

## Day26 v0.1 Release Packaging and Portfolio Polish

Day26 turns the Day25 RC into a v0.1 portfolio release package through documentation-only polish. It adds committed release notes and a concise portfolio checklist so reviewers can follow the existing README, runner metadata, report index, dashboard viewer, RC demo flow, and RC validation evidence without adding runner behavior.

Committed release docs:

```text
docs/portfolio_evidence/v0.1_release_notes.md
docs/portfolio_evidence/v0.1_portfolio_checklist.md
```

Safety behavior:

- Does not connect to routers, switches, WireGuard clients, or iperf3 endpoints.
- Does not add runner tasks, product features, or report generators.
- Does not read `config.json`, exported WireGuard `.conf` files, SSH passwords, private keys, or local secrets.
- Does not commit generated reports, exports, real configs, caches, or secrets.

## Day28 Portfolio Evidence Final Review

Day28 performs a documentation-only final review of the v0.1 portfolio evidence package. It aligns README scope, demo scripts, portfolio evidence notes, release notes, and safety wording so reviewers see one consistent v0.1 story.

Review focus:

- Clarify implemented v0.1 features versus future roadmap items.
- Keep demo flow centered on project goal, safe runner/task catalog, report visibility, portfolio evidence, and safety boundaries.
- Treat `reports/` and `exports/` as local generated artifacts that are ignored by Git.
- Keep real configs, credentials, passwords, private keys, WireGuard `.conf` files, and environment-specific files out of committed evidence.
- Preserve the existing safe-runner behavior and avoid adding live VPN, HA, VRRP, failover, or new device-control logic.

## Day29 v0.1 Release Tag Preparation

Day29 prepares the v0.1 repository state for release tagging. It records the final tag checklist, validation command, safety posture, and release-tag handoff notes without creating generated reports or changing runner/dashboard behavior.

Evidence document:

```text
docs/portfolio_evidence/day29_v0.1_release_tag_preparation.md
```

Recommended final validation before creating the tag:

```powershell
python -m pytest --basetemp=.pytest-tmp-day29-tag
```

Day29 does not create the Git tag by itself. Create `v0.1` only after the Day29 documentation commit is complete and validation passes.

## Day30 v0.1 Post-tag Verification

Day30 records the observed local `v0.1` tag state after the Day29 release preparation handoff. It confirms the tag exists and points at the Day29 release preparation merge commit without creating, moving, deleting, or pushing tags.

Evidence document:

```text
docs/portfolio_evidence/day30_v0.1_post_tag_verification.md
```

Recorded verification command:

```powershell
git show --no-patch --format=fuller v0.1
```

Observed tag target:

```text
bc3dd01d27aab2ef34506d407a6d9a27da9b03f2
```

Day30 is documentation-only. It does not create generated reports, add runner or dashboard behavior, execute live workflows, read secrets, or change the `v0.1` tag.

## Day31 HA / VRRP Topology and Safety Planning

Day31 creates the v0.2 HA / VRRP planning foundation without adding VRRP automation, runner behavior, dashboard behavior, live configuration changes, generated reports, or secrets.

Review the planning docs:

```text
docs/roadmap/ha_vrrp_topology_plan.md
docs/roadmap/ha_vrrp_safety_model.md
```

## Day32 - VRRP Read-only Precheck Runner

Purpose: collect current HA/VRRP-related state without changing devices.

Safety: read-only only; blocks `add`, `set`, `remove`, `disable`, `enable`, `reboot`, and `reset-configuration` before any MikroTik command is sent.

Run the Day32 runner:

```powershell
python mikrotik_day32_vrrp_readonly_precheck.py
python network_lab.py --task day32-vrrp-precheck
```

Reports:

```text
reports/lab-summary/day32_vrrp_readonly_precheck.json
reports/lab-summary/day32_vrrp_readonly_precheck.html
reports/lab-summary/day32_vrrp_readonly_precheck.txt
```

Safety behavior:

- Day31 is classified as `documentation_only`.
- Day32 is classified as `read_only_with_report`.
- The Day32 runner sends only read-only MikroTik commands such as `/system identity print`, `/interface vrrp print detail`, `/ip address print detail`, `/ip route print detail`, bridge print commands, and `/export terse`.
- The runner does not deploy VRRP, change interfaces, change IP addresses, edit routes, edit firewall rules, disable services, reboot, or reset devices.
- If VRRP is not configured, the report records `VRRP not configured or command returned no entries` and keeps the run as readiness evidence rather than a deployment failure.

## Day33 - VRRP Topology Design + Dry-run Command Preview

Purpose: render the intended HA/VRRP topology and the RouterOS commands that a future guarded workflow would review, without connecting to devices.

Safety: safe dry-run only; no SSH, no credentials, no RouterOS command execution, no failover trigger, no reboot, no reset, and no interface state changes.

Run the Day33 dry-run:

```powershell
python mikrotik_day33_vrrp_topology_dry_run.py
python network_lab.py --task day33-vrrp-dry-run
```

Profile:

```text
topology_profiles/day33_vrrp_topology_dry_run.json
```

Reports:

```text
reports/lab-summary/day33_vrrp_topology_dry_run.json
reports/lab-summary/day33_vrrp_topology_dry_run.html
reports/lab-summary/day33_vrrp_topology_dry_run.txt
```

Safety behavior:

- Day33 is classified as `safe_dry_run`.
- The Day33 runner validates the MikroTik + Cisco Lab Topology v0.2 values before rendering commands.
- Required VRRP values are VRID `88`, interface `vrrp-lan`, parent interface `bridge`, lab01 priority `150`, lab02 priority `100`, and VIP `192.168.88.99/32`.
- Physical LAN bridge IPs are lab01 `192.168.88.2/24` and lab02 `192.168.88.3/24`; the VIP must not equal either physical address.
- Required command preview for lab01 is `DRY-RUN: /interface vrrp add name=vrrp-lan interface=bridge vrid=88 priority=150 preemption-mode=yes` and `DRY-RUN: /ip address add address=192.168.88.99/32 interface=vrrp-lan`.
- Required command preview for lab02 is `DRY-RUN: /interface vrrp add name=vrrp-lan interface=bridge vrid=88 priority=100 preemption-mode=yes` and `DRY-RUN: /ip address add address=192.168.88.99/32 interface=vrrp-lan`.
- Previewed RouterOS commands are configuration-changing by nature, but they are text output only.
- The runner blocks destructive preview keywords such as `remove`, `disable`, `enable`, `reboot`, and `reset-configuration`.
- The runner does not read `config.json`, open SSH, send commands, deploy VRRP, or modify live lab state.

## Day34 - VRRP Staged Apply Plan and Safety Gate

Purpose: convert the Day33 dry-run preview into a staged backup-then-primary apply plan with a safety gate, while still blocking live execution.

Safety: blocked plan-only gate; no SSH, no credentials, no RouterOS command execution, no failover trigger, no reboot, no reset, and no interface state changes.

Run the Day34 staged plan:

```powershell
python mikrotik_day34_vrrp_staged_apply_plan.py
python network_lab.py --task day34-vrrp-staged-plan
```

Profile:

```text
topology_profiles/day34_vrrp_staged_apply_plan.json
```

Reports:

```text
reports/lab-summary/day34_vrrp_staged_apply_plan.json
reports/lab-summary/day34_vrrp_staged_apply_plan.html
reports/lab-summary/day34_vrrp_staged_apply_plan.txt
```

Safety behavior:

- Day34 is classified as `blocked_guarded_live_plan` in the report and `dry-run` in the runner task catalog.
- The Day34 safety gate checks for Day32 read-only precheck evidence and Day33 dry-run evidence.
- Missing Day32 or Day33 evidence keeps the overall Day34 result as `BLOCKED`.
- The staged plan previews backup router VRRP commands before primary router VRRP commands.
- Rollback commands are rendered as scoped preview text only and are not executed.
- Manual operator confirmation and live execution remain blocked in the Day34 report.
- The runner does not read `config.json`, open SSH, send commands, deploy VRRP, or modify live lab state.

## Day35 - VRRP Failover Validation

Purpose: safely prove that lab02 takes over the VRRP VIP when lab01 has a manual LAN-side failure.

Safety: controlled failover observation; automation collects evidence and reports, while the operator manually disconnects/reconnects the lab01 LAN cable from the LAN switch.

Run Day35:

```powershell
python mikrotik_day35_vrrp_failover_validation.py
python network_lab.py --task day35-vrrp-failover-validation
```

Profile:

```text
topology_profiles/day35_vrrp_failover_validation.json
```

Reports:

```text
reports/lab-summary/day35_vrrp_failover_validation.json
reports/lab-summary/day35_vrrp_failover_validation.html
reports/lab-summary/day35_vrrp_failover_validation.txt
```

Safety behavior:

- Day35 is classified as `controlled_failover_observation`.
- Day35 is not a configuration day and does not modify RouterOS configuration.
- The failover trigger is manual and external: disconnect lab01 LAN from the switch, then reconnect it when prompted.
- Automation uses `ping -S 192.168.88.100 <target>` for LAN reachability checks.
- RouterOS evidence collection is limited to read-only `print` commands.
- Interface enable/disable, firewall/NAT modification, IP address changes, VRRP changes, reboot, reset, and automatic failure injection are blocked.
- The LAN server firewall must allow ICMPv4 Echo from `192.168.88.0/24`.

Completion summary:

- Day35 live VRRP failover validation result: `PASS`.
- Manual lab01 LAN disconnect/reconnect was the only failover trigger.
- Automation remained read-only, and RouterOS configuration modification commands stayed blocked.
- lab01 started as `MASTER`; lab02 started as `BACKUP`.
- VRRP VIP remained reachable through failover.
- Operator guidance includes Step 1/2, Step 2/2, countdown, and progress messages.
- Latest validated commit: `6513bba`.

## Day36 - VRRP Failover Evidence Review and Report Hardening

Purpose: review the existing Day35 VRRP live validation evidence and make the generated reports, report index visibility, and portfolio traceability easier to review.

Safety: documentation and report hardening only. Day36 did not run new VRRP failover testing, did not inject a new fault, did not connect to MikroTik routers for live validation, and did not change router configuration.

Reviewed Day35 evidence:

```text
reports/lab-summary/day35_vrrp_failover_validation.json
reports/lab-summary/day35_vrrp_failover_validation.html
reports/lab-summary/day35_vrrp_failover_validation.txt
```

Day36 hardening:

- Day35 report generation now includes a concise evidence summary for initial master, backup router, failover trigger, observed failover result, recovery result, overall result, and limitations.
- The report explicitly states that convergence was validated by observed VRRP role transition and connectivity recovery, but exact convergence timing was not measured in Day35.
- The report index can infer PASS from Day35 `overall_status` metadata.
- Portfolio evidence documentation links Day35 validation evidence with the Day36 hardening note.
- No raw generated reports are required for source control; reports remain local generated evidence.

Roadmap note:

```text
docs/roadmap/day36_vrrp_failover_evidence_review_report_hardening.md
```

## Day37 - VRRP Report Regression and Evidence Snapshot Policy

Purpose: protect the Day35 and Day36 VRRP evidence chain with offline regression tests and a clear evidence snapshot policy.

Safety: regression and documentation only. Day37 did not perform new VRRP failover testing, did not unplug cables, did not connect to MikroTik routers for new validation, did not modify RouterOS configuration, and did not commit full runtime reports.

Day35-Day37 chain:

- Day35: VRRP live failover validation completed with a manual external failure trigger and read-only evidence collection.
- Day36: VRRP evidence summary and report hardening completed.
- Day37: Regression guards and evidence snapshot policy added.

Day37 regression coverage:

- Protects the Day35 report summary contract with fixture/sample JSON.
- Confirms report-index result detection handles `overall_status`, `status`, and missing or unknown status fields without crashing.
- Keeps runtime evidence under `reports/` local unless a small sanitized snapshot is intentionally selected for a milestone.

Roadmap note:

```text
docs/roadmap/day37_vrrp_report_regression_evidence_policy.md
```

## Day38 - Post-VRRP Milestone Review and v0.2 Scope Planning

Purpose: consolidate the Day31-Day37 HA / VRRP milestone before choosing the next v0.2 direction.

Safety: documentation and report-planning only. Day38 adds no new live test, no RouterOS configuration change, no SSH write command, no interface disable/enable automation, no reboot/reset automation, and no new iperf3 live run requirement.

Day38 review focus:

- Summarizes completed Day31-Day37 VRRP planning, precheck, dry-run, failover validation, report hardening, and regression evidence policy.
- Inventories committed planning evidence and marks local generated report paths as items to verify.
- Identifies remaining gaps such as manual physical failover trigger, limited topology variants, and need for a clearer v0.2 feature boundary.
- Compares candidate v0.2 directions including VRRP dashboard integration, multi-device read-only state collection, portfolio demo packaging, and AI-assisted summaries from existing reports only.
- Recommends a conservative v0.2 scope centered on read-only collection, report visibility, dashboard integration, and portfolio-ready HA / VRRP demo material.

Roadmap note:

```text
docs/roadmap/day38_post_vrrp_milestone_review_and_v0_2_scope_planning.md
```

## Day39 - VRRP Evidence Dashboard Integration

Purpose: integrate Day31-Day38 HA / VRRP docs, diagrams, profiles, generated reports, evidence policy, and milestone planning into the local dashboard and report index.

Safety: report-only and documentation/dashboard integration only. Day39 does not run live tests, open SSH sessions, require router credentials, start iperf3, trigger failover, or change MikroTik, Cisco, firewall/NAT, IP, VRRP, interface, reboot, reset, or topology settings.

Run Day39:

```powershell
python network_lab.py --task day39-vrrp-evidence-dashboard-integration
python network_lab.py --task report-index
```

Reports:

```text
reports/lab-summary/day39_vrrp_evidence_dashboard_integration.json
reports/lab-summary/day39_vrrp_evidence_dashboard_integration.html
```

v0.2 relevance: Day39 improves demo readiness and evidence traceability by making the HA / VRRP evidence chain visible from the dashboard `/reports` page, the generated report index, and the latest lab overview.

## Day40 - v0.2 Demo Readiness Review and Scope Lock

Purpose: lock the v0.2 demo scope, summarize the Day31-Day39 HA / VRRP milestone, and generate a portfolio-ready demo checklist and readiness report.

Safety: report-only and documentation-focused. Day40 does not run live tests, open SSH sessions, require credentials, start iperf3, trigger failover, or change MikroTik, Cisco, firewall/NAT, IP, VRRP, interface, reboot, reset, or topology settings.

Demo navigation command:

```powershell
python network_lab.py --task day40-v0.2-demo-readiness-review
```

Reports:

```text
reports/portfolio/day40_v0.2_demo_readiness_review.json
reports/portfolio/day40_v0.2_demo_readiness_review.html
```

Checklist:

```text
docs/portfolio_v0.2_demo_checklist.md
```

## Day41 - v0.2 Release Packaging

Purpose: prepare the v0.2 release package for Day31-Day40 HA / VRRP evidence, safety model, dashboard/report integration, and demo readiness. Day41 is report-only and documentation-only.

Safety: Day41 does not run live tests, open SSH sessions, require credentials, implement voice or AI features, change MikroTik, Cisco, firewall/NAT, IP, VRRP, interface, reboot, reset, or topology settings, or create a `v0.2` tag. The `v0.2` tag is reserved for Day42.

Release package:

```text
docs/releases/v0.2_release_package.md
docs/releases/v0.2_artifact_checklist.md
docs/portfolio/v0.2_demo_handoff_guide.md
```

Optional report-only packaging command:

```powershell
python network_lab.py --task day41-v0.2-release-packaging
```

Reports:

```text
reports/portfolio/day41_v0.2_release_packaging.json
reports/portfolio/day41_v0.2_release_packaging.html
```

## Portfolio Demo

v0.1 includes reviewer/interview demo scripts for presenting the current platform safely without adding features, changing runner/dashboard behavior, or running live device-changing workflows:

```text
docs/portfolio_demo_script.md
docs/portfolio_demo_script_zh-TW.md
```

## How to Read Reports

Reports are written as structured evidence for each workflow.

Common result meanings:

| Status | Meaning |
| --- | --- |
| PASS | The check matched the expected state. |
| FAIL | A required condition failed or a required report was missing. |
| WARNING | The device or lab is usable, but drift, missing optional evidence, or a non-blocking risk was found. |
| SKIP | The check was not applicable or lacked enough input to judge. |
| UNKNOWN | A source report did not expose a supported result field. |

JSON reports are useful for automation, regression comparison, and future RAG ingestion. HTML reports are intended for human review, screenshots, and portfolio demos.

When reading reports, start with:

1. Overall result or lab result.
2. Failed items and warning items.
3. Per-check expected and actual values.
4. Raw command output only when deeper troubleshooting is needed.

Passwords are not written to console output or report files.

## Sample Report Paths

MikroTik Day 2:

```text
reports/Hex-s-2025-lab01/day2_auto_setup_report.json
reports/Hex-s-2025-lab01/day2_auto_setup_report.txt
```

MikroTik Day 3:

```text
reports/Hex-s-2025-lab01/day3_test_report.json
reports/Hex-s-2025-lab01/day3_test_report.txt
```

MikroTik Day 4:

```text
reports/Hex-s-2025-lab01/day4_baseline_validation.json
reports/Hex-s-2025-lab01/day4_baseline_validation.html
reports/Hex-s-2025-lab02/day4_baseline_validation.json
reports/Hex-s-2025-lab02/day4_baseline_validation.html
reports/day4_summary_report.json
reports/day4_summary_report.html
```

Cisco Day 5:

```text
reports/cisco-switch/switch_topology_report.json
reports/cisco-switch/switch_topology_report.html
```

Day 6 lab summary:

```text
reports/day6_lab_topology_summary.json
reports/day6_lab_topology_summary.html
```

Day 8 iperf3 router performance:

```text
reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.json
reports/Hex-s-2025-lab01/day8_iperf3_WAN_TO_LAN_DNAT_report.html
reports/Hex-s-2025-lab01/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.json
reports/Hex-s-2025-lab01/day8_iperf3_LAN_TO_WAN_DNAT_REPLY_report.html
```

Day 9 router performance regression:

```text
reports/Hex-s-2025-lab01/day9_performance_regression_report.json
reports/Hex-s-2025-lab01/day9_performance_regression_report.html
reports/Hex-s-2025-lab01/day9_performance_regression_report.txt
```

Day 12 WireGuard VPN automation:

```text
reports/Hex-s-2025-lab01/day12_wireguard_vpn_automation_report.json
reports/Hex-s-2025-lab01/day12_wireguard_vpn_automation_report.html
```

Day 13 multi-router WireGuard Client-to-Site summary:

```text
reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary.json
reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary.html
reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary_YYYYMMDD_HHMMSS.json
reports/lab-summary/day13_multi_router_wireguard_client_to_site_summary_YYYYMMDD_HHMMSS.html
```

Day 19 portfolio evidence index:

```text
reports/portfolio/day19_runner_evidence_index.json
reports/portfolio/day19_runner_evidence_index.html
```

Day 24 RC demo flow:

```text
reports/portfolio/day24_rc_demo_flow.json
reports/portfolio/day24_rc_demo_flow.html
```

Day 25 v0.1 RC validation:

```text
docs/portfolio_evidence/day25_v0.1_rc_validation.md
```

Day 26 v0.1 release package:

```text
docs/portfolio_evidence/v0.1_release_notes.md
docs/portfolio_evidence/v0.1_portfolio_checklist.md
```

Day 29 v0.1 release tag preparation:

```text
docs/portfolio_evidence/day29_v0.1_release_tag_preparation.md
```

Day 30 v0.1 post-tag verification:

```text
docs/portfolio_evidence/day30_v0.1_post_tag_verification.md
```

Day31 HA / VRRP planning:

```text
docs/roadmap/ha_vrrp_topology_plan.md
docs/roadmap/ha_vrrp_safety_model.md
```

Day32 VRRP read-only precheck:

```text
reports/lab-summary/day32_vrrp_readonly_precheck.json
reports/lab-summary/day32_vrrp_readonly_precheck.html
reports/lab-summary/day32_vrrp_readonly_precheck.txt
```

Day33 VRRP topology dry-run:

```text
reports/lab-summary/day33_vrrp_topology_dry_run.json
reports/lab-summary/day33_vrrp_topology_dry_run.html
reports/lab-summary/day33_vrrp_topology_dry_run.txt
```

Day34 VRRP staged apply plan:

```text
reports/lab-summary/day34_vrrp_staged_apply_plan.json
reports/lab-summary/day34_vrrp_staged_apply_plan.html
reports/lab-summary/day34_vrrp_staged_apply_plan.txt
```

Day35 VRRP failover validation:

```text
reports/lab-summary/day35_vrrp_failover_validation.json
reports/lab-summary/day35_vrrp_failover_validation.html
reports/lab-summary/day35_vrrp_failover_validation.txt
```

Day37 VRRP evidence policy:

```text
docs/roadmap/day37_vrrp_report_regression_evidence_policy.md
```

Day38 post-VRRP milestone review and v0.2 scope planning:

```text
docs/roadmap/day38_post_vrrp_milestone_review_and_v0_2_scope_planning.md
```

Day39 VRRP evidence dashboard integration:

```text
reports/lab-summary/day39_vrrp_evidence_dashboard_integration.json
reports/lab-summary/day39_vrrp_evidence_dashboard_integration.html
```

Day40 v0.2 demo readiness review:

```text
docs/roadmap/day40_v0.2_demo_readiness_review.md
docs/portfolio_v0.2_demo_checklist.md
reports/portfolio/day40_v0.2_demo_readiness_review.json
reports/portfolio/day40_v0.2_demo_readiness_review.html
```

Day41 v0.2 release packaging:

```text
docs/releases/v0.2_release_package.md
docs/releases/v0.2_artifact_checklist.md
docs/portfolio/v0.2_demo_handoff_guide.md
reports/portfolio/day41_v0.2_release_packaging.json
reports/portfolio/day41_v0.2_release_packaging.html
```

## Testing Strategy

The project separates live-device validation from unit tests.

Live-device validation:

- Runs against MikroTik and Cisco devices over SSH.
- Produces JSON / HTML evidence under `reports/`.
- Confirms real lab behavior such as identity, firmware fields, WAN DHCP, LAN IP, SSH service state, switch model, port state, VLAN 1, MAC learning, and spanning-tree state.

Unit tests:

- Exercise parser logic, report normalization, config handling, and workflow behavior without requiring live devices.
- Protect expected behavior as scripts evolve.
- Avoid depending on real router or switch availability.

For documentation-only review passes, run `python -m pytest` before sharing the repository unless the local environment cannot provide Python or pytest.

## Portfolio Highlights

- Demonstrates network automation beyond simple command execution.
- Shows QA-style expected / actual / result reporting for infrastructure devices.
- Includes both router and switch validation in one lab story.
- Keeps vendor-specific runtime configs separated.
- Aggregates device-level reports into a lab-level topology summary.
- Uses password-safe report handling.
- Provides portfolio-friendly HTML output for demos and screenshots.
- Shows a clear growth path toward VPN, HA, performance, packet analysis, and AI-assisted reporting.
- Includes a final runner evidence index that ties task safety, report visibility, and portfolio readiness together.
- Includes a Day24 RC demo flow that gives reviewers a safe, repeatable walkthrough path.
- Includes v0.1 release notes and a portfolio checklist for documentation-only release review.
- Includes Day29 release tag preparation notes for final validation and tag handoff.
- Includes Day30 post-tag verification notes for local v0.1 tag traceability.
- Includes Day31 HA / VRRP planning docs for the v0.2 read-only precheck foundation.
- Includes Day32 VRRP read-only precheck evidence generation with a command safety guard.
- Includes Day33 VRRP topology design and dry-run command preview evidence without live execution.
- Includes Day34 VRRP staged apply planning and safety gate evidence without live execution.
- Includes Day35 VRRP controlled failover validation with manual external failure trigger and read-only evidence collection.
- Includes Day36 VRRP evidence summary/report hardening and Day37 offline regression guards plus evidence snapshot policy.
- Includes Day38 post-VRRP milestone review and conservative v0.2 scope planning without adding a new live test.
- Includes Day39 HA / VRRP evidence dashboard/report-index integration for safer v0.2 demo readiness.
- Includes Day40 v0.2 demo readiness review and scope lock without adding live tests, SSH, or device configuration changes.
- Includes Day41 v0.2 release packaging docs and report-only handoff while leaving `v0.2` tag creation for Day42.

## Roadmap

Planned future directions:

- Expanded VPN validation beyond the current guarded WireGuard evidence path
- HA / VRRP report visibility, read-only collection, and portfolio-ready demo packaging
- Additional performance scenarios beyond the current iperf3 workflows
- Syslog / packet capture analysis
- v3.0 Voice + AI Network Test Assistant / AI-assisted Network Test Orchestration as future roadmap only

v0.1 is packaged through Day29 and locally verified through Day30 as a portfolio release. Day41 prepares the first HA / VRRP milestone as a report-only v0.2 release package; Day42 owns `v0.2` tag preparation. Future work should stay explicit about whether it is report-only, read-only, dry-run, guarded-live, or disabled before adding new live lab behavior.
