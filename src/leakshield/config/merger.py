"""Configuration merge and resolution logic."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from leakshield.config.defaults import DEFAULT_CONFIG
from leakshield.config.loader import load_config_file, resolve_config_path
from leakshield.config.schema import LeakshieldConfig


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def build_runtime_config(
    *,
    repo_root: Path,
    config_path: Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
) -> LeakshieldConfig:
    resolved_path = resolve_config_path(repo_root, config_path)
    merged = deep_merge(DEFAULT_CONFIG, load_config_file(resolved_path))
    if cli_overrides:
        merged = deep_merge(merged, cli_overrides)
    return LeakshieldConfig.from_dict(merged)

