"""Parse staged diff hunks to line scopes."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def parse_changed_lines_from_diff(diff_text: str) -> set[int]:
    changed: set[int] = set()
    for line in diff_text.splitlines():
        match = HUNK_RE.match(line)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or "1")
        for line_number in range(start, start + count):
            changed.add(line_number)
    return changed


def staged_changed_lines(repo_root: Path, relative_path: str) -> set[int]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--", relative_path],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return parse_changed_lines_from_diff(result.stdout)

