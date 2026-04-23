"""JSON schema helpers for reports."""

from __future__ import annotations

from leakshield.models import ScanResult


SCHEMA_VERSION = "1.0"


def result_to_dict(result: ScanResult) -> dict:
    ordered_findings = sorted(
        result.findings,
        key=lambda finding: (finding.path, finding.line, finding.column, finding.type),
    )
    exit_code = 2 if result.summary.blocked else 0
    return {
        "tool": "leakshield",
        "schema_version": SCHEMA_VERSION,
        "mode": result.mode.value,
        "blocked": result.summary.blocked,
        "exit_code": exit_code,
        "summary": {
            "scanned_files": result.summary.scanned_files,
            "findings_total": result.summary.findings_total,
            "low": result.summary.low,
            "medium": result.summary.medium,
            "high": result.summary.high,
            "critical": result.summary.critical,
            "duration_ms": result.summary.duration_ms,
            "blocked": result.summary.blocked,
        },
        "findings": [
            {
                "id": finding.id,
                "type": finding.type,
                "severity": finding.severity.value,
                "confidence": round(finding.confidence, 3),
                "path": finding.path,
                "line": finding.line,
                "column": finding.column,
                "masked_value": finding.masked_value,
                "message": finding.message,
                "remediation": finding.remediation,
            }
            for finding in ordered_findings
        ],
    }
