"""Hook orchestration service."""

from __future__ import annotations

from pathlib import Path

from leakshield.git.hook_installer import HookInstallResult, install_pre_commit_hook


class HookService:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def install(self, command: str = "leakshield scan --staged --format cli") -> HookInstallResult:
        return install_pre_commit_hook(self.repo_root, command=command)

