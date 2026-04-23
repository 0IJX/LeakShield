from __future__ import annotations

from leakshield.config.merger import deep_merge


def test_deep_merge_overrides_nested_values() -> None:
    base = {"output": {"format": "cli", "color": True}}
    override = {"output": {"format": "json"}}
    merged = deep_merge(base, override)
    assert merged["output"]["format"] == "json"
    assert merged["output"]["color"] is True


def test_default_exclude_globs_include_fixture_noise_paths() -> None:
    from leakshield.config.defaults import DEFAULT_CONFIG

    excludes = DEFAULT_CONFIG["scan"]["exclude_globs"]
    assert "**/fixtures/**" in excludes
    assert "**/samples/**" in excludes
