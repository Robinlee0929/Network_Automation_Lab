# MikroTik Reset Baseline Check

Python automation for read-only acceptance checks after a MikroTik reset and baseline restore.

## Environment

- OS: Windows
- RouterOS device: MikroTik
- Router IP: `192.168.88.1`
- PC IP: `192.168.88.254`
- Login method: SSH
- Username: `admin`
- SSH port: `22`

The script asks for the SSH password at runtime. Press Enter at the password prompt to use the default value from `config.json`. Do not hard-code passwords in the Python source.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config.example.json config.json
```

Edit `config.json` if you want a default password for cases where you press Enter at the runtime password prompt.

## Tests

Run unit tests without connecting to MikroTik:

```powershell
pytest
```

## Usage

Provide a device name from the command line:

```powershell
python mikrotik_baseline_check.py --device-name hex-s-2025-lab01
```

Version 2 can also set the MikroTik `/system identity` to the device name. This is optional and only runs when `--set-identity` is provided:

```powershell
python mikrotik_baseline_check.py --device-name hex-s-2025-lab01 --set-identity
```

Or run without `--device-name` and enter it when prompted:

```powershell
python mikrotik_baseline_check.py
```

Prompt:

```text
Please input device name:
```

Password prompt:

```text
Please input SSH password (press Enter to use config.json default):
```

Without `--set-identity`, the device name is used only for console and report identification.

## Read-Only Commands

Baseline checks allow only these read-only commands:

```text
/system clock print
/system ntp client print
/ping 8.8.8.8 count=3
/file print
```

Blocked operations include reset, reboot, backup load, import, identity changes, and IP, firewall, bridge, or DHCP modifications.

Exception: Version 2 allows `/system identity set name=<device_name>` only through the explicit `--set-identity` option. Other write operations remain blocked.

## Acceptance Criteria

The run passes only when all checks pass:

- SSH login succeeds.
- `/system clock print` contains `time-zone-name: Asia/Taipei`.
- `/system clock print` contains `gmt-offset: +08:00`.
- `/system ntp client print` contains `enabled: yes`.
- `/system ntp client print` contains `status: synchronized`.
- `/ping 8.8.8.8 count=3` has `received > 0` or `packet-loss` is not `100%`.
- `/file print` contains `baseline-wan-ntp-ok.backup`.
- `/file print` contains `baseline-wan-ntp-ok.rsc`.

## Reports

The script writes:

- Console PASS / FAIL result
- Timestamped JSON report, for example `reports/report_20260525_133500_PASS.json`
- Timestamped text report, for example `reports/report_20260525_133500_PASS.txt`
- Latest-report aliases: `reports/report.json` and `reports/report.txt`

The console output also lists each check item and its PASS / FAIL result.

`report.json` contains:

```json
{
  "device_name": "<input device name>",
  "router_ip": "192.168.88.1",
  "ssh_port": 22,
  "overall_result": "PASS or FAIL",
  "checks": []
}
```

## Error Handling

The script reports failures for:

- SSH timeout
- Authentication failure
- Command timeout
- Unexpected RouterOS output format
