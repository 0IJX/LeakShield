"""Placeholder suppression helpers."""

from __future__ import annotations

import re


PLACEHOLDER_VALUES = {
    "your_api_key",
    "your_token_here",
    "changeme",
    "replace_me",
    "example",
    "example_token",
    "dummy",
    "test",
    "sample",
    "<secret>",
}

PLACEHOLDER_PATTERNS = (
    re.compile(r"^\$\{[A-Z0-9_]+\}$"),
    re.compile(r"^\$[A-Z0-9_]+$"),
    re.compile(r"^<[^>]+>$"),
    re.compile(r"(?i)^x{6,}$"),
)


def is_placeholder(value: str, context_line: str = "") -> bool:
    stripped = value.strip()
    normalized = stripped.strip("\"'`").lower()
    if normalized in PLACEHOLDER_VALUES:
        return True
    if normalized.startswith("example_") or normalized.startswith("dummy_"):
        return True
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(stripped):
            return True
    lowered_context = context_line.lower()
    has_placeholder_signal = bool(
        re.search(r"\b(example|dummy|sample|placeholder|fake)\b", lowered_context)
    )
    has_low_complexity_value = len(normalized) <= 32 and not any(char.isdigit() for char in normalized)
    if has_placeholder_signal and has_low_complexity_value:
        return True
    return False
