# Network Automation Testing Platform

## Project Overview

Network Automation Testing Platform is a Python-based lab automation project for validating network device configuration, connectivity, topology, and report output across a small multi-vendor lab.

The current implementation covers Day 1 through Day 6:

- MikroTik baseline and post-reset validation
- MikroTik Day 2 setup workflow after reset
- MikroTik Day 3 post-setup validation
- MikroTik Day 4 multi-device baseline validation
- Cisco Catalyst switch topology validation
- Day 6 lab-level topology summary report

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

Compatibility aliases are also available:

```powershell
python mikrotik_setup.py
python mikrotik_auto_setup.py
python cisco_day5_topology_validation.py
python topology_summary.py
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
