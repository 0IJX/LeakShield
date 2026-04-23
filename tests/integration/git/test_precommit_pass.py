from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from leakshield.services.hook_service import HookService


def test_precommit_allows_clean_commit(clean_repo: Path, env_with_src: dict[str, str]) -> None:
    service = HookService(clean_repo)
    service.install(command=f"\"{sys.executable}\" -m leakshield.cli scan --staged --format cli")

    (clean_repo / "clean.txt").write_text("hello=world\n", encoding="utf-8")
    subprocess.run(["git", "add", "clean.txt"], cwd=clean_repo, check=False, capture_output=True, text=True)

    commit = subprocess.run(
        ["git", "commit", "-m", "should pass"],
        cwd=clean_repo,
        check=False,
        capture_output=True,
        text=True,
        env=env_with_src,
    )
    assert commit.returncode == 0
