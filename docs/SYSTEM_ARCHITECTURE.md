# LeakShield Phase 2 System Architecture

## Summary
- Build LeakShield as a layered local CLI system with strict separation between orchestration, detection, filtering, classification, and reporting.
- Keep all scanning and decision logic local-only; no outbound network paths in core runtime.
- Use stable internal contracts so the same engine can power local CLI now and CI/team features later.

## Architecture Overview
- Runtime style: `CLI -> Application Service -> Scan Pipeline -> Reporters -> Exit Policy`.
- Key principle: commands only orchestrate; domain services own security logic.

```text
+---------------------+
| Typer CLI Commands  |
| scan/install/doctor |
+----------+----------+
           |
           v
+---------------------+        +---------------------+
| Application Layer   |<------>| Config + Policy     |
| ScanService         |        | leakshield.yml      |
| HookService         |        | .leakshieldignore   |
| DoctorService       |        +---------------------+
+----------+----------+
           |
           v
+---------------------+        +---------------------+
| Target Providers    |        | Discovery Guards    |
| Full repo walker    |------->| .gitignore aware    |
| Staged git adapter  |        | binary/file limits  |
+----------+----------+        +---------------------+
           |
           v
+---------------------+
| Detection Pipeline  |
| Regex -> Entropy    |
| -> Context Filter   |
| -> Classification   |
+----------+----------+
           |
           v
+---------------------+        +---------------------+
| Findings Store      |------->| Reporters           |
| in-memory only      |        | Rich terminal/JSON  |
+----------+----------+        +---------------------+
           |
           v
+---------------------+
| Exit Code Policy    |
| block on critical   |
+---------------------+
```

## Core Modules and Responsibilities
- `cli`: Typer command definitions and argument parsing.
- `services`: command orchestration (`scan`, `install-hook`, `doctor`), no detector logic.
- `config`: load, validate, and merge defaults + `leakshield.yml` + CLI overrides.
- `discovery`: file/staged-target collection, `.gitignore` handling, binary/size checks.
- `git`: staged diff and index readers, pre-commit hook installer/validator.
- `detectors`: regex and entropy detector implementations, detector registry.
- `filtering`: placeholder suppression, path ignore checks, allowlist/context suppression.
- `classification`: severity/confidence scoring and finding normalization.
- `reporting`: masking, Rich terminal renderer, JSON serializer, exit code policy.
- `models`: typed contracts for `ScanTarget`, `Candidate`, `Finding`, `ScanSummary`.

## Detection Pipeline Design
- Step 1: extract candidates from regex detectors with detector metadata.
- Step 2: run entropy scoring on candidate value and nearby token window.
- Step 3: apply filtering rules:
  - Ignore match if file/path is ignored.
  - Ignore known placeholders (`YOUR_API_KEY`, `example`, `changeme`, test fixtures).
  - Ignore allowlisted values/patterns from config.
- Step 4: classify each remaining finding:
  - `type`: detector family (`aws_key`, `github_token`, `jwt`, `private_key`, `db_conn`, `env_secret`, and similar).
  - `confidence`: weighted score from regex certainty + entropy + context signals.
  - `severity`: mapped from type and confidence (`critical`, `high`, `medium`, `low`).
- Step 5: emit masked finding only; raw secret never leaves in-memory candidate handling.

## Data Flow Design

### 1) Full Scan (`leakshield scan`)
1. Load config and ignore policy.
2. Enumerate repository files, respecting `.gitignore` and binary/size guards.
3. Run pipeline per text file.
4. Aggregate findings and summary.
5. Render terminal/JSON and return policy-based exit code.

### 2) Staged Git Scan (`leakshield scan --staged`)
1. Read staged entries from Git index.
2. Build scan targets from staged file snapshots.
3. Restrict findings to staged-added/modified lines.
4. Run same pipeline and report path/line scoped to staged content.
5. Return exit code from blocking policy.

### 3) Pre-commit Hook Execution
1. Hook executes `leakshield scan --staged --format cli`.
2. If critical findings exist (or configured threshold), hook exits non-zero to block commit.
3. Output shows masked findings and remediation text.
4. If no blocking findings, hook exits zero and commit proceeds.

