from __future__ import annotations

from leakshield.classification.confidence import score_confidence
from leakshield.classification.severity import map_severity
from leakshield.models import Candidate, Severity


def _candidate(secret_type: str, entropy: float) -> Candidate:
    return Candidate(
        detector_id="test",
        secret_type=secret_type,
        path="a.py",
        line=1,
        column=1,
        value="value",
        context_line="value",
        entropy=entropy,
    )


def test_confidence_scoring_uses_entropy() -> None:
    low = score_confidence(_candidate("github_token", 2.5))
    high = score_confidence(_candidate("github_token", 4.5))
    assert high > low


def test_severity_mapping() -> None:
    assert map_severity("private_key", 0.95) == Severity.CRITICAL
    assert map_severity("env_secret", 0.40) in {Severity.LOW, Severity.MEDIUM}

