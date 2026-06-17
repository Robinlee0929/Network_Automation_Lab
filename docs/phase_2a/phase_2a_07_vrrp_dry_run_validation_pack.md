# Phase 2A-07 VRRP Dry-Run / Mock Evidence Validation Pack

Phase 2A-07 validates local VRRP mock evidence only. It is dry-run,
mock-only, read-only, and report-only.

## Scope

The pack checks local evidence for:

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

Phase 2A-07 does not perform real VRRP testing. It does not connect to any
device and does not run device commands.

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

Phase 2A-07 implementation is authorized for this pack only.

- Phase 2B authorization: false
- next_phase_allowed: false

Run:

```bash
python network_lab.py --task phase2a-07-vrrp-dry-run-validation-pack
python -m pytest
python network_lab.py --report-index
```
