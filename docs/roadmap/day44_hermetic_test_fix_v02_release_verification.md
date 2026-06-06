# Day44 - Hermetic Test Fix for v0.2 Release Verification

## Problem Summary

Day43 v0.2 release verification found that a fresh checkout could fail the Python regression suite on:

```text
tests/test_day12_wireguard_vpn_automation.py::test_existing_peer_is_not_removed_in_default_mode
```

The failure was:

```text
ValueError: Missing required non-interactive values: --router-host, --router-username
```

## Root Cause

The test passed `--device-name` and `--non-interactive`, but did not pass the router host or router username required by the Day12 non-interactive config builder.

In a local developer working tree, ignored `config.json` could provide those values, so the test passed accidentally. In a fresh checkout, `config.json` is absent by design, so the hidden dependency caused the test to fail.

## Fix Summary

Day44 makes the Day12 test path hermetic by supplying explicit fake non-live CLI values in the test:

- Router host: `192.0.2.10`
- Router username: `test-admin`
- Device name: `test-device`

The regression test changes the current working directory to an empty temporary directory and asserts that no local `config.json` exists. This proves the config-builder path no longer depends on an ignored private config file.

Day44 also hardens the Day12 fake runner helper so any unexpected RouterOS write command fails the test immediately. A regression test covers the existing-peer default-mode path and confirms the run does not generate or execute a remove command.

## Test Result

Targeted test command:

```powershell
python -m pytest tests/test_day12_wireguard_vpn_automation.py -q
```

Full test command:

```powershell
python -m pytest
```

Both commands passed during Day44 verification.

## Safety Confirmation

Day44 is a non-live test-only fix.

No SSH was run. No live network test was run. No connection was made to MikroTik, Cisco, router, switch, firewall, VPN, WireGuard peer, or iperf3 endpoint.

No router, switch, firewall, NAT, IP, VRRP, WireGuard, route, or interface configuration was changed.

No real credentials, real IP-dependent assumptions, private config files, or ignored `config.json` file were added.

The Day12 runtime safety behavior was not weakened. The fix is limited to hermetic tests and documentation.

Fresh checkout verification no longer depends on ignored `config.json` for this Day12 test path.
