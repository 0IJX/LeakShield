from __future__ import annotations

from pathlib import Path

from leakshield.detectors.base import DetectorContext
from leakshield.detectors.regex_detector import RegexDetector


def test_regex_detector_finds_expected_secret_types() -> None:
    sample = Path("tests/fixtures/detectors/samples.txt").read_text(encoding="utf-8")
    detector = RegexDetector()
    candidates = detector.scan(sample, DetectorContext(path="samples.txt"))
    secret_types = {candidate.secret_type for candidate in candidates}
    assert "openai_api_key" in secret_types
    assert "aws_access_key" in secret_types
    assert "github_token" in secret_types
    assert "jwt" in secret_types
    assert "bearer_token" in secret_types
    assert "db_connection" in secret_types
    assert "env_secret" in secret_types


def test_regex_detector_provides_line_numbers() -> None:
    text = "A=1\nTOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234\nB=2\n"
    detector = RegexDetector()
    candidates = detector.scan(text, DetectorContext(path="x.env"))
    github = [candidate for candidate in candidates if candidate.secret_type == "github_token"][0]
    assert github.line == 2
    assert github.column >= 1

