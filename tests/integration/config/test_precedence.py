from __future__ import annotations

from pathlib import Path

from leakshield.config.merger import build_runtime_config
from leakshield.models import OutputFormat


def test_config_precedence_defaults_yaml_cli(clean_repo: Path) -> None:
    (clean_repo / "leakshield.yml").write_text("output:\n  format: cli\n", encoding="utf-8")
    cfg = build_runtime_config(
        repo_root=clean_repo,
        cli_overrides={"output": {"format": "json"}},
    )
    assert cfg.output.format == OutputFormat.JSON

