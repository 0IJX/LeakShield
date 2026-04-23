from __future__ import annotations

import pytest

from leakshield.models import Finding, ScanSummary, Severity


def test_finding_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError):
        Finding(
            id="id",
            type="openai_api_key",
            severity=Severity.HIGH,
            confidence=1.1,
            path="a.py",
            line=1,
            column=1,
            detector_id="regex",
            masked_value="sk-****",
            message="msg",
            remediation="fix",
        )


def test_scan_summary_counts_by_severity() -> None:
    findings = [
        Finding(
            id="1",
            type="a",
            severity=Severity.CRITICAL,
            confidence=0.9,
            path="a.py",
            line=1,
            column=1,
            detector_id="d",
            masked_value="***",
            message="m",
            remediation="r",
        ),
        Finding(
            id="2",
            type="b",
            severity=Severity.MEDIUM,
            confidence=0.7,
            path="b.py",
            line=2,
            column=1,
            detector_id="d",
            masked_value="***",
            message="m",
            remediation="r",
        ),
    ]
    summary = ScanSummary.from_findings(findings=findings, scanned_files=2, duration_ms=10, blocked=True)
    assert summary.critical == 1
    assert summary.medium == 1
    assert summary.findings_total == 2