## Config System Design (`leakshield.yml`)
- `version`: schema version for forward compatibility.
- `scan`: max file size, include/exclude globs, staged/full defaults.
- `detectors`: enable/disable regex and entropy, per-detector toggles.
- `thresholds`: min confidence, entropy threshold, blocking severity.
- `allowlist`: values/patterns/paths to suppress known safe matches.
- `output`: default format (`cli` or `json`), verbosity, color preference.
- `hook`: pre-commit behavior (enabled, fail severity threshold).

### Resolution Order
1. Built-in defaults.
2. Repository `leakshield.yml`.
3. CLI flags (highest precedence).

## Ignore System (`.leakshieldignore`)
- Uses gitignore-style path patterns.
- Applied before content scanning to reduce cost and noise.
- Combined with `.gitignore` using union behavior.

## Output and Reporting Design
- CLI output:
  - Rich summary panel with totals by severity.
  - Findings table with `file`, `line`, `type`, `severity`, `confidence`, `masked_value`.
  - Remediation hints and rotation guidance for exposed credentials.
- JSON output:
  - Stable schema with `schema_version`, `mode`, `summary`, and `findings`.
  - Each finding includes `id`, `type`, `severity`, `confidence`, `path`, `line`, `masked_value`, `message`, `remediation`.
- Masking rules:
  - Never print full values.
  - Keep short prefix/suffix only when safe.
  - Private key and long token bodies are heavily redacted.

## Extension Model for Future Detectors
- Detector contract:
  - `id`, `version`, `supported_modes`, `scan(text, context) -> candidates`.
- Register built-in detectors through an internal registry.
- Add plugin loading later via Python entry points group `leakshield.detectors`.
- Keep classifier/reporter interfaces detector-agnostic so new detectors need no CLI changes.
- Plugin security guardrails:
  - No persistence of candidate raw values.
  - Plugin output always normalized and masked through central reporting.

## Final MVP Folder Structure
```text
LeakShield/
  docs/
    PRODUCT_SPEC.md
    SYSTEM_ARCHITECTURE.md
  src/
    leakshield/
      __init__.py
      cli.py
      models.py
      services/
      config/
      discovery/
      git/
      detectors/
      filtering/
      classification/
      reporting/
  hooks/
    pre-commit.template
  tests/
    unit/
    integration/
    fixtures/
  .leakshieldignore
  leakshield.yml
  requirements.txt
  README.md
  CONTRIBUTING.md
  SECURITY.md
  LICENSE
```

## Public Interfaces and Types (MVP Contracts)
- CLI commands:
  - `leakshield scan [--staged] [--format cli|json] [--config PATH]`
  - `leakshield install-hook`
  - `leakshield doctor`
- Core contracts:
  - `Finding`: `type`, `severity`, `confidence`, `path`, `line`, `masked_value`, `remediation`.
  - `ScanSummary`: counts by severity, scanned files, duration, blocked status.
- JSON report is versioned via `schema_version` for future CI/team compatibility.

## Test Scenarios for Architecture Validation
- Full scan respects `.gitignore` and `.leakshieldignore`.
- Staged scan only reports findings present in staged changes.
- Pre-commit blocks on critical and passes otherwise.
- Placeholder/allowlist suppression reduces false positives.
- Masking never exposes full secrets in CLI or JSON output.
- Config precedence behaves as `defaults < yaml < CLI flags`.
- Extension registration adds detectors without changing CLI command layer.

## Key Architecture Decisions
- Single shared scan pipeline for full and staged modes to prevent behavior drift.
- Policy/config are separated from command handlers for CI/team reuse later.
- Stable JSON schema and typed finding model enable future integrations.
- Central masking in reporting prevents accidental secret exposure.
- Detector registry abstraction enables plugin-style expansion.

## Assumptions
- Canonical CLI command is `leakshield` (not typo variants).
- Local-first means no telemetry or outbound calls in the MVP runtime path.
- Default blocking threshold is `critical`, configurable in `leakshield.yml`.
- Initial detector set is regex + entropy only; ML approaches are out of MVP.
