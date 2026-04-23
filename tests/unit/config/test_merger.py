from __future__ import annotations

from leakshield.config.merger import deep_merge


def test_deep_merge_overrides_nested_values() -> None:
    base = {"output": {"format": "cli", "color": True}}
    override = {"output": {"format": "json"}}
    merged = deep_merge(base, override)
    assert merged["output"]["format"] == "json"
    assert merged["output"]["color"] is True

