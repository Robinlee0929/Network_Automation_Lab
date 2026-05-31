# Network Automation Lab

## Project Overview

Network Automation Lab is a Python-based lab automation project for validating network device configuration, connectivity, topology, and report output across a small multi-vendor lab.

A Python-based network automation and validation lab for MikroTik RouterOS, Cisco switch topology checks, iperf3 performance testing, regression checks, and local report visualization.

The current implementation covers Day 1 through Day 11:

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
- JSON and HTML report output for device-level and lab-level evidence.
- Adapter-oriented structure for cross-platform baseline validation experiments.
- Password-safe workflow: runtime password prompts are used, and passwords are not written to reports.

## Supported Devices

| Device | Platform | Current Scope |
| --- | --- | --- |
| MikroTik hEX S 2025 | RouterOS | Reset setup, acceptance check, post-setup validation, multi-device baseline validation |
| Cisco WS-C2960CG-8TC-L | Cisco IOS | Read-only switch topology validation |

Cisco validation is read-only. It runs show commands for topology evidence and does not enter configuration mode, change VLANs, change ports, update IP settings, or save configuration.

## Current Day 1-Day 6 Progress Summary

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

## Lab Topology

![Lab Topology Day 1-Day 6](docs/assets/lab_topology_day1_day6.png)

This lab uses a Windows Automation PC, a Cisco WS-C2960CG-8TC-L switch, two MikroTik hEX S 2025 routers, and an upstream ISP cable modem or home router. The Automation PC runs the Python validation workflows, connects to devices over SSH, and generates JSON / HTML reports at both device and lab level.

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

For this Day 7 documentation pass, tests were intentionally not run.

## Portfolio Highlights

- Demonstrates network automation beyond simple command execution.
- Shows QA-style expected / actual / result reporting for infrastructure devices.
- Includes both router and switch validation in one lab story.
- Keeps vendor-specific runtime configs separated.
- Aggregates device-level reports into a lab-level topology summary.
- Uses password-safe report handling.
- Provides portfolio-friendly HTML output for demos and screenshots.
- Shows a clear growth path toward VPN, HA, performance, packet analysis, and AI-assisted reporting.

## Roadmap

Planned future directions:

- VPN validation
- HA / failover validation
- Performance testing
- Syslog / packet capture analysis
- AI report summary / RAG integration

Day 7 is limited to documentation cleanup and portfolio packaging. No large feature work is planned for this phase.
