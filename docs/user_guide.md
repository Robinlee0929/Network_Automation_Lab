# User Guide

This guide explains how to prepare and run the Network Automation Testing Platform for the current Day 1 through Day 6 scope.

## Environment Requirements

- Windows 10 or Windows 11 Automation PC
- Python 3.10 or newer
- Git
- Network access from the Automation PC to the lab devices
- SSH enabled on the target MikroTik and Cisco devices
- Project dependencies installed from `requirements.txt`

Supported lab devices:

- MikroTik hEX S 2025 running RouterOS
- Cisco WS-C2960CG-8TC-L running Cisco IOS

## Setup Steps

Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Create local runtime config files:

```powershell
Copy-Item config.example.json config.json
Copy-Item config.cisco.example.json config.cisco.json
```

Review each local config file before running live-device validation. Keep secrets out of committed files and enter passwords at runtime when prompted.

## config.json / config.cisco.json Preparation

Use `config.json` for MikroTik workflows.

Typical MikroTik values to review:

- `host`
- `port`
- `username`
- `device_name`
- `target_routeros_version`
- `expected`
- `devices`

Use `config.cisco.json` for Cisco switch topology validation.

Typical Cisco values to review:

- `host`
- `port`
- `username`
- `device_name`
- `expected_model`
- `expected_management_ip`
- `expected_connected_ports`
- `legacy_ssh`

Keep password fields empty when possible. The scripts prompt for credentials during execution and do not write passwords to reports.

## How to Run MikroTik Validation

Run the Day 2 reset setup workflow in dry-run mode first:

```powershell
python mikrotik_day2_auto_setup.py --dry-run --device-name Hex-s-2025-lab01
```

Run Day 2 apply mode only after reviewing the dry-run output:

```powershell
python mikrotik_day2_auto_setup.py --device-name Hex-s-2025-lab01
```

Run the MikroTik acceptance check:

```powershell
python mikrotik_acceptance_check.py --device-name Hex-s-2025-lab01
```

Run Day 3 post-setup validation:

```powershell
python mikrotik_post_validation.py --device-name Hex-s-2025-lab01
```

Run Day 4 multi-device baseline validation:

```powershell
python mikrotik_day4_multi_device_baseline.py
```

## How to Run Cisco Topology Validation

Create and review the Cisco runtime config:

```powershell
Copy-Item config.cisco.example.json config.cisco.json
```

Run Cisco switch topology validation:

```powershell
python cisco_topology_validation.py
```

The Cisco workflow is read-only. It collects show-command evidence and writes JSON / HTML reports.

## How to Run Day 6 Lab Summary

Run the lab summary after MikroTik Day 4 and Cisco Day 5 reports exist:

```powershell
python day6_lab_topology_summary.py
```

You can also use the compatibility alias:

```powershell
python topology_summary.py
```

The Day 6 summary reads existing JSON reports from the paths defined in `topology_profiles/day6_lab_topology.json`. It does not connect to devices.

## How to Read JSON / HTML Reports

Use JSON reports for structured evidence and future automation. Use HTML reports for manual review, demos, and portfolio screenshots.

Recommended reading order:

1. Check the overall result.
2. Review failed items.
3. Review warning items.
4. Compare expected and actual values.
5. Use raw command output only when troubleshooting is needed.

Common result meanings:

| Status | Meaning |
| --- | --- |
| PASS | The check matched the expected state. |
| FAIL | A required condition failed. |
| WARNING | A non-blocking risk, drift, or optional evidence issue was found. |
| SKIP | The check was not applicable or did not have enough data. |
| UNKNOWN | A source report did not expose a supported result field. |

## Common Troubleshooting

### SSH connection failed

- Confirm the device IP address is reachable from the Automation PC.
- Confirm SSH is enabled on the device.
- Confirm the configured SSH port is correct.
- For Cisco Catalyst 2960 devices, confirm whether legacy SSH algorithms are required.
- For MikroTik Day 4 WAN-side access, confirm the WAN SSH pre-check has been completed if needed.

### password incorrect

- Re-enter the runtime password carefully.
- Confirm the username matches the target device.
- Confirm the device account is allowed to log in through SSH.
- Keep passwords out of config files unless the local lab workflow explicitly requires otherwise.

### report path not found

- Confirm the required earlier workflow has been run.
- Confirm the report path in `topology_profiles/day6_lab_topology.json` matches the generated file.
- Confirm the device name used during the run matches the report folder name.

### device name mismatch

- Use the same `--device-name` value across setup, validation, and report review.
- Confirm the device profile exists under `devices` in `config.json`.
- Confirm Day 6 topology profile entries match the generated report folders.

### pytest failed

- Read the first failing test and error message before changing code.
- Confirm dependencies are installed in the active virtual environment.
- Confirm tests are being run from the project root.
- Separate parser or report-format failures from live-device connectivity issues.
- Do not use test failures as a reason to modify live config files or reports.
