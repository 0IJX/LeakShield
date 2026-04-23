"""Detector registry and extension loading."""

from __future__ import annotations

from importlib.metadata import entry_points

from leakshield.detectors.base import Detector, DetectorContext
from leakshield.detectors.regex_detector import RegexDetector
from leakshield.models import Candidate


class DetectorRegistry:
    """Registry of built-in and optionally plugin detectors."""

    def __init__(self, detectors: list[Detector] | None = None) -> None:
        self._detectors: list[Detector] = detectors[:] if detectors else [RegexDetector()]

    @property
    def detectors(self) -> tuple[Detector, ...]:
        return tuple(self._detectors)

    def register(self, detector: Detector) -> None:
        self._detectors.append(detector)

    def load_entrypoint_plugins(self, group: str = "leakshield.detectors") -> None:
        for candidate in entry_points(group=group):
            try:
                detector_factory = candidate.load()
                detector = detector_factory()
                self.register(detector)
            except Exception:
                # Never crash scanning due to plugin load failure.
                continue

    def scan_text(self, text: str, path: str) -> list[Candidate]:
        context = DetectorContext(path=path)
        results: list[Candidate] = []
        for detector in self._detectors:
            try:
                results.extend(detector.scan(text, context))
            except Exception:
                # Detector failures should not break the full scan.
                continue
        return results

