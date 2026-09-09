# S2-RO-08: Offline VRRP command policy and parser

## Decision summary

S2-RO-08 provides one immutable command policy and a bounded offline parser
for `mikrotik.vrrp_status`. The sole command is `/interface vrrp print detail`.
Neither component executes that command or grants execution authority.

Current RouterOS 7.24.2 compatibility remediation: implementation candidate
for independent review. The bounded extension supports dynamic Flags legend
subsets, comment-only record headers, and `v3-checksum-as-v2`. It preserves
fail-closed parsing and grants no live-run or retry authority.

Original S2-RO-08 delivery status (historical): validated implementation
candidate; independent security review PASS.
Ready for separate local-commit authorization. S2-RO-09 remains future-only.
The sequence index's earlier planning status is historical; this document
records the Owner-authorized expanded S2-RO-08 implementation boundary.

## Allowed scope and files

The original five-file candidate consists of:

- [Command policy](../../validation_framework/stage2_vrrp_readonly_command_policy.py)
- [Command-policy tests](../../tests/stage2/test_vrrp_readonly_command_policy.py)
- [Offline parser](../../validation_framework/stage2_vrrp_readonly_parser.py)
- [Parser tests](../../tests/stage2/test_vrrp_readonly_parser.py)
- This document.

The current compatibility remediation changes only the parser, its tests,
and this existing document. Command policy and evidence contracts are unchanged.

The parser and tests are separate modules to keep command identity validation
independent of untrusted-output parsing. S2-RO-01 through S2-RO-07 remain
unchanged. No dependencies, CLI tasks, runners, or validation plugins are added.

## Forbidden scope

No command execution, SSH, NETCONF, RESTCONF, sockets, DNS, device access,
credential retrieval, approval acquisition, Owner verification, replay-ledger
consumption, known-host acquisition, provider integration, or subprocess is
performed. No command builder, caller command argument, alias, compatibility
command, fallback, write command, retry, scheduler, worker, or runtime loop
exists. Tests use synthetic in-memory data.

## Command contract

`resolve_stage2_vrrp_readonly_command(request)` accepts only the exact
S2-RO-01 request type and revalidates its fields. It issues one frozen, slotted
`Stage2VrrpReadOnlyCommandSpecification` with these exact values:

| Field | Value |
| --- | --- |
| schema_version | s2-ro-08.command-policy.v1 |
| operation_id | mikrotik.vrrp_status |
| command_policy_version | policy.stage2.vrrp-readonly.v1 |
| command_text | /interface vrrp print detail |
| read_only | True |
| execution_authorized | False |

Unsupported requests and policy drift fail closed with INVALID_REQUEST,
UNKNOWN_REQUEST, or INVALID_POLICY. Public command resolution accepts no
additional argument. Normal mutation, subclassing, copying, and serialization
of the issued specification are prohibited. Python code with arbitrary
in-process mutation privileges is outside this data-contract boundary.

## Repository evidence and selected format

The parser uses the indexed, flag-based detail format demonstrated by
`routeros_vrrp_detail` in the Day35 VRRP failover tests and the retained
historical bounded Stage-2 adapter. The S2-RO-01 contract defines normalized
field types and limits. Older simplified `state=...` test inputs are not an
accepted compatibility format. The original grammar used offline repository
evidence. The current extension addresses three Owner-reported RouterOS 7.24.2
output characteristics; tests retain only synthetic data. Codex performs no
device collection or general RouterOS discovery for this remediation.

References:

- [S2-RO-01 evidence contract](stage2_vrrp_readonly_s2_ro_01_contract.md)
- [Day35 fixture and tests](../../tests/test_mikrotik_day35_vrrp_failover_validation.py)
- [Day35 safety record](../roadmap/day35_vrrp_failover_validation_safety.md)
- Historical `adapters/stage2_mikrotik_vrrp_adapter.py` on retained branch
  `codex/stage2-mikrotik-vrrp-transport-two-finding-remediation` (evidence only).
- [Integration gates](actual_automation_integration_plan.md)

## Parser input and grammar

`parse_stage2_vrrp_readonly_output(request, raw_output)` revalidates the command
policy before parsing. It accepts only exact built-in bytes, from 1 through
65,536 bytes, decoded as strict UTF-8. Subclasses, zero bytes, overflow,
replacement decoding, truncation, and partial success are prohibited.

Each record starts with a decimal index, spaces, optional flags, and fields.
The index is at most five digits; numeric index duplicates reject even when
spelled with leading zeros. Indented continuation lines may contain complete
fields. Values cannot span lines. One supported Flags legend is optional before
all records. Other headers, banners, and trailing fragments reject. A legend
without records and whitespace-only output reject.

