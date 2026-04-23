"""`.leakshieldignore` handling."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class LeakshieldIgnore:
    patterns: list[str]

    @classmethod
    def from_repo(cls, repo_root: Path) -> "LeakshieldIgnore":
        ignore_path = repo_root / ".leakshieldignore"
        if not ignore_path.exists():
            return cls(patterns=[])
        patterns: list[str] = []
        for line in ignore_path.read_text(encoding="utf-8").splitlines():
            cleaned = line.strip()
            if not cleaned or cleaned.startswith("#"):
                continue
            patterns.append(cleaned)
        return cls(patterns=patterns)

    def matches(self, relative_path: str) -> bool:
        normalized = relative_path.replace("\\", "/")
        for pattern in self.patterns:
            if pattern.endswith("/") and normalized.startswith(pattern[:-1]):
                return True
            if fnmatch.fnmatch(normalized, pattern):
                return True
            if "/" not in pattern and fnmatch.fnmatch(Path(normalized).name, pattern):
                return True
        return False

