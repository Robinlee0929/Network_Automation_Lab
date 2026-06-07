# Day57 - Intent Mapping Prototype Artifact

This artifact defines a static, dry-run-only prototype for mapping user text to reviewed runner task proposals.

Day57 does not call OpenAI APIs, speech APIs, SSH, live runner tasks, devices, or `config.json`. It does not change NAT, IP, VRRP, WireGuard, firewall, route, interface, or device configuration.

## Prototype Mapping Examples

| User input | Intent | Mapped runner task | Safety level | Confirmation | Execution |
| --- | --- | --- | --- | --- | --- |
| Show me the latest reports | `view_reports` | `report-index` | `report_only` | Not required or low-risk confirmation only | Dry-run mapping only |
| Run the WireGuard check | `wireguard_status_or_validation_request` | `wireguard-runner` | `guarded_dry_run` | Required before any future live-capable path | Dry-run mapping only |
| Do VRRP failover test | `vrrp_failover_test_request` | `day35-vrrp-failover-validation` as a blocked/future guarded candidate | `guarded_live_candidate` | Mandatory | Blocked in Day57; dry-run mapping only |
| Open dashboard | `open_dashboard_or_report_view` | Dashboard / report viewer | `local_ui_only` | Not required | Dry-run mapping only |
| Make everything better | `unknown_or_ambiguous` | None | `needs_manual_review` | Manual review required | No task mapped; dry-run only |

## Reviewed Intent Object Shape

```json
{
  "normalized_user_input": "run the wireguard check",
  "detected_intent": "wireguard_status_or_validation_request",
  "mapped_allowlisted_task": "wireguard-runner",
  "safety_level": "guarded_dry_run",
  "confirmation_requirement": "required_before_any_future_live_capable_path",
  "execution_mode": "dry_run_only",
  "mapped_task_executed": false,
  "openai_api_used": false,
  "voice_control_used": false,
  "ssh_used": false,
  "device_connection_used": false,
  "config_json_read": false
}
```

## Blocked Actions

Every Day57 mapping blocks:

- OpenAI API calls.
- Speech or voice control.
- SSH sessions.
- Live runner delegation.
- MikroTik, Cisco, router, switch, firewall, VPN, or device connections.
- NAT, IP, VRRP, WireGuard, firewall, route, interface, or device configuration changes.

## CLI Prototype

The optional local CLI prototype is deterministic and dry-run-only:

```powershell
python network_lab.py --task intent-mapping-prototype --intent-text "show me the latest reports"
```

The command prints a mapping proposal only. It never executes the mapped runner task.