The legend line must begin exactly `Flags: `, followed by at least one exact
flag-description pair. Supported mappings are `X - DISABLED`, `I - INVALID`,
`G - GRP-AUTHORITY`, `g - GRP-MEMBER`, `R - RUNNING`, `M - MASTER`,
`B - BACKUP`, and `F - FAILURE`. Any nonempty subset is accepted, with pairs
separated only by `; `. Unknown flags, wrong descriptions, duplicate flags,
malformed separators, and surrounding spaces reject as MALFORMED_OUTPUT.
For example, `Flags: R - RUNNING; M - MASTER` is accepted. The one exact
legacy Day35 legend remains an explicit compatibility exception:

```text
Flags: X - DISABLED; I - INVALID; G - GRP-AUTHORITY, g - GRP-MEMBER; R - RUNNING; M - MASTER, B - BACKUP, F - FAILURE
```

A physical record-start line may instead end in a comment-only remainder:
`0 RM ;;; synthetic VRRP comment`. The remainder must be exactly `;;;` or
start with `;;; `; `;;`, `;;;;`, and attached text such as `;;;text` reject.
Any `=` in that remainder rejects as MALFORMED_OUTPUT, preventing mixed
comment/field headers. All required fields must then come from ordinary
indented continuation lines. Standalone and continuation-line comments reject.
Comment text is discarded before field parsing, cannot alter normalized facts,
and is absent from returned objects, logs, and canonical evidence. Printable
quotes in comments are inert; field values still cannot span physical lines.
The outer UTF-8, control-character, and byte-limit checks apply to comments too.

Spaces, LF, CRLF, and blank lines are accepted within the global byte bound.
Tabs, bare CR, terminal escapes, prohibited control/format characters, and
Unicode line separators reject. Field order is independent; record order is
preserved. Quoted values have no escape syntax. Empty quoted auxiliary values
are allowed. Every field token must be consumed.

| Required field | Normalization and bounds |
| --- | --- |
| name | NFC text, 1–128 UTF-8 bytes, no controls or surrounding whitespace |
| vrid | Canonical unsigned decimal, 1–255 |
| priority | Canonical unsigned decimal, 0–255 |
| interval | Positive decimal plus ms or s; normalized to 1–255,000 milliseconds |
| version | Canonical decimal 2 or 3 |

Numeric signs, leading zeros in these numeric fields, fractions, booleans,
and unsupported versions reject. Required numeric values may be quoted;
unquoting does not relax their lexical or range checks.

Flags X/I/R set disabled/invalid/running. M/B/F select MASTER/BACKUP/FAILURE;
absence means UNKNOWN. Repeated flags or multiple role flags reject. The
repository legend's G/g flags carry no S2-RO-01 evidence field and are discarded.

Optional auxiliary keys are exactly: `mtu`, `mac-address`, `arp`,
`arp-timeout`, `interface`, `group-authority`, `preemption-mode`,
`authentication`, `on-backup`, `on-master`, `on-fail`, `v3-protocol`,
`sync-connection-tracking`, `connection-tracking-mode`, and
`v3-checksum-as-v2`. The last key is the sole auxiliary allowlist addition for
the current compatibility remediation. Their token syntax
is validated and their contents discarded; they are not semantically validated
or executed, including callback-shaped text.

Neither auxiliary values nor comments become evidence fields. Their original
bytes still contribute to the existing complete-output byte count and digest.
Unobserved `password`, `remote-address`, `connection-tracking-port`, and
`group-master` fields remain unsupported; broader support requires a separate
compatibility decision.

Unknown keys and all duplicate keys reject, including auxiliary duplicates.
One through 32 complete records are required. Duplicate indexes or instance
names reject the entire output. Equal VRIDs with distinct names are not treated
as duplicate identities. Empty or malformed output never becomes an empty
successful observation.

## Result and failure contract

`Stage2VrrpParsedOutput` contains an immutable tuple of S2-RO-01 normalized
records, the byte count, and SHA-256 of the complete original bytes. Its safe
representation contains no raw output; `execution_authorized` is always False.
It is normalized data, not an authenticity token. Direct construction does not
prove transport provenance. Later trusted runtime composition owns request
binding and duration when constructing S2-RO-01 observation evidence.

Raw bytes/text exist transiently during parsing and are absent from the result.
The digest provides correlation, not authenticity or execution permission.
Errors expose only a bounded category with no chained underlying exception:

