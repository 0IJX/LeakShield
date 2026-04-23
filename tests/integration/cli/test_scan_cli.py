from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from leakshield.cli import app


def test_scan_cli_blocks_on_critical(clean_repo: Path) -> None:
    (clean_repo / "secrets.txt").write_text("AWS=AKIA1234567890ABCD12\n", encoding="utf-8")

    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(clean_repo)
        result = runner.invoke(app, ["scan"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 2
    assert "Potential Secret Findings" in result.stdout

