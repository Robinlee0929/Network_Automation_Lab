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
- Timestamped JSON report, for example `reports/day1/report_20260525_133500_PASS.json`
- Timestamped text report, for example `reports/day1/report_20260525_133500_PASS.txt`
- Latest-report aliases: `reports/day1/report.json` and `reports/day1/report.txt`

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

## Day 2 Reset Auto Setup

`mikrotik_day2_auto_setup.py` is the Day 2 workflow for a MikroTik hEX S 2025 after reset. It connects by SSH, checks RouterOS and RouterBOARD versions, optionally applies a conservative baseline, validates the result, and writes JSON and text reports.

Update `config.json` from `config.example.json`:

```json
{
  "host": "192.168.88.1",
  "port": 22,
  "username": "admin",
  "password": "",
  "device_name": "Hex-s-2025-lab01",
  "target_routeros_version": "7.22.3",
  "enable_apply_config": false,
  "enable_backup": true,
  "enable_report": true,
  "timezone": "Asia/Taipei",
  "disable_services": ["ftp", "telnet"]
}
```

Run:

```powershell
python mikrotik_day2_auto_setup.py
```

### Dry-Run vs Apply Mode

- `enable_apply_config: false` runs version checks, backup if enabled, validation commands, and report output. It lists the identity, timezone, NTP, and service commands that would be applied, but does not apply them.
- If dry-run finds a RouterOS package version mismatch, the console and text report include manual update guidance. The script still does not download, install, upgrade, or reboot automatically.
- `enable_apply_config: true` applies only the conservative Day 2 baseline:
  - `/system identity set name=<device_name>`
  - `/system clock set time-zone-name=<timezone>`
  - `/system ntp client set enabled=yes`
  - `/ip service disable [find name=<service>]` only for services listed in `disable_services`

The script never disables SSH, HTTP (`www`), or HTTPS (`www-ssl`). It does not change the admin password, delete users, reboot, import config, upgrade RouterOS packages, or run RouterBOARD firmware upgrade.

### Version and Firmware Checks

Day 2 checks but does not upgrade:

- `/system package print` is parsed for the `routeros` package version and compared with `target_routeros_version`.
- `/system routerboard print` is parsed for `current-firmware`, `upgrade-firmware`, and `factory-firmware`.
- If `current-firmware != upgrade-firmware`, the report shows `WARNING`; no `/system routerboard upgrade` or reboot is executed.

### Day 2 Reports

When `enable_report` is true, the script writes:

- `reports/day2/day2_auto_setup_report.json`
- `reports/day2/day2_auto_setup_report.txt`

The report includes SSH result, RouterOS package version, RouterBOARD firmware fields, backup/apply/validation results, executed commands, warnings, and errors. The SSH password is never written to console or report.

### Day 2 Acceptance Criteria

- `python mikrotik_day2_auto_setup.py` can run from this project folder.
- SSH failure stops configuration apply and is reported clearly.
- Dry-run mode does not apply identity, timezone, NTP, or service changes.
- Apply mode changes only identity, timezone, NTP, and services listed in `disable_services`.
- RouterOS `routeros` package version is parsed and written to report.
- RouterBOARD firmware fields are parsed and written to report.
- Firmware mismatch produces `WARNING` without upgrade or reboot.
- JSON and Markdown reports are generated when `enable_report` is true.
- `pytest` passes without a live MikroTik connection.
