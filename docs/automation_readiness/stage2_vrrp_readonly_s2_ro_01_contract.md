# S2-RO-01 minimal VRRP request and evidence contract

## Decision summary

**S2-RO-01 implements one immutable, protocol-neutral data contract for a future
MikroTik VRRP read-only observation. It is offline and ready only for
independent code review after validation.**

The module has no target registry, credential backend, authorization envelope,
Owner verifier, replay ledger, known-host acquisition, transport, RouterOS
parser, runtime composition, CLI registration, or live entrypoint.

`VALID S2-RO-01 CONTRACT != EXECUTION AUTHORIZATION`

`S2-RO-01 IMPLEMENTED OFFLINE != STAGE-2 LIVE ACCESS STARTED`

## Scope and fixed operation

The implementation is
`validation_framework.stage2_vrrp_readonly_contract`. It uses only the Python
standard library and recognizes one operation:

```text
mikrotik.vrrp_status
```

The identifier is retained from the reviewed historical Stage-2 design so
later bounded components do not require an operation-name translation. The
module does not contain or accept the RouterOS command that may eventually
implement the operation.

## Request contract

`Stage2VrrpObservationRequest` contains exactly:

| Field | Contract |
| --- | --- |
| `schema_version` | Exactly `1.0` |
| `operation_id` | Exactly `mikrotik.vrrp_status` |
| `run_id` | Bounded lowercase ASCII logical reference beginning `run.` |
| `target_ref` | Bounded lowercase ASCII logical reference beginning `target.` |
| `credential_ref` | Bounded opaque logical reference beginning `credential.` |
| `authorization_ref` | Bounded logical reference beginning `authorization.` |
| `read_only` | Exact Boolean `true` |

All logical references use one dotted lowercase ASCII grammar, are at most 160
characters, and reject whitespace, path separators, shell-style punctuation,
control characters, and Unicode confusables. Credential references additionally
reject material-shaped tokens such as `password`, `private-key`, `secret`, and
`token`.

The request has no command, endpoint, IP address, hostname, username, password,
key material, retry control, timeout override, output limit override, or bypass
flag. It uses an `authorization_ref`, not an authorization UUID: issuance,
signature, lifetime, and single-use identity belong to a later authorization
envelope slice and are deliberately not duplicated here.

The `execution_authorized` property is always `False`.

## Normalized evidence contract

`Stage2VrrpObservationEvidence` represents a successful normalized observation
only. It repeats the run, target, authorization, and fixed operation bindings,
then records:

- fixed command policy version `policy.stage2.vrrp-readonly.v1`;
- exact `attempt_count = 1`;
- exact `retry_count = 0`;
- duration from 1 through 60,000 milliseconds;
- raw-output byte count from 0 through 65,536;
- lowercase 64-hex SHA-256 for correlation without retaining raw output;
- zero through 32 immutable normalized VRRP records.

The SHA-256 field is correlation metadata, not proof that output was authentic,
complete, parsed correctly, or safe. Those checks belong to later transport and
parser slices.

The evidence schema cannot represent raw command output, a transcript, target
IP, credential material, raw host key, signing material, or arbitrary command.
Its `execution_authorized` property is always `False`; successful evidence does
not grant a second operation.

## VRRP record

Each `NormalizedVrrpRecord` contains only:

| Field | Bound |
| --- | --- |
| `instance_name` | NFC UTF-8 display text, 1-128 bytes, no control characters or surrounding whitespace |
| `vrid` | Integer 1-255 |
| `priority` | Integer 0-255 |
| `interval_ms` | Integer 1-255,000 |
| `version` | Integer `2` or `3` |
| `running` | Boolean |
| `role` | `MASTER`, `BACKUP`, `FAILURE`, or `UNKNOWN` |
| `disabled` | Boolean |
| `invalid` | Boolean |

Interval is normalized to milliseconds. This avoids binding evidence to
RouterOS presentation variants such as `1`, `1s`, or `1000ms`. S2-RO-01 does
not parse or interpret those source forms.

An empty record collection is valid normalized evidence for a complete future
observation in which no VRRP instances are configured. Later validation policy
may distinguish that state from parser failure; this contract cannot silently
turn malformed output into an empty observation.

## Serialization and immutability

The three public data types are frozen, slotted dataclasses. Construction and
parsing validate every field. Mutable input records and exported dictionaries
cannot alter an existing contract object.

Plain-record parsers require exact built-in `dict` and `list` containers,
reject missing and unknown fields, and perform no coercion or defaulting.
Canonical JSON parsers accept bounded raw `bytes`, strict UTF-8, compact sorted
keys, and byte-exact canonical reserialization. BOMs, whitespace variants,
trailing newlines, duplicate object keys, invalid constants, invalid UTF-8, and
oversized input fail closed.

## Failure boundary

This slice defines only two sanitized contract-validation categories:

```text
INVALID_REQUEST
INVALID_EVIDENCE
```

Target, credential, authorization, host-key, connection, command, parsing, and
cleanup failures are deferred because S2-RO-01 implements none of those
boundaries. Adding speculative runtime failure categories here would couple the
offline data contract to unauthorized later slices.

## Offline proof and forbidden scope

Focused tests cover exact valid objects, unsupported operations, false
read-only claims, malformed and overlong references, material-shaped credential
references, wrong types, unknown or secret-shaped fields, immutable state,
attempt/retry invariants, every numeric and collection bound, VRRP enums,
canonical JSON and duplicate-key rejection, input/output isolation, and safe
representations.

AST-based safety checks prove the module imports none of `socket`, `paramiko`,
`subprocess`, `ctypes`, `dns`, `os`, or `pathlib`, and exposes no connection,
execution, RouterOS parsing, or entrypoint function.

This slice does not authorize or implement S2-RO-02 or any later target,
credential, authorization, trust, transport, parser, runtime, or live-device
work. Independent review is the only next candidate after validation.
