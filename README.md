# LeakShield

![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status: Active](https://img.shields.io/badge/status-active-success)

**Stop secrets before they ever reach Git history.**

LeakShield is a local-first CLI that detects sensitive values in code and blocks risky changes before they are committed.  
It exists to prevent avoidable incidents: leaked credentials, forced key rotation, and cleanup work after secrets land in Git.

## Why LeakShield? 🔍

- Prevent leaks before commit, not after exposure.
- Local-first by default: no source code leaves your machine.
- Smart detection pipeline: regex + entropy + context filtering.
- Clean, masked output designed for real developer workflows.
- Built-in Git hook integration for staged-commit protection.

## Quick Demo ⚡

```text
$ leakshield scan --staged

[CRITICAL] openai_api_key detected
File: app.py:12
Value: sk-****cdef

❌ Commit blocked
```

When run through the installed pre-commit hook, a blocking result prevents the commit from being recorded.

## Example Output 🧾

```text
LeakShield Scan Summary
Mode: staged
Scanned files: 2
Findings: 2
Critical: 1 | High: 1 | Medium: 0 | Low: 0
Blocked: yes
Duration: 63 ms
Status: BLOCKING ISSUES DETECTED

Potential Secret Findings (grouped by file)
File        Line  Severity  Type            Confidence  Masked Value
app/.env    12    critical  aws_access_key  0.95        AKIA************12
src/app.py  44    high      github_token    0.90        ghp_**************************9x
```

All findings are masked in both CLI and JSON output.

## Use Cases 🛠️

- Prevent accidental API key/token leaks during everyday development.
- Secure repositories before publishing open-source code.
- Enforce safe commit behavior across team workflows.
- Run CI checks with machine-readable JSON output.

## Features ✅

- Scan modes:
  - Full scan: `leakshield scan`
  - Staged scan: `leakshield scan --staged`
- CLI commands:
  - `leakshield scan`
  - `leakshield install-hook`
  - `leakshield doctor`
- JSON output for automation: `--format json`
- Test/fixture noise handling: findings in `tests/` and fixture-style paths are summarized as `Test/Fixture Findings`, down-weighted by default (`lower_confidence`), and fully expanded with higher `output.verbosity` when needed.
- Config and ignore support:
  - `leakshield.yml`
  - `.leakshieldignore`
  - `.gitignore`-aware discovery

## Installation 📦

### Requirements

- Python 3.12+
- Git

### Install from source

```bash
git clone https://github.com/0IJX/LeakShield.git
cd LeakShield
pip install -e .
```

### Local Development Install

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e .
```

## Usage 🚀

### Health Check

```bash
leakshield doctor
```

### Scanning

```bash
leakshield scan
leakshield scan --staged
leakshield scan --config ./leakshield.yml
```

### Git Hook Protection

```bash
leakshield install-hook
```

### Automation / CI

```bash
leakshield scan --staged --format json
```

## JSON Output (CI) 🤖

```json
{
  "tool": "leakshield",
  "schema_version": "1.0",
  "mode": "staged",
  "blocked": true,
  "exit_code": 2,
  "summary": {
    "scanned_files": 2,
    "findings_total": 1,
    "critical": 1,
    "high": 0,
    "medium": 0,
    "low": 0,
    "duration_ms": 41
  },
  "findings": [
    {
      "type": "openai_api_key",
      "severity": "critical",
      "path": "app.py",
      "line": 12,
      "masked_value": "sk-****cdef"
    }
  ]
}
```

## Configuration ⚙️

Default file: `leakshield.yml`

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

Configuration precedence:
1. Built-in defaults
2. `leakshield.yml`
3. CLI flags

## Ignore Rules 🧹

- `.gitignore` is respected during file discovery.
- `.leakshieldignore` supports LeakShield-specific exclusions.
- Default config excludes common noisy paths such as `fixtures`, `samples`, and `testdata`.

Example:

```text
tests/fixtures/*
docs/examples/*
```

## Architecture Overview 🧱

LeakShield uses a layered flow:

`CLI -> Services -> Detection Pipeline -> Reporting -> Exit Policy`

Module breakdown:
- `detectors`: regex and entropy candidate generation
- `filtering`: placeholder/context/allowlist suppression
- `classification`: severity and confidence scoring
- `discovery` + `git`: full and staged file collection
- `reporting`: masked CLI/JSON output and blocking policy
- `config`: schema, load, and merge precedence

## Security Guarantees 🔐

- Local-first runtime (no outbound scanning calls).
- Masked output only; raw secret values are not printed.
- In-memory processing with fail-closed blocking by severity threshold.

## Development 🧪

```bash
pytest
```

Targeted test example:

```bash
pytest tests/integration/scan/test_staged_scan.py
```

## Roadmap Direction 🛣️

LeakShield remains a free local CLI.  
Future direction: team workflows, CI integrations, and enterprise controls.

## Documentation 📚

- [Product Spec](docs/PRODUCT_SPEC.md)
- [System Architecture](docs/SYSTEM_ARCHITECTURE.md)
