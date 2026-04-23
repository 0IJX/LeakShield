"""Built-in regex patterns for secret detection."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class PatternSpec:
    id: str
    secret_type: str
    pattern: str
    flags: int = 0
    value_group: int = 0


PATTERN_SPECS: tuple[PatternSpec, ...] = (
    PatternSpec(
        id="openai_api_key",
        secret_type="openai_api_key",
        pattern=r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b",
    ),
    PatternSpec(
        id="aws_access_key_id",
        secret_type="aws_access_key",
        pattern=r"\bAKIA[0-9A-Z]{16}\b",
    ),
    PatternSpec(
        id="github_token",
        secret_type="github_token",
        pattern=r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    ),
    PatternSpec(
        id="jwt_token",
        secret_type="jwt",
        pattern=r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b",
    ),
    PatternSpec(
        id="bearer_token",
        secret_type="bearer_token",
        pattern=r"(?i)\bBearer\s+([A-Za-z0-9\-._~+/]{20,}={0,2})\b",
        value_group=1,
    ),
    PatternSpec(
        id="private_key_block",
        secret_type="private_key",
        pattern=(
            r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |)?PRIVATE KEY-----"
            r"[\s\S]+?"
            r"-----END (?:RSA |EC |OPENSSH |DSA |)?PRIVATE KEY-----"
        ),
        flags=re.MULTILINE,
    ),
    PatternSpec(
        id="db_connection_string",
        secret_type="db_connection",
        pattern=(
            r"\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis|mssql)://"
            r"[^/\s:@]+:[^@\s]+@"
            r"[^\s'\"`]+"
        ),
    ),
    PatternSpec(
        id="env_secret_assignment",
        secret_type="env_secret",
        pattern=(
            r"(?im)^\s*(?:api[_-]?key|secret|token|password|passwd|db_password|private_key)"
            r"[A-Z0-9_]*\s*=\s*([^\s#]+)"
        ),
        flags=re.MULTILINE,
        value_group=1,
    ),
)
