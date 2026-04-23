"""Full-scan file discovery and loading."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from leakshield.discovery.binary_guard import should_skip_file
from leakshield.discovery.gitignore_matcher import is_git_repo, list_git_visible_files
from leakshield.discovery.leakshield_ignore import LeakshieldIgnore
from leakshield.models import ScanTarget


def _fallback_walk(repo_root: Path) -> list[Path]:
    files: list[Path] = []
    for current_root, dirs, names in os.walk(repo_root):
        current = Path(current_root)
        dirs[:] = [d for d in dirs if d != ".git"]
        for name in names:
            files.append(current / name)
    return files


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def discover_files(
    *,
    repo_root: Path,
    ignore: LeakshieldIgnore,
    max_file_size_bytes: int,
    include_globs: list[str],
    exclude_globs: list[str],
) -> list[Path]:
    if is_git_repo(repo_root):
        candidates = list_git_visible_files(repo_root)
    else:
        candidates = _fallback_walk(repo_root)

    results: list[Path] = []
    for path in candidates:
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root).as_posix()
        if ignore.matches(rel):
            continue
        if include_globs and not _matches_any(rel, include_globs):
            continue
        if exclude_globs and _matches_any(rel, exclude_globs):
            continue
        if should_skip_file(path, max_file_size_bytes=max_file_size_bytes):
            continue
        results.append(path)
    return results


def iter_targets(repo_root: Path, files: list[Path]):
    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = file_path.relative_to(repo_root).as_posix()
        yield ScanTarget(path=rel, content=text)


def build_targets(repo_root: Path, files: list[Path]) -> list[ScanTarget]:
    return list(iter_targets(repo_root, files))
