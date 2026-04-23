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
    re.compile(r"^<[^>]+>$"),
    re.compile(r"(?i)^x{6,}$"),
)


def is_placeholder(value: str, context_line: str = "") -> bool:
    normalized = value.strip().strip("\"'`").lower()
    if normalized in PLACEHOLDER_VALUES:
        return True
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(value.strip()):
            return True
    lowered_context = context_line.lower()
    if "example" in lowered_context or "dummy" in lowered_context:
        return True
    return False

