"""Allowlist filtering logic."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field

from leakshield.models import Candidate


@dataclass(slots=True)
class Allowlist:
    values: list[str] = field(default_factory=list)
    patterns: list[str] = field(default_factory=list)
    paths: list[str] = field(default_factory=list)


def _path_matches(path: str, patterns: list[str]) -> bool:
    normalized = path.replace("\\", "/")
    for pattern in patterns:
        if fnmatch.fnmatch(normalized, pattern):
            return True
    return False


def is_allowlisted(candidate: Candidate, allowlist: Allowlist) -> bool:
    if candidate.value in allowlist.values:
        return True
    if _path_matches(candidate.path, allowlist.paths):
        return True
    for pattern in allowlist.patterns:
        try:
            if re.search(pattern, candidate.value):
                return True
        except re.error:
            continue
    return False

