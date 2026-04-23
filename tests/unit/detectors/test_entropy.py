from __future__ import annotations

from leakshield.detectors.entropy import is_high_entropy, shannon_entropy


def test_entropy_is_deterministic() -> None:
    value = "abcdefghijklmnopqrstuvwxyz0123456789"
    assert shannon_entropy(value) == shannon_entropy(value)


def test_entropy_threshold_behavior() -> None:
    assert is_high_entropy("abc123", threshold=3.5, min_length=6) is False
    assert is_high_entropy("aB3kLm9Qw2Xz8Yv1Tp6Nr4Hs", threshold=3.5, min_length=10) is True

