from __future__ import annotations

from leakshield.filtering.allowlist import Allowlist, is_allowlisted
from leakshield.models import Candidate


def _candidate(value: str, path: str = "src/app.py") -> Candidate:
    return Candidate(
        detector_id="github_token",
        secret_type="github_token",
        path=path,
        line=1,
        column=1,
        value=value,
        context_line=value,
    )


def test_allowlist_by_value() -> None:
    allowlist = Allowlist(values=["ghp_abcdefghijklmnopqrstuvwxyz1234"])
    assert is_allowlisted(_candidate("ghp_abcdefghijklmnopqrstuvwxyz1234"), allowlist)


def test_allowlist_by_path() -> None:
    allowlist = Allowlist(paths=["tests/*"])
    assert is_allowlisted(_candidate("secret", path="tests/fixture.py"), allowlist)

