"""Rich terminal renderer."""

from __future__ import annotations

from collections import Counter, defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from leakshield.filtering.context_filter import is_test_related_path
from leakshield.models import ScanResult, Severity

SEVERITY_WEIGHT = {
    Severity.CRITICAL: 0,
    Severity.HIGH: 1,
    Severity.MEDIUM: 2,
    Severity.LOW: 3,
}


def _severity_style(severity: Severity) -> str:
    if severity == Severity.CRITICAL:
        return "[bold red]critical[/bold red]"
    if severity == Severity.HIGH:
        return "[red]high[/red]"
    if severity == Severity.MEDIUM:
        return "[yellow]medium[/yellow]"
    return "[cyan]low[/cyan]"


def _split_test_fixture_findings(findings: list) -> tuple[list, list]:
    regular_findings: list = []
    test_fixture_findings: list = []
    for finding in findings:
        if is_test_related_path(finding.path):
            test_fixture_findings.append(finding)
        else:
            regular_findings.append(finding)
    return regular_findings, test_fixture_findings


def _build_findings_table(*, findings: list, title: str) -> Table:
    grouped: dict[str, list] = defaultdict(list)
    for finding in findings:
        grouped[finding.path].append(finding)

    table = Table(title=title)
    table.add_column("File", overflow="fold", min_width=24)
    table.add_column("Line", justify="right")
    table.add_column("Severity")
    table.add_column("Type")
    table.add_column("Confidence", justify="right")
    table.add_column("Masked Value", overflow="fold")
    paths = sorted(grouped.keys())
    for path_index, path in enumerate(paths):
        file_findings = sorted(
            grouped[path],
            key=lambda finding: (SEVERITY_WEIGHT[finding.severity], finding.line, finding.column),
        )
        for finding_index, finding in enumerate(file_findings):
            table.add_row(
                path if finding_index == 0 else "",
                str(finding.line),
                _severity_style(finding.severity),
                finding.type,
                f"{finding.confidence:.2f}",
                finding.masked_value,
                end_section=finding_index == len(file_findings) - 1 and path_index != len(paths) - 1,
            )
    return table


def _render_test_fixture_summary(*, findings: list, console: Console, show_details: bool) -> None:
    severity_counts = Counter(finding.severity for finding in findings)
    type_counts = Counter(finding.type for finding in findings)
    type_summary = ", ".join(
        f"{secret_type}: {count}"
        for secret_type, count in sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))
    )
    summary_text = (
        f"Count: {len(findings)}\n"
        f"Critical: {severity_counts[Severity.CRITICAL]} | High: {severity_counts[Severity.HIGH]} | "
        f"Medium: {severity_counts[Severity.MEDIUM]} | Low: {severity_counts[Severity.LOW]}\n"
        f"Types: {type_summary if type_summary else 'none'}\n"
    )
    if show_details:
        summary_text += "Details: expanded below because verbosity is set to verbose/debug."
    else:
        summary_text += "Details: summarized to reduce noise (set output.verbosity to verbose to expand)."
    console.print(Panel(summary_text, title="Test/Fixture Findings"))
    if show_details:
        ordered = sorted(
            findings,
            key=lambda finding: (
                finding.path,
                finding.line,
                finding.column,
                SEVERITY_WEIGHT[finding.severity],
            ),
        )
        console.print(
            _build_findings_table(
                findings=ordered,
                title="Test/Fixture Findings (full details)",
            )
        )


def render_cli(
    result: ScanResult,
    *,
    console: Console | None = None,
    verbosity: str = "normal",
) -> None:
    active_console = console or Console()
    summary = result.summary
    status = (
        "[bold red]BLOCKING ISSUES DETECTED[/bold red]"
        if summary.blocked
        else "[bold green]NO BLOCKING ISSUES[/bold green]"
    )
    ordered_findings = sorted(
        result.findings,
        key=lambda finding: (
            finding.path,
            finding.line,
            finding.column,
            SEVERITY_WEIGHT[finding.severity],
        ),
    )
    regular_findings, test_fixture_findings = _split_test_fixture_findings(ordered_findings)
    summary_text = (
        f"Mode: {result.mode.value}\n"
        f"Scanned files: {summary.scanned_files}\n"
        f"Findings: {summary.findings_total}\n"
        f"Critical: {summary.critical} | High: {summary.high} | Medium: {summary.medium} | Low: {summary.low}\n"
        f"Test/fixture findings: {len(test_fixture_findings)}\n"
        f"Blocked: {'yes' if summary.blocked else 'no'}\n"
        f"Duration: {summary.duration_ms} ms\n"
        f"Status: {status}"
    )
    active_console.print(Panel(summary_text, title="LeakShield Scan Summary"))

    if not result.findings:
        active_console.print("[green]No potential leaks detected.[/green]")
        return

    if regular_findings:
        active_console.print(
            _build_findings_table(
                findings=regular_findings,
                title="Potential Secret Findings (grouped by file)",
            )
        )
    else:
        active_console.print(
            "[yellow]No non-test findings to list. "
            "All current findings are in test/fixture paths.[/yellow]"
        )

    show_test_details = verbosity.strip().lower() in {"verbose", "debug"}
    if test_fixture_findings:
        _render_test_fixture_summary(
            findings=test_fixture_findings,
            console=active_console,
            show_details=show_test_details,
        )

    active_console.print(
        "[yellow]Remediation:[/yellow] remove secrets from code, move to secure env/config, "
        "and rotate credentials if exposure is possible."
    )
