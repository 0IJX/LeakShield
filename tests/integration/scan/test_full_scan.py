from __future__ import annotations

from pathlib import Path

from leakshield.config.merger import build_runtime_config
from leakshield.services.scan_service import ScanService


def test_full_scan_respects_gitignore_and_detects_seeded_secret(clean_repo: Path) -> None:
    (clean_repo / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    (clean_repo / "ignored.txt").write_text("TOKEN=ghp_abcdefghijklmnopqrstuvwxyz1234\n", encoding="utf-8")
    (clean_repo / "app.env").write_text("OPENAI_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
    (clean_repo / "blob.bin").write_bytes(b"\x00\x01\x02\x03")

    config = build_runtime_config(repo_root=clean_repo)
    service = ScanService(clean_repo, config)
    result = service.scan_full()

    assert any("app.env" in finding.path for finding in result.findings)
    assert all("ignored.txt" not in finding.path for finding in result.findings)
    assert result.summary.scanned_files >= 1

