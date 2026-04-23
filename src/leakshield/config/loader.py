"""Configuration loading helpers."""

from __future__ import annotations

from pathlib import Path

import yaml


def resolve_config_path(repo_root: Path, explicit_path: Path | None) -> Path:
    if explicit_path is not None:
        return explicit_path
    return repo_root / "leakshield.yml"


def load_config_file(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError("Configuration file must contain a YAML object")
    return raw

