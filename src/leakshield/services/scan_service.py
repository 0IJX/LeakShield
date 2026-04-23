"""Scan orchestration service."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Iterable

from leakshield.config.schema import LeakshieldConfig
from leakshield.detectors.registry import DetectorRegistry
from leakshield.discovery.file_walker import discover_files, iter_targets
from leakshield.discovery.leakshield_ignore import LeakshieldIgnore
from leakshield.git.diff_hunks import staged_changed_lines
from leakshield.git.staged_content import read_staged_content
from leakshield.git.staged_files import list_staged_files
from leakshield.models import Finding, ScanMode, ScanResult, ScanSummary, ScanTarget
from leakshield.reporting.exit_policy import should_block
from leakshield.services.pipeline import PipelineOptions, run_pipeline


class ScanService:
    """Scan service for full and staged modes."""

    def __init__(self, repo_root: Path, config: LeakshieldConfig) -> None:
        self.repo_root = repo_root
        self.config = config
        self.registry = DetectorRegistry(
            detectors=None if config.detectors.regex_enabled else []
        )

    def scan(self, *, staged: bool) -> ScanResult:
        return self.scan_staged() if staged else self.scan_full()

    def scan_full(self) -> ScanResult:
        start = time.perf_counter()
        ignore = LeakshieldIgnore.from_repo(self.repo_root)
        files = discover_files(
            repo_root=self.repo_root,
            ignore=ignore,
            max_file_size_bytes=self.config.scan.max_file_size_bytes,
            include_globs=self.config.scan.include_globs,
            exclude_globs=self.config.scan.exclude_globs,
        )
        findings, scanned_files = self._scan_targets(iter_targets(self.repo_root, files))
        blocked = should_block(findings, self.config.thresholds.block_severity)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return ScanResult(
            mode=ScanMode.FULL,
            findings=findings,
            summary=ScanSummary.from_findings(
                findings=findings,
                scanned_files=scanned_files,
                duration_ms=duration_ms,
                blocked=blocked,
            ),
        )

    def scan_staged(self) -> ScanResult:
        start = time.perf_counter()
        ignore = LeakshieldIgnore.from_repo(self.repo_root)
        targets: list[ScanTarget] = []
        for relative_path in list_staged_files(self.repo_root):
            if ignore.matches(relative_path):
                continue
            content = read_staged_content(self.repo_root, relative_path)
            if content is None:
                continue
            lines = staged_changed_lines(self.repo_root, relative_path)
            targets.append(
                ScanTarget(
                    path=relative_path.replace("\\", "/"),
                    content=content,
                    # If diff hunk parsing yields no line scope, fall back to full
                    # staged content scan so staged mode still detects clear leaks.
                    changed_lines=lines if lines else None,
                    is_staged=True,
                )
            )
        findings, scanned_files = self._scan_targets(targets)
        blocked = should_block(findings, self.config.thresholds.block_severity)
        duration_ms = int((time.perf_counter() - start) * 1000)
        return ScanResult(
            mode=ScanMode.STAGED,
            findings=findings,
            summary=ScanSummary.from_findings(
                findings=findings,
                scanned_files=scanned_files,
                duration_ms=duration_ms,
                blocked=blocked,
            ),
        )

    def _scan_targets(self, targets: Iterable[ScanTarget]) -> tuple[list[Finding], int]:
        options = PipelineOptions(
            allowlist=self.config.allowlist,
            entropy_threshold=self.config.thresholds.entropy_threshold,
            min_confidence=self.config.thresholds.min_confidence,
            enable_entropy=self.config.detectors.entropy_enabled,
            test_path_mode=self.config.scan.test_path_mode,
            test_path_confidence_multiplier=self.config.scan.test_path_confidence_multiplier,
        )
        findings: list[Finding] = []
        scanned_files = 0
        for target in targets:
            scanned_files += 1
            findings.extend(
                run_pipeline(
                    target=target,
                    detector_registry=self.registry,
                    options=options,
                    ignore_path=False,
                )
            )
        findings.sort(key=lambda item: (item.path, item.line, item.column))
        return findings, scanned_files
