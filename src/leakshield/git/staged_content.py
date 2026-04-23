"""Read staged file content from git index."""

from __future__ import annotations

import subprocess
from pathlib import Path


def read_staged_content(repo_root: Path, relative_path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f":{relative_path}"],
        cwd=repo_root,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    try:
        return result.stdout.decode("utf-8")
    except UnicodeDecodeError:
        return result.stdout.decode("utf-8", errors="ignore")

