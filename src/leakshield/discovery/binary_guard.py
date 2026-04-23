"""Binary and size guardrails."""

from __future__ import annotations

from pathlib import Path

BINARY_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".ico",
    ".pdf",
    ".zip",
    ".gz",
    ".tar",
    ".7z",
    ".rar",
    ".jar",
    ".class",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".bin",
    ".dat",
    ".mp3",
    ".mp4",
    ".mov",
    ".avi",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
}

LIKELY_TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".md",
    ".txt",
    ".env",
    ".sh",
    ".bash",
    ".zsh",
    ".ps1",
    ".psm1",
    ".sql",
    ".xml",
    ".html",
    ".css",
    ".scss",
    ".dockerfile",
}


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

    suffix = path.suffix.lower()
    if suffix in BINARY_EXTENSIONS:
        return True
    if suffix in LIKELY_TEXT_EXTENSIONS:
        return False

    return is_binary_file(path)
