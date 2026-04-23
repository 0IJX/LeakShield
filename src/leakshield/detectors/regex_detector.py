"""Regex-based secret detector."""

from __future__ import annotations

import bisect
import re
from dataclasses import dataclass

from leakshield.detectors.base import DetectorContext
from leakshield.detectors.regex_patterns import PATTERN_SPECS
from leakshield.models import Candidate


@dataclass(slots=True)
class _CompiledPattern:
    id: str
    secret_type: str
    regex: re.Pattern[str]
    value_group: int


def _line_starts(text: str) -> list[int]:
    starts = [0]
    for idx, char in enumerate(text):
        if char == "\n":
            starts.append(idx + 1)
    return starts


def _index_to_line_column(index: int, starts: list[int]) -> tuple[int, int]:
    line_idx = bisect.bisect_right(starts, index) - 1
    line_start = starts[line_idx]
    return line_idx + 1, index - line_start + 1


def _line_value(lines: list[str], line_number: int) -> str:
    if line_number < 1 or line_number > len(lines):
        return ""
    return lines[line_number - 1]


class RegexDetector:
    """Regex detector for known secret shapes."""

    id = "regex_detector"
    version = "1.0.0"
    supported_modes = ("full", "staged")

    def __init__(self) -> None:
        self._patterns = [
            _CompiledPattern(
                id=spec.id,
                secret_type=spec.secret_type,
                regex=re.compile(spec.pattern, spec.flags),
                value_group=spec.value_group,
            )
            for spec in PATTERN_SPECS
        ]

    def scan(self, text: str, context: DetectorContext) -> list[Candidate]:
        candidates: list[Candidate] = []
        starts = _line_starts(text)
        lines = text.splitlines()
        for pattern in self._patterns:
            for match in pattern.regex.finditer(text):
                value = match.group(pattern.value_group)
                start = match.start(pattern.value_group)
                line, column = _index_to_line_column(start, starts)
                candidates.append(
                    Candidate(
                        detector_id=pattern.id,
                        secret_type=pattern.secret_type,
                        path=context.path,
                        line=line,
                        column=column,
                        value=value,
                        context_line=_line_value(lines, line),
                        metadata={"match_span": [match.start(), match.end()]},
                    )
                )
        return candidates
