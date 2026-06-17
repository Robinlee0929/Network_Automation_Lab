# Phase 2A-07 Day1-Day160 Artifact-to-Jobs Dry-Run Validation Pack

Phase 2A-07 maps Day1-Day160 in-repo artifact patterns into candidate Phase 2A
Jobs. It is dry-run, mock-only, read-only, local-only, and report-only.

The VRRP validation pack remains included, but VRRP is now the first concrete
example Job rather than the whole Phase 2A-07 scope.

## Scope

The pack inspects prior repository artifact references such as README timeline
entries, roadmap documents, task/report registry entries, and local report path
patterns. It maps those patterns into candidate Jobs:

- `baseline_check`
- `interface_status_check`
- `wan_lan_check`
- `vrrp_validation`
- `backup_config_plan`
- `blocked_config_change_request`

Safe candidates are represented only as dry-run/mock/local/report-only Jobs.
Unsafe candidates are blocked or planning-only.

## Artifact-to-Jobs Mapping

| Job type | Source artifact pattern | Phase 2A-07 disposition |
| --- | --- | --- |
| `baseline_check` | Day1-Day4 baseline and multi-device baseline evidence | Safe dry-run/mock/local/report-only candidate |
| `interface_status_check` | Day5 topology and Day32 read-only interface/precheck evidence | Safe dry-run/mock/local/report-only candidate |
| `wan_lan_check` | Day8-Day13 WAN/LAN and performance evidence summaries | Safe dry-run/mock/local/report-only candidate |
| `vrrp_validation` | Day31-Day39 HA/VRRP planning, dry-run, blocked plan, and mock evidence | First concrete local mock validation Job |
| `backup_config_plan` | Day2/Day41 backup and release packaging references | Planning-only; blocked from execution |
| `blocked_config_change_request` | Day34, Day57, Day79, and Day160 blocked-change/next-phase evidence | Blocked non-executing Job candidate |

## VRRP Example Job

The `vrrp_validation` example checks local evidence for:

- expected VRRP group
- expected virtual IP
- expected active router
- expected standby router
- active priority greater than standby priority
- preempt setting
- interface state
- evidence freshness
- mismatch detection
- incomplete evidence detection

The local fixture is:

- `fixtures/phase_2a/phase_2a_07_vrrp_mock_evidence.json`

The generated reports are:

- `reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.json`
- `reports/lab-summary/phase_2a_07_vrrp_dry_run_validation_pack.html`

## Safety Boundary

Phase 2A-07 does not perform real VRRP testing or any other real network
operation. It does not connect to any device and does not run device commands.

The implementation keeps these capabilities disabled:

- SSH
- live device access
- NETCONF
- RESTCONF
- provider calls
- API calls
- model calls
- adapter execution
- broker execution
- runner execution
- secrets handling
- real network I/O
- real command execution
- real backup execution
- real failover testing
- config change logic
- custom script execution

## Unsafe Request Rejection

The negative regression matrix rejects live-oriented request shapes, including:

- SSH into a router
- live command collection such as VRRP show commands
- live failover tests
- VRRP priority changes
- interface shutdown or no-shutdown actions
- execution targets with credentials, host/IP, or port 22
- provider/API/model fields
- custom command or script fields

Rejected inputs are summarized with redacted field paths and stable references.
The report does not include raw unsafe values.

## Authorization Boundary

Phase 2A-07 implementation is authorized for this dry-run/mock artifact-to-Jobs
mapping pack only.

- Phase 2B authorization: false
- next_phase_allowed: false

Run:

```bash
python network_lab.py --task phase2a-07-vrrp-dry-run-validation-pack
python -m pytest
python network_lab.py --report-index
```
