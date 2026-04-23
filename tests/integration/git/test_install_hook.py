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

