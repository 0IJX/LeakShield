"""Exit code and blocking policy logic."""

from __future__ import annotations

from leakshield.models import Finding, Severity

SEVERITY_RANK = {
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def should_block(findings: list[Finding], threshold: Severity) -> bool:
    threshold_rank = SEVERITY_RANK[threshold]
    return any(SEVERITY_RANK[finding.severity] >= threshold_rank for finding in findings)


def scan_exit_code(findings: list[Finding], threshold: Severity) -> int:
    return 2 if should_block(findings, threshold) else 0

