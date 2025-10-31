#Requires -Version 5.1
<#
  GunSonu - Unified Test Runner
  - (1) Activate venv if present
  - (2) Run pytest and write JUnit to .\reports\junit.xml
  - (3) Run PDF smoke test (fpdf2) via pdf_test.ps1
  - (4) Combine results, write .\reports\summary.txt and exit non-zero on any failure
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Section($t){ Write-Host "`n==== $t ====" }

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

# Prepare reports dir
$Reports = Join-Path $Root "reports"
if (-not (Test-Path $Reports)) { New-Item -ItemType Directory -Path $Reports | Out-Null }

# --- Python / venv ---
Write-Section "Python / venv"
$Py = "$Root\.venv\Scripts\python.exe"
if (Test-Path $Py) {
  Write-Host "Using venv: $Py"
} else {
  $Py = (Get-Command python).Source
  Write-Host "Using system python: $Py"
}

# --- PyTest ---
Write-Section "PyTest"
$JUnit = Join-Path $Reports "junit.xml"
$pytestArgs = @("-m","pytest","-q","--disable-warnings","--maxfail=1","--junitxml",$JUnit)
& $Py $pytestArgs
$pytestExit = $LASTEXITCODE
if ($pytestExit -ne 0) { Write-Host "PyTest FAILED (exit=$pytestExit)" } else { Write-Host "PyTest OK" }

# --- PDF Smoke ---
Write-Section "PDF Smoke"
$PdfLog = Join-Path $Reports "pdf_smoke.log"
$PdfScript = Join-Path $Root "pdf_test.ps1"
if (-not (Test-Path $PdfScript)) { throw "Missing $PdfScript" }

# Run with ExecutionPolicy Bypass and capture output to log
& powershell -NoProfile -ExecutionPolicy Bypass -File $PdfScript *>&1 | Tee-Object -FilePath $PdfLog
$pdfExit = $LASTEXITCODE
if ($pdfExit -ne 0) { Write-Host "PDF Smoke FAILED (exit=$pdfExit)" } else { Write-Host "PDF Smoke OK" }

# --- Summary ---
Write-Section "Summary"
$Summary = Join-Path $Reports "summary.txt"
$sha = ""
if (Test-Path $PdfLog) {
  $line = Select-String -Path $PdfLog -Pattern "^SHA256:\s*(.+)$" -SimpleMatch:$false -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($line) {
    $sha = ($line.Matches[0].Groups[1].Value).Trim()
  }
}
$size = ""
if (Test-Path $PdfLog) {
  $line2 = Select-String -Path $PdfLog -Pattern "^Size:\s*(.+)\s*bytes" -SimpleMatch:$false -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($line2) {
    $size = ($line2.Matches[0].Groups[1].Value).Trim()
  }
}

@(
  "PyTest exit: $pytestExit"
  "PDF Smoke exit: $pdfExit"
  "PDF Size: $size"
  "PDF SHA256: $sha"
) | Out-File -FilePath $Summary -Encoding UTF8

$overall = 0
if ($pytestExit -ne 0 -or $pdfExit -ne 0) { $overall = 1 }

Write-Host "`nOverall exit code: $overall"
exit $overall
