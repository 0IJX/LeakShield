"""Shared candidate-to-finding pipeline."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from leakshield.classification.confidence import score_confidence
from leakshield.classification.severity import map_severity
from leakshield.detectors.entropy import shannon_entropy
from leakshield.detectors.registry import DetectorRegistry
from leakshield.filtering.allowlist import Allowlist
from leakshield.filtering.context_filter import should_filter_candidate
from leakshield.models import Finding, ScanTarget
from leakshield.reporting.masking import mask_secret


@dataclass(slots=True)
class PipelineOptions:
    allowlist: Allowlist
    entropy_threshold: float
    min_confidence: float
    enable_entropy: bool = True


def _finding_id(path: str, line: int, detector_id: str, masked_value: str) -> str:
    raw = f"{path}:{line}:{detector_id}:{masked_value}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def run_pipeline(
    *,
    target: ScanTarget,
    detector_registry: DetectorRegistry,
    options: PipelineOptions,
    ignore_path: bool = False,
) -> list[Finding]:
    findings_by_key: dict[tuple[str, int, int, str], Finding] = {}
    candidates = detector_registry.scan_text(target.content, target.path)
    for candidate in candidates:
        candidate.entropy = shannon_entropy(candidate.value) if options.enable_entropy else None
        if target.changed_lines is not None and candidate.line not in target.changed_lines:
            continue
        if should_filter_candidate(candidate, ignore_path=ignore_path, allowlist=options.allowlist):
            continue
        confidence = score_confidence(candidate, entropy_threshold=options.entropy_threshold)
        if confidence < options.min_confidence:
            continue
        severity = map_severity(candidate.secret_type, confidence)
        masked_value = mask_secret(candidate.value)
        finding = Finding(
            id=_finding_id(candidate.path, candidate.line, candidate.detector_id, masked_value),
            type=candidate.secret_type,
            severity=severity,
            confidence=confidence,
            path=candidate.path,
            line=candidate.line,
            column=candidate.column,
            detector_id=candidate.detector_id,
            masked_value=masked_value,
            message=f"Potential {candidate.secret_type} detected.",
            remediation=(
                "Remove the secret from source, replace with secure environment/config "
                "reference, and rotate if it was exposed."
            ),
            metadata=candidate.metadata.copy(),
        )
        dedupe_key = (finding.path, finding.line, finding.column, finding.masked_value)
        existing = findings_by_key.get(dedupe_key)
        if existing is None or finding.confidence > existing.confidence:
            findings_by_key[dedupe_key] = finding
    return list(findings_by_key.values())
