# Day122 Report Index Responsibility Split

Day122 clarifies the existing `report-index` flow without changing external behavior. The work keeps report-index report-only: it scans local files, normalizes reviewer-visible metadata, renders local output, and remains wired through the existing CLI entrypoints.

## Responsibility Boundaries

### Scanning / Discovery

Scanning is responsible only for finding local report files declared by the existing report catalog. It collects JSON and HTML paths from configured glob patterns, ignores `config.json`, and does not infer status, render output, invoke adapters, run tasks, open SSH, or contact devices.

### Metadata Normalization / Collection

Normalization converts scanned paths and catalog metadata into the existing report-index row shape. It preserves the current `FOUND`, `MISSING`, and disabled guardrail rows, existing relative path formatting, existing Day18 runner evidence attachment, and existing optional missing-report notes.

### Rendering / Output

Rendering is responsible for console formatting and writing the existing local HTML report index. It consumes normalized rows and the existing task catalog summary but does not discover reports, change report schema, modify dashboard behavior, or execute runner tasks.

### CLI Wiring / Command Dispatch Boundary

CLI wiring remains the dispatch boundary. `python network_lab.py --report-index` continues to call the local report visibility index path, while `python network_lab.py --task report-index` continues to use the profile-backed latest lab overview path. Day122 does not add a new CLI task or change command names.

## Explicit Non-Changes

- Dashboard unchanged.
- Task catalog unchanged.
- Report schema unchanged.
- No new runner task behavior.
- No live execution behavior.
- No SSH or device access.
- No configuration-changing command path.
- No dashboard route, template, static page, or dashboard documentation changes.
