"""Core typed models for LeakShield."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScanMode(StrEnum):
    FULL = "full"
    STAGED = "staged"


class OutputFormat(StrEnum):
    CLI = "cli"
    JSON = "json"


@dataclass(slots=True)
class ScanTarget:
    path: str
    content: str
    changed_lines: set[int] | None = None
    is_staged: bool = False

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("ScanTarget.path is required")


@dataclass(slots=True)
class Candidate:
    detector_id: str
    secret_type: str
    path: str
    line: int
    column: int
    value: str
    context_line: str
    entropy: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.detector_id:
            raise ValueError("Candidate.detector_id is required")
        if not self.secret_type:
            raise ValueError("Candidate.secret_type is required")
        if self.line < 1:
            raise ValueError("Candidate.line must be >= 1")
        if self.column < 1:
            raise ValueError("Candidate.column must be >= 1")


@dataclass(slots=True)
class Finding:
    id: str
    type: str
    severity: Severity
    confidence: float
    path: str
    line: int
    column: int
    detector_id: str
    masked_value: str
    message: str
    remediation: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Finding.confidence must be between 0 and 1")
        if self.line < 1:
            raise ValueError("Finding.line must be >= 1")
        if self.column < 1:
            raise ValueError("Finding.column must be >= 1")
        if not self.masked_value:
            raise ValueError("Finding.masked_value is required")


@dataclass(slots=True)
class ScanSummary:
    scanned_files: int
    findings_total: int
    low: int
    medium: int
    high: int
    critical: int
    duration_ms: int
    blocked: bool

    @classmethod
    def from_findings(
        cls,
        *,
        findings: list[Finding],
        scanned_files: int,
        duration_ms: int,
        blocked: bool,
    ) -> "ScanSummary":
        counts = {Severity.LOW: 0, Severity.MEDIUM: 0, Severity.HIGH: 0, Severity.CRITICAL: 0}
        for finding in findings:
            counts[finding.severity] += 1
        return cls(
            scanned_files=scanned_files,
            findings_total=len(findings),
            low=counts[Severity.LOW],
            medium=counts[Severity.MEDIUM],
            high=counts[Severity.HIGH],
            critical=counts[Severity.CRITICAL],
            duration_ms=duration_ms,
            blocked=blocked,
        )


@dataclass(slots=True)
class ScanResult:
    mode: ScanMode
    findings: list[Finding]
    summary: ScanSummary

