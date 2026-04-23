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


def _replace_or_append_block(existing: str, block: str) -> str:
    if not existing.strip():
        return "#!/bin/sh\n\n" + block

    if HOOK_BEGIN in existing and HOOK_END in existing:
        start = existing.index(HOOK_BEGIN)
        end = existing.index(HOOK_END) + len(HOOK_END)
        trailing_newline = "\n" if not existing[end:].startswith("\n") else ""
        return existing[:start] + block + trailing_newline + existing[end:].lstrip("\n")

    normalized = existing
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized + "\n" + block


def install_pre_commit_hook(repo_root: Path, command: str) -> HookInstallResult:
    hooks_dir = repo_root / ".git" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "pre-commit"
    block = _render_hook(command)
    existing = ""
    if hook_path.exists():
        existing = hook_path.read_text(encoding="utf-8", errors="ignore")
    rendered = _replace_or_append_block(existing, block)

    if hook_path.exists() and existing == rendered:
        return HookInstallResult(hook_path=hook_path, installed=False, message="Hook already installed.")

    hook_path.write_text(rendered, encoding="utf-8")
    try:
        os.chmod(hook_path, 0o755)
    except OSError:
        pass
    return HookInstallResult(hook_path=hook_path, installed=True, message="Hook installed.")
