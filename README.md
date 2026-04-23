# LeakShield

LeakShield is a local-first CLI that detects potential secrets and blocks risky commits before they enter Git history.

## Why LeakShield

- Prevents secret leaks before commit, not after incident response.
- Runs fully local-first: no source code leaves your machine.
- Uses layered detection (regex + entropy + contextual filtering) to improve signal quality.
- Produces masked, actionable output suitable for both humans and automation.

## Features

- Full repository scan: `leakshield scan`
- Staged-only scan: `leakshield scan --staged`
- Pre-commit hook installer: `leakshield install-hook`
- Environment diagnostics: `leakshield doctor`
- Output formats: Rich CLI table or JSON (`--format json`)
- CI-friendly JSON contract with deterministic ordering and explicit `blocked`/`exit_code`
- Ignore controls:
  - `.gitignore` (respected during discovery)
  - `.leakshieldignore` (LeakShield-specific path exclusions)
  - `allowlist` entries via `leakshield.yml`

## Installation

### Requirements

- Python 3.12+
- Git (for staged scan and hook workflows)

### Local development install

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -e .
```

## Quick Start

### 1) Verify environment

```bash
leakshield doctor
```

### 2) Scan the full repository

```bash
leakshield scan
```

### 3) Scan only staged changes

```bash
leakshield scan --staged
```

### 4) Install pre-commit protection

```bash
leakshield install-hook
```

## Usage Examples

### JSON output for automation

```bash
leakshield scan --staged --format json
```

### Use a custom config file

```bash
leakshield scan --config ./leakshield.yml
```

## Sample Output (Masked)

```text
LeakShield Scan Summary
Mode: staged
Scanned files: 2
Findings: 1
Critical: 1 | High: 0 | Medium: 0 | Low: 0
Blocked: yes
Duration: 42 ms
Status: BLOCKING ISSUES DETECTED

Potential Secret Findings (grouped by file)
File      Line  Severity  Type            Confidence  Masked Value
app/.env  12    critical  aws_access_key  0.95        AKIA************12
```

LeakShield never prints full secret values in CLI or JSON output.

### JSON output shape (for CI)

```json
{
  "tool": "leakshield",
  "schema_version": "1.0",
  "mode": "staged",
  "blocked": true,
  "exit_code": 2,
  "summary": { "...": "..." },
  "findings": [ { "...": "..." } ]
}
```

## Configuration

Default config file: `leakshield.yml`

```yaml
version: 1
thresholds:
  min_confidence: 0.45
  entropy_threshold: 3.5
  block_severity: critical
allowlist:
  values: []
  patterns: []
  paths: []
```

Precedence order:
1. Built-in defaults
2. `leakshield.yml`
3. CLI flags

## Ignore Rules

- `.gitignore` excludes files from discovery.
- `.leakshieldignore` adds LeakShield-specific path patterns.
- Default config also excludes common noisy fixture/sample paths:
  - `**/fixtures/**`
  - `**/samples/**`
  - `**/sample/**`
  - `**/testdata/**`
  - `**/__snapshots__/**`

Example `.leakshieldignore`:

```text
tests/fixtures/*
docs/examples/*
```

## Architecture Snapshot

LeakShield follows a layered design:

`CLI -> Services -> Detection Pipeline -> Reporting -> Exit Policy`

Core modules:
- `detectors`: regex and entropy candidate generation
- `filtering`: placeholder, allowlist, context suppression
- `classification`: severity and confidence scoring
- `discovery` / `git`: full and staged target enumeration
- `reporting`: masking, CLI/JSON renderers, block policy
- `config`: schema, loading, merge precedence

## Security Guarantees

- Local-first runtime; no outbound network calls in scan flow.
- In-memory candidate processing.
- Masked output only, never full secret values.
- Designed to fail closed on blocking severity thresholds.

## Development

Run tests:

```bash
pytest
```

Run a targeted staged scan test:

```bash
pytest tests/integration/scan/test_staged_scan.py
```

## Roadmap Direction

LeakShield is free as a local CLI.
Future direction: paid team dashboard, CI integration, and enterprise security controls.
