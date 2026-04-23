"""Environment diagnostics service."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from leakshield.discovery.gitignore_matcher import is_git_repo


@dataclass(slots=True)
class DoctorCheck:
    name: str
    ok: bool
    message: str


@dataclass(slots=True)
class DoctorReport:
    checks: list[DoctorCheck]

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)


class DoctorService:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def run(self) -> DoctorReport:
        checks: list[DoctorCheck] = []

        git_path = shutil.which("git")
        checks.append(
            DoctorCheck(
                name="git",
                ok=bool(git_path),
                message="Git available" if git_path else "Git executable not found in PATH",
            )
        )

        in_repo = is_git_repo(self.repo_root)
        checks.append(
            DoctorCheck(
                name="repository",
                ok=in_repo,
                message="Git repository detected" if in_repo else "Current directory is not a Git repository",
            )
        )

        if git_path and in_repo:
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_root,
                check=False,
                capture_output=True,
                text=True,
            )
            checks.append(
                DoctorCheck(
                    name="git_status",
                    ok=status.returncode == 0,
                    message="Git status command works" if status.returncode == 0 else "Unable to run git status",
                )
            )

        return DoctorReport(checks=checks)

