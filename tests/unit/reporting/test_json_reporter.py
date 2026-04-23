from __future__ import annotations

import json

from leakshield.models import Finding, ScanMode, ScanResult, ScanSummary, Severity
from leakshield.reporting.json_reporter import render_json


def test_json_report_schema_fields() -> None:
    finding = Finding(
        id="abc",
        type="openai_api_key",
        severity=Severity.HIGH,
        confidence=0.9,
        path="app.py",
        line=10,
        column=5,
        detector_id="openai_api_key",
        masked_value="sk-p****56",
        message="detected",
        remediation="rotate",
    )
    result = ScanResult(
        mode=ScanMode.FULL,
        findings=[finding],
        summary=ScanSummary.from_findings(findings=[finding], scanned_files=1, duration_ms=12, blocked=False),
    )
    payload = json.loads(render_json(result))
    assert payload["schema_version"] == "1.0"
    assert payload["summary"]["findings_total"] == 1
    assert payload["findings"][0]["masked_value"] == "sk-p****56"

