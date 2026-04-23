<#
Run environment and repo readiness checks for LeakShield.

Usage:
  powershell -ExecutionPolicy Bypass -File .\scripts\audit-env.ps1
#>

$ErrorActionPreference = "Stop"

Write-Host "== Toolchain checks ==" -ForegroundColor Cyan
git --version
python --version
node --version
npm --version
codex --version

Write-Host "`n== Codex auth check ==" -ForegroundColor Cyan
codex login status

Write-Host "`n== Repo checks ==" -ForegroundColor Cyan
git rev-parse --is-inside-work-tree
git status --short

$venvPython = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
  Write-Host "`n.venv was not found at project root." -ForegroundColor Yellow
  exit 1
}

Write-Host "`n== Python package checks (.venv) ==" -ForegroundColor Cyan
$packages = @("typer", "rich", "pyyaml", "pytest", "ruff")
foreach ($package in $packages) {
  & $venvPython -m pip show $package 1>$null 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "OK: $package"
  } else {
    Write-Host "MISSING: $package" -ForegroundColor Yellow
  }
}

Write-Host "`n== Pytest version (.venv) ==" -ForegroundColor Cyan
& $venvPython -m pytest --version
