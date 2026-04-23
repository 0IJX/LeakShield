from __future__ import annotations

from pathlib import Path

from leakshield.services.hook_service import HookService


def test_install_hook_is_idempotent(clean_repo: Path) -> None:
    service = HookService(clean_repo)
    first = service.install()
    second = service.install()
    assert first.hook_path.exists()
    assert first.installed is True
    assert second.installed is False


def test_install_hook_preserves_existing_hook_content(clean_repo: Path) -> None:
    hook_path = clean_repo / ".git" / "hooks" / "pre-commit"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text("#!/bin/sh\necho \"custom hook\"\n", encoding="utf-8")

    service = HookService(clean_repo)
    service.install()

    content = hook_path.read_text(encoding="utf-8")
    assert "custom hook" in content
    assert ">>> leakshield >>>" in content
