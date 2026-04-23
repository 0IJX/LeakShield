"""LeakShield CLI entrypoint."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from leakshield.config.merger import build_runtime_config
from leakshield.models import OutputFormat
from leakshield.reporting.cli_reporter import render_cli
from leakshield.reporting.exit_policy import scan_exit_code
from leakshield.reporting.json_reporter import render_json
from leakshield.services.doctor_service import DoctorService
from leakshield.services.hook_service import HookService
from leakshield.services.scan_service import ScanService

app = typer.Typer(help="LeakShield: local-first secret leak prevention for Git workflows.")


@app.command("scan")
def scan_command(
    staged: bool = typer.Option(False, "--staged", help="Scan staged changes only."),
    format: OutputFormat | None = typer.Option(
        None,
        "--format",
        case_sensitive=False,
        help="Output format: cli or json.",
    ),
    config: Path | None = typer.Option(None, "--config", exists=False, help="Path to leakshield.yml."),
) -> None:
    repo_root = Path.cwd()
    cli_overrides: dict = {}
    if format is not None:
        cli_overrides = {"output": {"format": format.value}}

    runtime_config = build_runtime_config(
        repo_root=repo_root,
        config_path=config,
        cli_overrides=cli_overrides,
    )
    effective_format = format or runtime_config.output.format
    service = ScanService(repo_root=repo_root, config=runtime_config)
    result = service.scan(staged=staged)

    if effective_format == OutputFormat.JSON:
        typer.echo(render_json(result))
    else:
        render_cli(result)

    raise typer.Exit(scan_exit_code(result.findings, runtime_config.thresholds.block_severity))


@app.command("install-hook")
def install_hook_command() -> None:
    service = HookService(repo_root=Path.cwd())
    result = service.install(command="leakshield scan --staged --format cli")
    if result.installed:
        typer.echo(f"Installed pre-commit hook at: {result.hook_path}")
    else:
        typer.echo(f"Pre-commit hook already up to date: {result.hook_path}")


@app.command("doctor")
def doctor_command() -> None:
    service = DoctorService(repo_root=Path.cwd())
    report = service.run()
    console = Console()
    table = Table(title="LeakShield Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Message", overflow="fold")

    for check in report.checks:
        table.add_row(check.name, "OK" if check.ok else "FAIL", check.message)
    console.print(table)
    raise typer.Exit(0 if report.ok else 1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

