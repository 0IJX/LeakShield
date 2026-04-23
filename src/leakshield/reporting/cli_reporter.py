"""Rich terminal renderer."""

from __future__ import annotations

from collections import defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

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


def render_cli(result: ScanResult, *, console: Console | None = None) -> None:
    active_console = console or Console()
    summary = result.summary
    status = (
        "[bold red]BLOCKING ISSUES DETECTED[/bold red]"
        if summary.blocked
        else "[bold green]NO BLOCKING ISSUES[/bold green]"
    )
    summary_text = (
        f"Mode: {result.mode.value}\n"
        f"Scanned files: {summary.scanned_files}\n"
        f"Findings: {summary.findings_total}\n"
        f"Critical: {summary.critical} | High: {summary.high} | Medium: {summary.medium} | Low: {summary.low}\n"
        f"Blocked: {'yes' if summary.blocked else 'no'}\n"
        f"Duration: {summary.duration_ms} ms\n"
        f"Status: {status}"
    )
    active_console.print(Panel(summary_text, title="LeakShield Scan Summary"))

    if not result.findings:
        active_console.print("[green]No potential leaks detected.[/green]")
        return

    grouped: dict[str, list] = defaultdict(list)
    ordered_findings = sorted(
        result.findings,
        key=lambda finding: (
            finding.path,
            finding.line,
            finding.column,
            SEVERITY_WEIGHT[finding.severity],
        ),
    )
    for finding in ordered_findings:
        grouped[finding.path].append(finding)

    table = Table(title="Potential Secret Findings (grouped by file)")
    table.add_column("File", overflow="fold")
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
    active_console.print(table)
    active_console.print(
        "[yellow]Remediation:[/yellow] remove secrets from code, move to secure env/config, "
        "and rotate credentials if exposure is possible."
    )
