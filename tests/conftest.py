from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, check=False, capture_output=True, text=True, env=env)


def init_git_repo(path: Path) -> None:
    run(["git", "init"], cwd=path)
    run(["git", "config", "user.email", "test@example.com"], cwd=path)
    run(["git", "config", "user.name", "LeakShield Test"], cwd=path)


@pytest.fixture()
def project_root() -> Path:
    return ROOT


@pytest.fixture()
def clean_repo(tmp_path: Path) -> Path:
    init_git_repo(tmp_path)
    (tmp_path / "README.md").write_text("test repo\n", encoding="utf-8")
    run(["git", "add", "."], cwd=tmp_path)
    run(["git", "commit", "-m", "init"], cwd=tmp_path)
    return tmp_path


@pytest.fixture()
def env_with_src(project_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(project_root / "src") + (os.pathsep + existing if existing else "")
    return env

