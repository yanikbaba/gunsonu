#Requires -Version 5.1
<#
  GunSonu - CI Orchestrator
  Intended for local preflight or simple CI agents.
  Steps:
    - Ensure reports dir clean
    - Run unified tests (run_tests.ps1)
    - Emit pass/fail with clear code
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

$Reports = Join-Path $Root "reports"
if (-not (Test-Path $Reports)) { New-Item -ItemType Directory -Path $Reports | Out-Null }

# Optional: clean old logs
Get-ChildItem $Reports -File -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue

$Runner = Join-Path $Root "run_tests.ps1"
if (-not (Test-Path $Runner)) { throw "Missing run_tests.ps1" }

Write-Host "=== GunSonu CI Orchestrator ==="
& powershell -NoProfile -ExecutionPolicy Bypass -File $Runner
$code = $LASTEXITCODE
if ($code -eq 0) {
  Write-Host "✅ ALL TESTS PASSED"
} else {
  Write-Host "❌ TESTS FAILED (exit=$code)"
}
exit $code
