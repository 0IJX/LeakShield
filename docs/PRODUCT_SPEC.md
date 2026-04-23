# LeakShield Phase 1 Product Spec

## Summary
LeakShield is a local-first CLI guardrail that prevents secrets from entering Git history by scanning code before commit and blocking high-confidence leaks.

The MVP prioritizes trust, speed, and low-friction developer workflows, with architecture choices that allow a future paid team/CI product without changing the local-first core.

## 1) Target Users
- Individual developers shipping code from local Git repositories.
- Startup engineering teams without dedicated AppSec staff.
- Security-conscious open-source maintainers.
- Platform/DevOps teams that want standardized local secret prevention.

## 2) Real-World Use Cases
- A developer accidentally stages `.env` values and tries to commit.
- A backend engineer pastes an API token or JWT into test code.
- A developer commits an AWS, GitHub, or OpenAI key during debugging.
- A team installs a pre-commit hook once and gets automatic local enforcement.
- A repository owner runs a full scan before publishing/open-sourcing a project.

## 3) Pain Points Solved
- Secrets discovered too late in CI or after merge.
- Costly incident response: key rotation, token revocation, and audit overhead.
- Noisy tools with too many false positives causing alert fatigue.
- Slow scanners that interrupt commit flow.
- Security tools that require uploading source code externally.

## 4) MVP Scope (Strict)

### In Scope
- CLI commands:
  - `leakshield scan`
  - `leakshield scan --staged`
  - `leakshield install-hook`
  - `leakshield doctor`
- Detection:
  - Regex detectors for common secret formats.
  - Entropy heuristics for suspicious high-entropy strings.
  - Context filtering and placeholder suppression (for example `YOUR_API_KEY`).
  - Finding classification with type, severity, and confidence.
- Git integration:
  - Pre-commit hook.
  - Staged diff scanning.
  - Commit blocking on critical findings.
- Ignore and allow controls:
  - `.leakshieldignore`.
  - Config-based allowlist entries.
- Output and UX:
  - Clean terminal UX.
  - Masked values only.
  - File and line references.
  - JSON output mode for automation.
- Security posture:
  - Local-only analysis.
  - No secret persistence.
  - No full secret printing.

### Out of Scope (MVP)
- Cloud dashboard, centralized policy management, or remote telemetry.
- CI SaaS service and enterprise SSO/RBAC.
- Auto-remediation commits.
- ML-based classifier training pipeline.
- IDE plugins beyond basic CLI integration.

## 5) Future Roadmap (Phased)
- Phase A (Post-MVP): Better detector coverage, repository baseline support, faster incremental scanning, and improved suppression ergonomics.
- Phase B: Team features in OSS-compatible mode, including policy bundles, shared rule packs, and audit-friendly local reports.
- Phase C (Monetization start): Paid team dashboard, CI integration, policy analytics, and centralized exceptions.
- Phase D (Enterprise): Organization governance, compliance exports, managed detector updates, and enterprise support controls.

## 6) Key Risks and Product Mitigations

### False Positives
- Risk: Commit friction and tool abandonment.
- Mitigation: Confidence scoring, context-aware filtering, explicit placeholder handling, and precise allowlist paths/patterns.

### Performance
- Risk: Slow commits reduce adoption.
- Mitigation: Staged-only mode, binary skipping, `.gitignore` awareness, and efficient file traversal with detector short-circuiting.

### Developer Friction
- Risk: Hook bypassing or full tool disablement.
- Mitigation: Clear messaging, actionable remediation guidance, easy install/uninstall, and predictable config/ignore flows.

## MVP Success Criteria
- Blocks critical leaks reliably in pre-commit flow.
- Keeps median staged scan latency low enough for daily use.
- Produces readable, masked, actionable findings.
- Delivers low-noise detection quality on representative repositories.
- Is publish-ready as an open-source CLI with contributor docs and tests.

## Assumptions
- Primary delivery target is Python 3.12+ local CLI usage.
- Local-first and prevention-first are non-negotiable.
- Monetization is additive (team/CI features), not a replacement for the free local CLI.
