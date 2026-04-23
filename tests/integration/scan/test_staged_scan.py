from __future__ import annotations

from pathlib import Path
import subprocess

from leakshield.config.merger import build_runtime_config
import leakshield.services.scan_service as scan_service_module
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


def test_staged_scan_detects_openai_key_in_staged_env_file(clean_repo: Path) -> None:
    staged_file = clean_repo / "leakshield_test.env"
    staged_file.write_text('OPENAI_API_KEY="sk-proj-test1234567890abcdef"\n', encoding="utf-8")
    subprocess.run(["git", "add", staged_file.name], cwd=clean_repo, check=True, capture_output=True, text=True)

    config = build_runtime_config(repo_root=clean_repo)
    result = ScanService(clean_repo, config).scan_staged()

    assert any(f.path == staged_file.name and f.type == "openai_api_key" for f in result.findings)
    assert result.summary.blocked is True


def test_staged_scan_falls_back_to_full_content_when_line_scope_missing(
    clean_repo: Path, monkeypatch
) -> None:
    staged_file = clean_repo / "leakshield_test.env"
    staged_file.write_text('OPENAI_API_KEY="sk-proj-test1234567890abcdef"\n', encoding="utf-8")
    subprocess.run(["git", "add", staged_file.name], cwd=clean_repo, check=True, capture_output=True, text=True)

    config = build_runtime_config(repo_root=clean_repo)
    service = ScanService(clean_repo, config)
    monkeypatch.setattr(scan_service_module, "staged_changed_lines", lambda *_args, **_kwargs: set())
    result = service.scan_staged()

    assert any(f.path == staged_file.name and f.type == "openai_api_key" for f in result.findings)
