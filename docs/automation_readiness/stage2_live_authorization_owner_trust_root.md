# Standalone Stage-2 Owner trust-root configuration contract

## Decision summary

**One standalone, immutable Owner trust-root configuration/acquisition contract
is implemented for offline validation with synthetic records only.** This
delivery contains only the module, its tests, and this document. The historical
Owner verifier and accumulated Stage-1/Stage-2 implementation are not included.
The module is not registered with any verifier, runtime, CLI, startup
composition, task registry, or production approval source. It provisions no
key, file, path, identity, hash, ACL, approval, credential, network operation,
or device access.

`OWNER TRUST-ROOT CONTRACT IMPLEMENTED OFFLINE != PRODUCTION TRUST ROOT PROVISIONED`

`OWNER TRUST-ROOT CONTRACT IMPLEMENTED OFFLINE != PRODUCTION OWNER VERIFIER COMPOSED`

`OWNER TRUST-ROOT CONTRACT IMPLEMENTED OFFLINE != LIVE EXECUTION AUTHORIZED`

## Standalone delivery context

The module uses only the Python standard library. Its tests additionally use
pytest and import the module directly under the `validation_framework`
namespace package; this delivery adds no package initializer or historical
framework exports. No adapter, envelope, verifier, ledger, snapshot, transport,
or runtime composition is supplied by these three files.

The Stage-2 name identifies this bounded contract, not delivery or acceptance
of the historical Stage-1/Stage-2 program. The public Stage-0 baseline and
separately gated roadmap remain unchanged. Any future verifier or startup
consumer requires separate implementation, authorization, and validation.

## Root-of-trust boundary

The trust-root record does not authenticate itself. A future separately
authorized startup composition must supply all three expected values:

- one canonical absolute repository-external Windows path;
- one exact Win32 file identity;
- one lowercase SHA-256 of the complete raw file.

Those expected values may not come from the record, authorization envelope,
approval artifact, request, ordinary CLI argument, environment variable, home
expansion, search, or fallback. The ultimate authenticity assumption is
Owner-controlled filesystem placement and ACLs plus those independently pinned
composition values. A digest stored inside the record would be circular and is
therefore absent.

Repository-external placement and ancestor/ACL trust are composition
preconditions, not checks performed by this module. The module validates path
syntax and binds the opened file's identity and content; it does not locate the
repository boundary, traverse and validate ancestor directories, inspect ACLs,
or validate the approval directory on disk. Offline tests establish the bounded
module contract, not these deployment preconditions or production integration.

## Exact atomic record

The record is strict UTF-8 canonical JSON containing exactly seven string
fields:

```text
schema_version
ed25519_public_key_base64
issuer_ref
lab_only_attestation_ref
approval_source_id
approval_source_absolute_path
approval_source_directory_identity
```

`schema_version` is exactly `1.0`. Unknown, missing, duplicate, non-string, or
additional fields fail closed. Serialization uses sorted keys, compact `,` and
`:` separators, no optional whitespace, no BOM, and no trailing newline. The
raw file must equal its canonical reserialization byte for byte. The fixed
maximum is:

```text
OWNER_TRUST_ROOT_MAX_BYTES = 4096
```

The bound is not caller configurable. Byte 4,096 is accepted only after an
additional one-byte EOF probe proves that the file is complete; byte 4,097 is
rejected.

## Public verification key and fixed identities

`ed25519_public_key_base64` is exactly 44 ASCII characters of canonical RFC
4648 standard Base64 with canonical padding. Strict decoding must produce
exactly 32 bytes, and re-encoding must reproduce the original value. URL-safe
Base64, whitespace, PEM, 31-byte keys, 33-byte keys, and noncanonical padding
are rejected.

`issuer_ref`, `lab_only_attestation_ref`, and `approval_source_id` use the
module's self-contained lowercase dotted ASCII reference grammar. They are
immutable trusted configuration, not caller- or envelope-selected authority.

The audit-only public-key fingerprint is derived as:

```text
SHA256:<unpadded canonical Base64(SHA-256(raw 32-byte public key))>
```

It is not part of the record and is never accepted instead of the pinned path,
file identity, complete-file digest, or raw verification key.

## Approval-source identity only

The record stores a canonical absolute drive-rooted Windows approval-directory
path and identity in this exact form:

```text
win32-fileid-v1:<16-lowercase-hex-volume-serial>:<32-lowercase-hex-file-id>
```

Canonical path validation is component-aware. Components containing Windows
forbidden filename characters (`<`, `>`, `:`, `"`, `/`, `\\`, `|`, `?`, or
`*`), control characters, or a trailing dot or ASCII space are rejected.
Reserved-device matching examines the stem before the first dot, removes only
trailing ASCII spaces from that stem for comparison, and matches after Unicode
uppercase conversion, including dotless `ı` in `conın$`. The full-path
NFC/casefold requirement remains unchanged. The reserved set is `CON`, `PRN`,
`AUX`, `NUL`, `CONIN$`,
`CONOUT$`, and `COM` / `LPT` followed by one of `1` through `9` or the
superscript digits `¹`, `²`, `³`. This rejects extension and space-before-extension
aliases such as `nul.txt`, `nul .txt`, `com1 .json`, `com¹.txt`, and
`CONOUT$ .log`, including when they appear as intermediate components.

