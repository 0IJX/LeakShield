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


def test_full_scan_downweights_findings_in_test_paths_by_default(clean_repo: Path) -> None:
    (clean_repo / "src").mkdir(parents=True, exist_ok=True)
    (clean_repo / "tests").mkdir(parents=True, exist_ok=True)
    secret = "sk-proj-abcdefghijklmnopqrstuvwxyz123456"
    (clean_repo / "src" / "app.py").write_text(f"TOKEN = '{secret}'\n", encoding="utf-8")
    (clean_repo / "tests" / "test_app.py").write_text(f"TOKEN = '{secret}'\n", encoding="utf-8")

    config = build_runtime_config(repo_root=clean_repo)
    service = ScanService(clean_repo, config)
    result = service.scan_full()

    src_finding = next(f for f in result.findings if f.path == "src/app.py")
    test_finding = next(f for f in result.findings if f.path == "tests/test_app.py")

    assert test_finding.confidence < src_finding.confidence
    assert test_finding.severity != src_finding.severity


def test_full_scan_can_ignore_test_paths_via_config(clean_repo: Path) -> None:
    (clean_repo / "tests").mkdir(parents=True, exist_ok=True)
    (clean_repo / "tests" / "test_leak.py").write_text(
        "token = 'ghp_abcdefghijklmnopqrstuvwxyz1234'\n",
        encoding="utf-8",
    )

    config = build_runtime_config(
        repo_root=clean_repo,
        cli_overrides={"scan": {"test_path_mode": "ignore"}},
    )
    service = ScanService(clean_repo, config)
    result = service.scan_full()

    assert all(not finding.path.startswith("tests/") for finding in result.findings)

