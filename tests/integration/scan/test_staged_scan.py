from __future__ import annotations

from pathlib import Path
import subprocess

from leakshield.config.merger import build_runtime_config
from leakshield.services.scan_service import ScanService


def test_staged_scan_only_reports_staged_changes(clean_repo: Path) -> None:
    tracked = clean_repo / "tracked.txt"
    tracked.write_text("safe=1\n", encoding="utf-8")
    (clean_repo / "unstaged.txt").write_text("TOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234\n", encoding="utf-8")

    subprocess.run(["git", "add", "tracked.txt"], cwd=clean_repo, check=False, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "add tracked"], cwd=clean_repo, check=False, capture_output=True, text=True)

    tracked.write_text("safe=1\nOPENAI=sk-proj-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=clean_repo, check=False, capture_output=True, text=True)

    config = build_runtime_config(repo_root=clean_repo)
    result = ScanService(clean_repo, config).scan_staged()

    paths = {finding.path for finding in result.findings}
    assert "tracked.txt" in paths
    assert "unstaged.txt" not in paths