These are deterministic string checks, not filesystem normalization or a proof
that every possible Windows alias has been resolved. Accepted paths are not
rewritten. Non-reserved names such as `console`, `console .txt`, `com10`,
`lpt10`, and `conin$-backup` remain valid; whitespace other than ASCII space is
not stripped for device matching. No compatibility normalization such as NFKC
is introduced. Python 3.13 `ntpath.isreserved()` is a reference oracle for
these bounded categories, not a production dependency or an OS-wide guarantee.
The existing repository-external placement precondition and same-handle
identity, digest, and final-reparse checks are unchanged.

The contract does not open, enumerate, provision, or read that directory. A
future separately authorized read-only approval-source implementation must use
exact `owner_approval_ref` lookup and a deterministic filename, with no
enumeration, wildcard, newest-record selection, alias, or fallback. Signed
artifact lookup, zero/duplicate-result rejection, signature verification, and
signed-artifact size bounds belong to a separately authorized verifier and
approval-source implementation. They are not implemented or validated by this
standalone trust-root delivery.

Production ACL policy remains operational work outside this module:

| Identity | Trust-root / approval-source access |
| --- | --- |
| Runtime identity | Read and required directory traversal only |
| Owner/admin provisioning identity | Controlled write/replace |
| Ordinary user/process | Deny write |

No ACL API is called and no permission is changed.

## One-open Win32 acquisition

The acquisition validates expected syntax before native construction and then
uses exactly one trust-root source open:

```text
validate expected canonical path / FileId / SHA
→ CreateFileW once
→ GetFileType
→ GetFileInformationByHandleEx(FileAttributeTagInfo)
→ reject directory or final reparse point
→ GetFileInformationByHandleEx(FileIdInfo)
→ compare exact identity
→ bounded ReadFile loop through the same handle
→ prove EOF
→ SHA-256 complete raw bytes
→ compare exact expected SHA
→ strict canonical JSON parse
→ CloseHandle exactly once
→ issue immutable configuration
```

`CreateFileW` uses only `GENERIC_READ`, `FILE_SHARE_READ`, `OPEN_EXISTING`, and
`FILE_FLAG_OPEN_REPARSE_POINT`. No share-write, share-delete, create,
truncation, write, backup semantics, or overlapped I/O is present. The approved
native capability surface is limited to `CreateFileW`, `GetFileType`,
`GetFileInformationByHandleEx(FileAttributeTagInfo)`,
`GetFileInformationByHandleEx(FileIdInfo)`, `ReadFile`, and `CloseHandle`.

Type, attributes, identity, bytes, and digest all come from the same handle.
There is no Python `open`, second path open, hashing reopen, or parser reopen.
Every successful open is closed exactly once on success or failure. A close
failure prevents configuration issuance.

## Immutable acquisition authority

`OwnerTrustRootConfiguration` contains only:

- schema version;
- immutable 32-byte Ed25519 public key;
- fixed issuer and lab-attestation references;
- approval-source logical ID, canonical path, and directory identity;
- derived audit fingerprint;
- acquired trust-root file identity and SHA-256.

It retains no file handle, complete file, mutable parser object, private key,
approval artifact, or credential. Its representation does not render the key,
paths, identities, hashes, or fingerprint.

The type is authority-bearing trusted composition evidence. Ordinary
construction, subclassing, `dataclasses.replace`, copy, deepcopy, pickle, and
supported reconstruction hooks are blocked. Only successful acquisition after
handle close issues the exact concrete type; no lookalike is an acquired
configuration. This is a supported-API application integrity boundary, not a
Python security sandbox. Deliberate low-level `object.__new__`, hostile
same-process introspection, monkey-patching, and a compromised interpreter are
outside the threat model.

## Key lifetime and private-key exclusion

The Owner private signing key is never a field, input, output, or dependency.
There is no key generation, signing API, signing tool, key ring, previous key,
next key, watcher, hot reload, or environment override. The public trust root
must be loaded once by any future authorized startup composition. Replacement
requires a separately authorized Owner reprovisioning event and restart; no
dual-key overlap or fallback exists.

## Offline proof and remaining gates

Tests use only synthetic public bytes, deterministic native fakes, and disposable
ordinary files for the existing Win32 regular-file and trailing-dot checks.
Reserved-device alias regressions are pure string/parser checks; a rejecting
native-factory sentinel proves invalid expected paths cannot construct native
access. No reserved device name is opened or created. They cover strict
canonical JSON, exact key decoding,
path and identity syntax, same-handle call ordering, one open, complete-file
identity/hash binding, exact byte limit and EOF probe, directory/reparse
rejection, read/close failures, immutable authority construction, safe output,
and absence of environment, credential, network, SSH, or runtime composition.

Still not implemented or authorized:

- a real Owner Ed25519 key or private-key custody operation;
- real issuer, lab-attestation, approval-source, path, FileId, or SHA values;
- trust-root or approval-directory provisioning and ACL changes;
- an approval-directory lookup implementation or real signed artifact;
- production Owner-verifier or runtime composition;
- production ledger and real known-hosts provisioning;
- Credential Manager, CredReadW, sockets, SSH, device access, or live proof.

Independent offline review of these three trust-root files is the only next
candidate after successful validation.
