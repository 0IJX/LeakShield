"""Severity mapping logic."""

from __future__ import annotations

from leakshield.models import Severity


BASE_SEVERITY_BY_TYPE: dict[str, Severity] = {
    "private_key": Severity.CRITICAL,
    "aws_access_key": Severity.CRITICAL,
    "openai_api_key": Severity.HIGH,
    "github_token": Severity.HIGH,
    "db_connection": Severity.HIGH,
    "jwt": Severity.MEDIUM,
    "bearer_token": Severity.MEDIUM,
    "env_secret": Severity.MEDIUM,
}


def map_severity(secret_type: str, confidence: float) -> Severity:
    base = BASE_SEVERITY_BY_TYPE.get(secret_type, Severity.MEDIUM)
    if confidence >= 0.93:
        if base == Severity.HIGH:
            return Severity.CRITICAL
        return base
    if confidence >= 0.78:
        return base
    if confidence >= 0.62:
        if base == Severity.CRITICAL:
            return Severity.HIGH
        if base == Severity.HIGH:
            return Severity.MEDIUM
        return base
    if base in {Severity.CRITICAL, Severity.HIGH}:
        return Severity.MEDIUM
    return Severity.LOW

