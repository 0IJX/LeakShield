"""Context-aware filtering rules."""

from __future__ import annotations

from leakshield.filtering.allowlist import Allowlist, is_allowlisted
from leakshield.filtering.placeholders import is_placeholder
from leakshield.models import Candidate


def should_filter_candidate(
    candidate: Candidate,
    *,
    ignore_path: bool,
    allowlist: Allowlist,
) -> bool:
    if ignore_path:
        return True
    if is_placeholder(candidate.value, candidate.context_line):
        return True
    if is_allowlisted(candidate, allowlist):
        return True
    line = candidate.context_line.strip()
    if line.startswith("#") or line.startswith("//"):
        if candidate.secret_type in {"env_secret", "bearer_token"}:
            return True
    return False

