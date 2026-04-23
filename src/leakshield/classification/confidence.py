"""Confidence scoring logic."""

from __future__ import annotations

from leakshield.models import Candidate


BASE_CONFIDENCE_BY_TYPE: dict[str, float] = {
    "private_key": 0.99,
    "aws_access_key": 0.95,
    "openai_api_key": 0.95,
    "github_token": 0.90,
    "db_connection": 0.85,
    "jwt": 0.82,
    "bearer_token": 0.74,
    "env_secret": 0.62,
}


def _clamp(value: float, *, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def score_confidence(candidate: Candidate, *, entropy_threshold: float = 3.5) -> float:
    score = BASE_CONFIDENCE_BY_TYPE.get(candidate.secret_type, 0.6)
    if candidate.entropy is None:
        return round(_clamp(score), 3)

    if candidate.entropy >= entropy_threshold + 0.7:
        score += 0.08
    elif candidate.entropy >= entropy_threshold:
        score += 0.04
    elif candidate.entropy < entropy_threshold - 0.8:
        score -= 0.08
    return round(_clamp(score), 3)

