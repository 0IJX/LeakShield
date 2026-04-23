from __future__ import annotations

from leakshield.reporting.masking import mask_secret


def test_masking_hides_secret_core() -> None:
    masked = mask_secret("sk-proj-abcdefghijklmnopqrstuvwxyz123456")
    assert masked.startswith("sk-p")
    assert "abcdefghijklmnopqrstuvwxyz123456" not in masked


def test_masking_private_key_block() -> None:
    value = "-----BEGIN PRIVATE KEY-----\nABC\n-----END PRIVATE KEY-----"
    masked = mask_secret(value)
    assert "ABC" not in masked
    assert "REDACTED" in masked

