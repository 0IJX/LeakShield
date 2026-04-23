from __future__ import annotations

from leakshield.filtering.placeholders import is_placeholder


def test_known_placeholder_is_filtered() -> None:
    assert is_placeholder("YOUR_API_KEY")
    assert is_placeholder("changeme")


def test_real_secret_not_placeholder() -> None:
    assert not is_placeholder("sk-proj-abcdefghijklmnopqrstuvwxyz123456")

