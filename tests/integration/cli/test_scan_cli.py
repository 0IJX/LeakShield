from __future__ import annotations

import os
from pathlib import Path

from typer.testing import CliRunner

from leakshield.cli import app


def test_scan_cli_blocks_on_critical(clean_repo: Path) -> None:
    raw_secret = "AKIA1234567890ABCD12"
    (clean_repo / "secrets.txt").write_text(f"AWS={raw_secret}\n", encoding="utf-8")

    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(clean_repo)
        result = runner.invoke(app, ["scan"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 2
    assert "Potential Secret Findings" in result.stdout
    assert raw_secret not in result.stdout


def test_scan_cli_summarizes_test_fixture_findings_by_default(clean_repo: Path) -> None:
    src_secret = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"
    test_secret = "ghp_abcdefghijklmnopqrstuvwxyz1234"
    (clean_repo / "src").mkdir(parents=True, exist_ok=True)
    (clean_repo / "tests").mkdir(parents=True, exist_ok=True)
    (clean_repo / "src" / "app.py").write_text(f"value = '{src_secret}'\n", encoding="utf-8")
    (clean_repo / "tests" / "test_app.py").write_text(f"value = '{test_secret}'\n", encoding="utf-8")

    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(clean_repo)
        result = runner.invoke(app, ["scan"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 2
    assert "Test/Fixture Findings" in result.stdout
    assert "Count: 1" in result.stdout
    assert "src/app.py" in result.stdout
    assert "tests/test_app.py" not in result.stdout


def test_scan_cli_can_expand_test_fixture_findings_with_verbose_output(clean_repo: Path) -> None:
    src_secret = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"
    test_secret = "ghp_abcdefghijklmnopqrstuvwxyz1234"
    (clean_repo / "leakshield.yml").write_text("output:\n  verbosity: verbose\n", encoding="utf-8")
    (clean_repo / "src").mkdir(parents=True, exist_ok=True)
    (clean_repo / "tests").mkdir(parents=True, exist_ok=True)
    (clean_repo / "src" / "app.py").write_text(f"value = '{src_secret}'\n", encoding="utf-8")
    (clean_repo / "tests" / "test_app.py").write_text(f"value = '{test_secret}'\n", encoding="utf-8")

    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(clean_repo)
        result = runner.invoke(app, ["scan"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 2
    assert "Test/Fixture Findings (full details)" in result.stdout
    assert "tests/test_app.py" in result.stdout
