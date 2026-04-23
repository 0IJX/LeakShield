from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from leakshield.cli import app


def test_doctor_cli_fails_outside_git_repo(tmp_path: Path) -> None:
    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(tmp_path)
        result = runner.invoke(app, ["doctor"])
    finally:
        os.chdir(previous)
    assert result.exit_code == 1
    assert "FAIL" in result.stdout

