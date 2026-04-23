"""Context-aware filtering rules."""

from __future__ import annotations

from leakshield.filtering.allowlist import Allowlist, is_allowlisted
from leakshield.filtering.placeholders import is_placeholder
from leakshield.models import Candidate


LOW_SIGNAL_ENV_VALUES = {
    "true",
    "false",
    "none",
    "null",
    "localhost",
    "127.0.0.1",
    "dev",
    "development",
    "local",
}

NOISY_FIXTURE_SEGMENTS = {
    "fixtures",
    "samples",
    "sample",
    "testdata",
    "__snapshots__",
}

NOISY_FIXTURE_TYPES = {
    "env_secret",
    "bearer_token",
    "jwt",
    "db_connection",
}


def _is_low_signal_env_value(value: str) -> bool:
    normalized = value.strip().strip("\"'`").lower()
    if normalized in LOW_SIGNAL_ENV_VALUES:
        return True
    if normalized.isdigit():
        return True
    if len(normalized) < 8:
        return True
    if normalized.isalpha() and len(normalized) <= 12:
        return True
    return False


def _is_noisy_fixture_path(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    segments = {segment for segment in normalized.split("/") if segment}
    return not NOISY_FIXTURE_SEGMENTS.isdisjoint(segments)


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
    if _is_noisy_fixture_path(candidate.path) and candidate.secret_type in NOISY_FIXTURE_TYPES:
        return True
    line = candidate.context_line.strip()
    if candidate.secret_type == "env_secret" and _is_low_signal_env_value(candidate.value):
        return True
    if candidate.secret_type == "bearer_token" and len(candidate.value.strip()) < 20:
        return True
    if line.startswith("#") or line.startswith("//"):
        if candidate.secret_type in {"env_secret", "bearer_token"}:
            return True
    return False
