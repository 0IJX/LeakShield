"""Detector interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from leakshield.models import Candidate


@dataclass(slots=True, frozen=True)
class DetectorContext:
    path: str


class Detector(Protocol):
    id: str
    version: str
    supported_modes: tuple[str, ...]

    def scan(self, text: str, context: DetectorContext) -> list[Candidate]:
        """Return raw candidate matches."""

