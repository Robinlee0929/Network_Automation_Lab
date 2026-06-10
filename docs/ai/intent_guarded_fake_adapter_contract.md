# Day93 Guarded Fake Adapter Contract

Day93 adds deterministic audit evidence for the adapter boundary after the
Day92 executable guard layer.

This is fake-adapter-only. It does not unlock real adapter execution, SSH,
RouterOS/API use, live command execution, device access, or `config.json`
loading.

## Contract

Every scenario is evaluated by the guard first. Only scenarios with
`guard_result == ALLOWED` may enter the fake adapter boundary.

Rejected scenarios must keep:

- `adapter_invocation_attempted = false`
- `adapter_boundary_entered = false`
- `fake_adapter_invoked = false`
- `real_adapter_invoked = false`

Allowed scenarios must show:

- `adapter_invocation_attempted = true`
- `adapter_boundary_entered = true`
- `fake_adapter_invoked = true`
- `adapter_type = "fake"`
- `real_adapter_invoked = false`

## Safety Boundary

Day93 remains fully local and deterministic:

- no real device access
- no SSH
- no live command execution
- no real adapter invocation
- no `config.json` dependency
- no OpenAI API or AI SDK call
- no dashboard POST route, form, execution button, adapter toggle, or live
  execution endpoint

## Evidence

The generated report proves:

- allowed read-only scenarios invoke the fake adapter exactly once each
- rejected scenarios never reach the adapter boundary
- every adapter boundary invocation has an invocation id and response record
- guard ordering violations remain 0
- safety violations remain 0
- final recommendation remains `KEEP_FAKE_ONLY`

Reports:

- `reports/lab-summary/day93_guarded_fake_adapter_contract.json`
- `reports/lab-summary/day93_guarded_fake_adapter_contract.html`

Runner:

```bash
python network_lab.py --task guarded-fake-adapter-contract
```
