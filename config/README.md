# Config Directory

This directory is reserved for non-secret configuration templates and notes.

Day-32-pre does not add runtime configuration files here. Real lab files such as
`config.json` and `config.cisco.json` must remain local and uncommitted.

Do not commit:

- Real router, switch, or client IP addresses.
- Usernames, passwords, API tokens, private keys, or WireGuard keys.
- RouterOS exports, backups, generated reports, or lab-specific evidence.

Future config templates should use placeholder values only and must clearly state
whether a workflow is `documentation_only`, `read_only`,
`read_only_with_report`, `safe_dry_run`, or `live_execution_blocked`.
