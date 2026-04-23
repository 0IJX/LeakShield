"""Rich terminal renderer."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from leakshield.models import ScanResult


def render_cli(result: ScanResult, *, console: Console | None = None) -> None:
    active_console = console or Console()
    summary = result.summary
    summary_text = (
        f"Mode: {result.mode.value}\n"
        f"Scanned files: {summary.scanned_files}\n"
        f"Findings: {summary.findings_total} "
        f"(critical={summary.critical}, high={summary.high}, medium={summary.medium}, low={summary.low})\n"
        f"Blocked: {'yes' if summary.blocked else 'no'}\n"
        f"Duration: {summary.duration_ms} ms"
    )
    active_console.print(Panel(summary_text, title="LeakShield Scan Summary"))

    if not result.findings:
        active_console.print("[green]No potential leaks detected.[/green]")
        return

    table = Table(title="Potential Secret Findings")
    table.add_column("File", overflow="fold")
    table.add_column("Line", justify="right")
    table.add_column("Type")
    table.add_column("Severity")
    table.add_column("Confidence", justify="right")
    table.add_column("Masked Value", overflow="fold")
    for finding in result.findings:
        table.add_row(
            finding.path,
            str(finding.line),
            finding.type,
            finding.severity.value,
            f"{finding.confidence:.2f}",
            finding.masked_value,
        )
    active_console.print(table)
    active_console.print(
        "[yellow]Remediation:[/yellow] remove secrets from code, move to secure env/config, "
        "and rotate credentials if exposure is possible."
    )

