"""Typed configuration schema."""

from __future__ import annotations

from dataclasses import dataclass, field

from leakshield.filtering.allowlist import Allowlist
from leakshield.models import OutputFormat, Severity


@dataclass(slots=True)
class ScanConfig:
    max_file_size_bytes: int = 1_000_000
    include_globs: list[str] = field(default_factory=list)
    exclude_globs: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DetectorConfig:
    regex_enabled: bool = True
    entropy_enabled: bool = True


@dataclass(slots=True)
class ThresholdConfig:
    min_confidence: float = 0.45
    entropy_threshold: float = 3.5
    block_severity: Severity = Severity.CRITICAL


@dataclass(slots=True)
class OutputConfig:
    format: OutputFormat = OutputFormat.CLI
    color: bool = True
    verbosity: str = "normal"


@dataclass(slots=True)
class HookConfig:
    enabled: bool = True
    fail_severity: Severity = Severity.CRITICAL


@dataclass(slots=True)
class LeakshieldConfig:
    version: int
    scan: ScanConfig
    detectors: DetectorConfig
    thresholds: ThresholdConfig
    allowlist: Allowlist
    output: OutputConfig
    hook: HookConfig

    @classmethod
    def from_dict(cls, payload: dict) -> "LeakshieldConfig":
        scan_data = payload.get("scan", {})
        detector_data = payload.get("detectors", {})
        threshold_data = payload.get("thresholds", {})
        allowlist_data = payload.get("allowlist", {})
        output_data = payload.get("output", {})
        hook_data = payload.get("hook", {})

        min_confidence = float(threshold_data.get("min_confidence", 0.45))
        if min_confidence < 0.0 or min_confidence > 1.0:
            raise ValueError("thresholds.min_confidence must be between 0 and 1")

        return cls(
            version=int(payload.get("version", 1)),
            scan=ScanConfig(
                max_file_size_bytes=int(scan_data.get("max_file_size_bytes", 1_000_000)),
                include_globs=list(scan_data.get("include_globs", [])),
                exclude_globs=list(scan_data.get("exclude_globs", [])),
            ),
            detectors=DetectorConfig(
                regex_enabled=bool(detector_data.get("regex_enabled", True)),
                entropy_enabled=bool(detector_data.get("entropy_enabled", True)),
            ),
            thresholds=ThresholdConfig(
                min_confidence=min_confidence,
                entropy_threshold=float(threshold_data.get("entropy_threshold", 3.5)),
                block_severity=Severity(str(threshold_data.get("block_severity", "critical"))),
            ),
            allowlist=Allowlist(
                values=list(allowlist_data.get("values", [])),
                patterns=list(allowlist_data.get("patterns", [])),
                paths=list(allowlist_data.get("paths", [])),
            ),
            output=OutputConfig(
                format=OutputFormat(str(output_data.get("format", "cli"))),
                color=bool(output_data.get("color", True)),
                verbosity=str(output_data.get("verbosity", "normal")),
            ),
            hook=HookConfig(
                enabled=bool(hook_data.get("enabled", True)),
                fail_severity=Severity(str(hook_data.get("fail_severity", "critical"))),
            ),
        )

