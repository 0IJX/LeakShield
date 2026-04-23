from __future__ import annotations

from pathlib import Path

from leakshield.config.loader import load_config_file


def test_load_config_file_reads_yaml(tmp_path: Path) -> None:
    path = tmp_path / "leakshield.yml"
    path.write_text("version: 1\noutput:\n  format: json\n", encoding="utf-8")
    data = load_config_file(path)
    assert data["version"] == 1
    assert data["output"]["format"] == "json"