- INVALID_OPERATION
- COMMAND_POLICY_VIOLATION
- INVALID_OUTPUT_TYPE
- OUTPUT_TOO_LARGE
- INVALID_UTF8
- EMPTY_OUTPUT
- MALFORMED_OUTPUT
- MISSING_REQUIRED_FIELD
- DUPLICATE_FIELD
- UNSUPPORTED_VALUE
- AMBIGUOUS_RECORD
- PARSER_INTERNAL_FAILURE

No successful result is returned when any record fails.

## Future transport boundary: documentation only

S2-RO-09 must separately implement pinned SSH transport. Its proposed limits
are one exec of the exact command, no PTY, no interactive shell, 15-second
connect timeout, 30-second command timeout, maximum 65,536 output bytes, zero
retries, and one attempt. Stderr, nonzero exit, timeout, overflow, invalid UTF-8,
and parser failure must fail closed. No timers, transport, or execution are
implemented here. S2-RO-10 runtime composition and S2-RO-11 live entrypoint
remain separately gated.

## Validation and acceptance

Required evidence is guarded focused tests with no skips, Stage-2 regression,
full pytest, report-index policy acceptance, whitespace checks including new
files, independent security review, and documentation readability review.
Every skip must be classified; no S2-RO-08 test may skip.

Windows validation disables plugin autoload, bytecode, and pytest cache. Native
blockers precede pytest import. Source-reviewed ephemeral Colorama and
click._winconsole module stubs avoid console initialization without faking
Win32 APIs or changing installed packages. Validation uses non-TTY output;
pytest's TTY-only Colorama wrapper is not emulated. An unexpected native path
is a stop condition, not permission to extend the guard.

The current remediation must preserve its three-file boundary and pass guarded
parser/contract/command-policy tests, Stage-2 regressions, full pytest, and
report-index before its separately Owner-authorized local commit. Independent
review remains a separate step; the original review below does not cover the
new remediation. No push, PR, merge, fresh authorization, replay consumption,
SSH, or second live attempt is authorized. A future live validation requires a
new package and new direct Owner authorization; spent authorization stays spent.

### RouterOS 7.24.2 remediation validation

Guarded offline validation with Python 3.13.7 and pytest 8.4.2 passed:

| Validation | Collected | Passed | Failed | Safety skips |
| --- | --- | --- | --- | --- |
| Parser, contract, command policy | 256 | 256 | 0 | 0 |
| Stage-2 regression | 1,633 | 1,631 | 0 | 2 |
| Full pytest | 3,759 | 3,756 | 0 | 3 |

Report-index: 14/14 PASS, zero failures, warnings, missing, or unknown entries.
Whitespace and documentation readability review: PASS. Independent remediation
review remains pending; these results establish readiness for that review only.

The existing offline launcher invokes pytest with
`-p no:cacheprovider --color=no -ra`, followed by these target arguments:

- `tests/stage2/test_vrrp_readonly_parser.py tests/stage2/test_vrrp_readonly_contract.py tests/stage2/test_vrrp_readonly_command_policy.py`
- `tests/stage2`
- No target arguments for the full suite.

Its report-index mode invokes `network_lab.py --task report-index` under the
same guard. The only skips are the two native Win32 tests and the Flask
process/socket lifecycle test classified below. No parser test skips. The
initial focused run found one new test fixture accidentally forming valid CRLF;
it was corrected to contain a bare CR and all subsequent validations passed.
Only synthetic parser inputs were used. No device command, credential read,
private-key access, or real replay consumption occurred.

### Original candidate validation (historical)

- Focused: 101 collected, 101 passed, zero failures or skips.
- Stage 2: 1,008 collected, 1,006 passed, zero failures, two safety skips.
- Full pytest: 3,134 collected, 3,131 passed, zero failures, three safety skips.
- Report-index: 14/14 PASS; zero failures, warnings, or missing entries.
- Whitespace and documentation readability: PASS.
- Separate read-only security review: PASS; zero unresolved material findings.

The two Stage-2 skips are the real Win32 disposable-file and trailing-dot-alias
trust-root tests. The third full-suite skip is the Flask process/socket
lifecycle test. These are the previously accepted local safety exclusions;
no S2-RO-08 test skips. No device or native API access was used to obtain these
results. Pytest 8.4.2 and Colorama 0.4.6 source inspection established that the
non-TTY startup path requires a Colorama module import with no exported symbol;
the ephemeral stub therefore exports no Colorama behavior.

The evidence applies to the local candidate and grants no staging, commit,
push, merge, or live-access authority.
