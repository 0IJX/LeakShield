from __future__ import annotations

from leakshield.filtering.allowlist import Allowlist
from leakshield.filtering.context_filter import is_test_related_path, should_filter_candidate
from leakshield.models import Candidate


def _candidate(secret_type: str, value: str, context_line: str) -> Candidate:
    return Candidate(
        detector_id="test",
        secret_type=secret_type,
        path="app.env",
        line=1,
        column=1,
        value=value,
        context_line=context_line,
    )


def test_low_signal_env_values_are_filtered() -> None:
    candidate = _candidate("env_secret", "true", "SECRET=true")
    assert should_filter_candidate(candidate, ignore_path=False, allowlist=Allowlist()) is True


def test_high_signal_env_values_are_not_filtered_by_default() -> None:
    candidate = _candidate("env_secret", "aB3kLm9Qw2Xz8Yv1Tp6N", "SECRET=aB3kLm9Qw2Xz8Yv1Tp6N")
    assert should_filter_candidate(candidate, ignore_path=False, allowlist=Allowlist()) is False


def test_fixture_paths_filter_noisy_types() -> None:
    candidate = Candidate(
        detector_id="test",
        secret_type="env_secret",
        path="tests/fixtures/sample.env",
        line=1,
        column=1,
        value="verylikelyplaceholder",
        context_line="SECRET=verylikelyplaceholder",
    )
    assert should_filter_candidate(candidate, ignore_path=False, allowlist=Allowlist()) is True


def test_test_related_path_detection() -> None:
    assert is_test_related_path("tests/unit/test_scan.py") is True
    assert is_test_related_path("src/auth_test.py") is True
    assert is_test_related_path("src/test_auth.py") is True
    assert is_test_related_path("docs/fixtures/token.txt") is True
    assert is_test_related_path("src/leakshield/services/scan_service.py") is False
