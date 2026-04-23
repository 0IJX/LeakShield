from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from leakshield.cli import app


def test_scan_json_output(clean_repo: Path) -> None:
    raw_secret = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"
    (clean_repo / "secrets.env").write_text(f"OPENAI={raw_secret}\n", encoding="utf-8")
    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(clean_repo)
        result = runner.invoke(app, ["scan", "--format", "json"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["schema_version"] == "1.0"
    assert payload["summary"]["findings_total"] >= 1
    assert raw_secret not in result.stdout
