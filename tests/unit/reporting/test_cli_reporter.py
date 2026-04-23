from __future__ import annotations

from rich.console import Console

from leakshield.models import Finding, ScanMode, ScanResult, ScanSummary, Severity
from leakshield.reporting.cli_reporter import render_cli


def _finding(*, path: str, line: int, secret_type: str, confidence: float, severity: Severity) -> Finding:
    return Finding(
        id=f"{path}:{line}",
        type=secret_type,
        severity=severity,
        confidence=confidence,
        path=path,
        line=line,
        column=1,
        detector_id=secret_type,
        masked_value="***",
        message="detected",
        remediation="rotate",
    )


def _render_text(result: ScanResult, *, verbosity: str) -> str:
    console = Console(record=True, force_terminal=False, color_system=None, width=120)
    render_cli(result, console=console, verbosity=verbosity)
    return console.export_text()


def test_cli_summarizes_test_fixture_findings_in_normal_mode() -> None:
    src_finding = _finding(
        path="src/app.py",
        line=10,
        secret_type="openai_api_key",
        confidence=0.95,
        severity=Severity.CRITICAL,
    )
    test_finding = _finding(
        path="tests/test_app.py",
        line=8,
        secret_type="github_token",
        confidence=0.70,
        severity=Severity.HIGH,
    )
    result = ScanResult(
        mode=ScanMode.FULL,
        findings=[src_finding, test_finding],
        summary=ScanSummary.from_findings(
            findings=[src_finding, test_finding],
            scanned_files=2,
            duration_ms=12,
            blocked=True,
        ),
    )

    output = _render_text(result, verbosity="normal")
    assert "Test/fixture findings: 1" in output
    assert "Test/Fixture Findings" in output
    assert "Count: 1" in output
    assert "Potential Secret Findings (grouped by file)" in output
    assert "src/app.py" in output
    assert "tests/test_app.py" not in output


def test_cli_can_expand_test_fixture_findings_in_verbose_mode() -> None:
    src_finding = _finding(
        path="src/app.py",
        line=10,
        secret_type="openai_api_key",
        confidence=0.95,
        severity=Severity.CRITICAL,
    )
    test_finding = _finding(
        path="tests/test_app.py",
        line=8,
        secret_type="github_token",
        confidence=0.70,
        severity=Severity.HIGH,
    )
    result = ScanResult(
        mode=ScanMode.FULL,
        findings=[src_finding, test_finding],
        summary=ScanSummary.from_findings(
            findings=[src_finding, test_finding],
            scanned_files=2,
            duration_ms=12,
            blocked=True,
        ),
    )

    output = _render_text(result, verbosity="verbose")
    assert "Test/Fixture Findings (full details)" in output
    assert "tests/test_app.py" in output

