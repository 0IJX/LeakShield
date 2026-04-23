"""Binary and size guardrails."""

from __future__ import annotations

from pathlib import Path


def is_binary_file(path: Path, sample_size: int = 4096) -> bool:
    try:
        sample = path.read_bytes()[:sample_size]
    except OSError:
        return True
    if b"\x00" in sample:
        return True
    return False


def should_skip_file(path: Path, max_file_size_bytes: int) -> bool:
    try:
        if path.stat().st_size > max_file_size_bytes:
            return True
    except OSError:
        return True
    return is_binary_file(path)

