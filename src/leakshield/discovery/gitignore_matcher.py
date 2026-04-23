"""Git-aware file listing."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run_git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def is_git_repo(repo_root: Path) -> bool:
    result = _run_git(repo_root, ["rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def list_git_visible_files(repo_root: Path) -> list[Path]:
    result = _run_git(repo_root, ["ls-files", "-co", "--exclude-standard"])
    if result.returncode != 0:
        return []
    files: list[Path] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        files.append(repo_root / line.strip())
    return files

