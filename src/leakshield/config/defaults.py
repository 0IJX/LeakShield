"""Default configuration values."""

from __future__ import annotations


DEFAULT_CONFIG: dict = {
    "version": 1,
    "scan": {
        "max_file_size_bytes": 1_000_000,
        "include_globs": [],
        "exclude_globs": [
            "**/fixtures/**",
            "**/samples/**",
            "**/sample/**",
            "**/testdata/**",
            "**/__snapshots__/**",
        ],
        "test_path_mode": "lower_confidence",
        "test_path_confidence_multiplier": 0.75,
    },
    "detectors": {
        "regex_enabled": True,
        "entropy_enabled": True,
    },
    "thresholds": {
        "min_confidence": 0.45,
        "entropy_threshold": 3.5,
        "block_severity": "critical",
    },
    "allowlist": {
        "values": [],
        "patterns": [],
        "paths": [],
    },
    "output": {
        "format": "cli",
        "color": True,
        "verbosity": "normal",
    },
    "hook": {
        "enabled": True,
        "fail_severity": "critical",
    },
}
