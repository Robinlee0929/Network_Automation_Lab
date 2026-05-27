# Cisco Switch Topology Validation

## Goal

This workflow adds read-only SSH validation for a Cisco WS-C2960CG-8TC-L switch. It checks that the switch is reachable, that the expected model and management interface are present, that required ports are connected, and that VLAN, MAC learning, and spanning-tree state match the lab topology.

The script does not enter configuration mode, change VLANs, save configuration, reload the switch, or modify interfaces.

## MikroTik vs Cisco

| Stage | Target | Purpose | Output |
| --- | --- | --- | --- |
| MikroTik baseline | MikroTik routers | Multi-device RouterOS baseline validation | Per-router and summary reports |
| Cisco topology validation | Cisco switch | Switch topology validation | Cisco switch JSON and HTML report |

Cisco topology validation is a separate workflow. It does not reuse or change the MikroTik baseline behavior.

## Cisco Switch Information

| Field | Expected Value |
| --- | --- |
| Model | `WS-C2960CG-8TC-L` |
| Management IP | `192.168.0.111` |
| Device type | `cisco_ios` |
| SSH username | `admin` |
| Expected VLAN | `1` |
| Expected STP mode | `pvst` |
| Expected connected ports | `Gi0/1`, `Gi0/5`, `Gi0/7`, `Gi0/8` |

## Topology

The Windows Automation PC runs Python and connects to the Cisco switch by SSH on TCP/22.

```text
Automation PC
    |
    | SSH TCP/22
    |
Cisco WS-C2960CG-8TC-L
    Management: Vlan1 192.168.0.111
    Expected connected ports: Gi0/1, Gi0/5, Gi0/7, Gi0/8
    Expected VLAN: 1 active
```

## CLI Commands

The script runs only read-only Cisco IOS commands:

```text
show version
show ip interface brief
show interfaces status
show vlan brief
show mac address-table
show spanning-tree summary
```

## PASS / FAIL Standards

The run passes only when all required checks pass:

- SSH login succeeds.
- `show version` is readable.
- Switch model equals `WS-C2960CG-8TC-L`.
- IOS version is parsed.
- `show ip interface brief` is readable.
- `Vlan1` management IP equals `192.168.0.111` and is `up/up`.
- `show interfaces status` is readable.
- `Gi0/1`, `Gi0/5`, `Gi0/7`, and `Gi0/8` are `connected`.
- VLAN `1` is `active`.
- `show mac address-table` is readable.
- At least one dynamic MAC address is present.
- `show spanning-tree summary` is readable.
- `VLAN0001` blocking ports equals `0`.
- JSON and HTML reports are generated.

## Report Output Path

The script writes:

```text
reports/cisco-switch/switch_topology_report.json
reports/cisco-switch/switch_topology_report.html
```

The JSON report includes device metadata, check results, parsed command data, raw command outputs, and report paths. SSH passwords are never written to reports.

## Legacy SSH Notes

Cisco Catalyst 2960 switches may offer older SSH algorithms. The Cisco config includes:

```json
"legacy_ssh": true
```

When enabled, the Cisco adapter attempts legacy-compatible SSH key exchange, cipher, and host-key algorithms for old IOS devices. If SSH still fails, verify the switch SSH server settings and confirm the Python `paramiko` version can negotiate with the switch.

If you copy `config.cisco.example.json` to `config.cisco.json`, keep `password` empty for normal use. The script prompts for the SSH password at runtime. Cisco switch settings are intentionally separate from the MikroTik `config.json` used by the MikroTik workflows.

## Usage

```powershell
Copy-Item config.cisco.example.json config.cisco.json
python cisco_topology_validation.py
```

Or run directly against the public-safe Cisco example config:

```powershell
python cisco_topology_validation.py --config config.cisco.example.json
```
