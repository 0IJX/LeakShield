from __future__ import annotations

import json
import os
from pathlib import Path

from typer.testing import CliRunner

from leakshield.cli import app


def test_end_to_end_scan_and_json_output(clean_repo: Path) -> None:
    (clean_repo / "app.py").write_text("token = 'ghp_abcdefghijklmnopqrstuvwxyz1234'\n", encoding="utf-8")
    runner = CliRunner()
    previous = Path.cwd()
    try:
        os.chdir(clean_repo)
        result = runner.invoke(app, ["scan", "--format", "json"])
    finally:
        os.chdir(previous)

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["summary"]["findings_total"] >= 1
    finding = payload["findings"][0]
    assert finding["masked_value"] != ""
    assert "abcdefghijklmnopqrstuvwxyz1234" not in finding["masked_value"]

