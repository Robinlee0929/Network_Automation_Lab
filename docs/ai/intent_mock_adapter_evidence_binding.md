# Mock Adapter + Evidence Binding

Day85 creates a deterministic mock adapter fixture that conforms to the Day84 read-only executor adapter interface contract and binds every mock response to reviewer evidence.

It remains mock-only, local, read-only, deterministic, and report-only. It does not introduce SSH, device access, live command execution, a real executor, AI API usage, approval unlock, execution unlock, POST routes, dashboard execution buttons, or mapped task execution.

## Purpose

Day84 defined the adapter interface contract. Day85 verifies a fixture can satisfy that contract without becoming a runtime adapter.

Each adapter record binds:

- request id
- adapter id
- Day84 contract reference
- evidence reference
- safety decision
- reviewer traceability fields

Compatible mock-style adapters may return deterministic fixture data, but they still cannot execute.

## Adapter Outcomes

Day85 validates these adapter outcomes:

| Adapter Type | Expected Result |
| --- | --- |
| mock adapter | compatible |
| replay adapter | compatible |
| evidence-only adapter | compatible |
| ssh adapter | blocked |
| live command adapter | blocked |
| AI executor adapter | blocked |
| approval unlock adapter | blocked |

Blocked adapters still generate an evidence trail, but always keep:

```json
{
  "allowed_to_execute": false,
  "ssh_allowed": false,
  "live_command_allowed": false,
  "approval_unlock_supported": false,
  "execution_unlock_supported": false
}
```

## Compatibility Matrix Scope

The Compatibility Matrix is internal Day85/Day86 validation evidence only.

It is included as a report section and deterministic test data so reviewers can verify compatible and blocked outcomes. It is not the Day85 topic and is not promoted to a standalone day.

## Reports

Run:

```bash
python network_lab.py --task mock-adapter-evidence-binding
```

Reports:

- `reports/lab-summary/day85_mock_adapter_evidence_binding.json`
- `reports/lab-summary/day85_mock_adapter_evidence_binding.html`

The HTML report is static and reviewer-facing. It contains no forms, POST actions, execution buttons, scripts, or live endpoints.

## Acceptance Criteria

Accept Day85 only if:

- every adapter response conforms to the Day84 response shape
- every response is bound to request id, contract reference, adapter fixture, and evidence reference
- mock, replay, and evidence-only adapters are compatible but non-executing
- SSH, live command, AI executor, and approval unlock adapters are blocked
- all execution, SSH, device, live command, AI API, approval unlock, and execution unlock flags remain false
- JSON and HTML reports are generated under `reports/lab-summary/`
- `python network_lab.py --task report-index` can still run
