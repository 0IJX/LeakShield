"""Masking utilities for sensitive values."""

from __future__ import annotations


def mask_secret(value: str) -> str:
    if not value:
        return ""
    stripped = value.strip()
    if "BEGIN" in stripped and "PRIVATE KEY" in stripped:
        return "-----BEGIN PRIVATE KEY-----***REDACTED***"
    length = len(stripped)
    if length <= 4:
        return "*" * length
    if length <= 10:
        return stripped[:1] + ("*" * (length - 2)) + stripped[-1:]
    keep_prefix = min(4, length // 3)
    keep_suffix = min(2, length // 4)
    masked_len = max(1, length - keep_prefix - keep_suffix)
    return stripped[:keep_prefix] + ("*" * masked_len) + stripped[-keep_suffix:]

