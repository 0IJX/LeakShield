"""Pre-commit hook installer."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

HOOK_BEGIN = "# >>> leakshield >>>"
HOOK_END = "# <<< leakshield <<<"


@dataclass(slots=True)
class HookInstallResult:
    hook_path: Path
    installed: bool
    message: str


def _render_hook(command: str) -> str:
    return (
        "#!/bin/sh\n"
        f"{HOOK_BEGIN}\n"
        "echo \"LeakShield: scanning staged changes...\"\n"
        f"{command}\n"
        "status=$?\n"
        "if [ $status -ne 0 ]; then\n"
        "  echo \"LeakShield: commit blocked.\"\n"
        "  exit $status\n"
        "fi\n"
        f"{HOOK_END}\n"
    )


def install_pre_commit_hook(repo_root: Path, command: str) -> HookInstallResult:
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "pre-commit"
    rendered = _render_hook(command)

    if hook_path.exists():
        current = hook_path.read_text(encoding="utf-8", errors="ignore")
        if HOOK_BEGIN in current and HOOK_END in current and rendered == current:
            return HookInstallResult(hook_path=hook_path, installed=False, message="Hook already installed.")

    hook_path.write_text(rendered, encoding="utf-8")
    try:
        os.chmod(hook_path, 0o755)
    except OSError:
        pass
    return HookInstallResult(hook_path=hook_path, installed=True, message="Hook installed.")

