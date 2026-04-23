from __future__ import annotations

import pytest

from leakshield.config.schema import LeakshieldConfig


def test_scan_test_path_mode_validation_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="scan.test_path_mode"):
        LeakshieldConfig.from_dict(
            {
                "scan": {
                    "test_path_mode": "unsupported-mode",
                }
            }
        )


def test_scan_test_path_confidence_multiplier_validation() -> None:
    with pytest.raises(ValueError, match="scan.test_path_confidence_multiplier"):
        LeakshieldConfig.from_dict(
            {
                "scan": {
                    "test_path_confidence_multiplier": 1.1,
                }
            }
        )

