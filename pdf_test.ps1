#Requires -Version 5.1
<#
  GunSonu - PDF Smoke Test Runner (FPDF2 version)
  - Works on Python 3.8+ including Store Python 3.13
  - Ensures pip
  - Installs fpdf2 if missing (pure Python, wheels not required)
  - Runs pdf_probe.py to generate a deterministic PDF
#>

$ErrorActionPreference = "Stop"

function Write-Section($t){ Write-Host "`n==== $t ====" }

Write-Section "Environment"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { throw "Python not found in PATH." }
Write-Host ("Python: " + $python.Source)

Write-Section "pip check"
& python -m pip --version | Out-Host

Write-Section "Dependencies (fpdf2)"
# PowerShell-safe presence check: try import
& python -c "import sys; 
try:
 import fpdf
 sys.exit(0)
except Exception:
 sys.exit(3)"
if ($LASTEXITCODE -eq 3) {
  Write-Host "Installing fpdf2..."
  & python -m pip install --user --quiet fpdf2
}

# Prepare output dir
$outDir = Join-Path $PSScriptRoot "dist"
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir | Out-Null }

# Run probe
Write-Section "Generate PDF"
$outFile = Join-Path $outDir "gunsonu_pdf_smoke.pdf"
& python (Join-Path $PSScriptRoot "pdf_probe.py") --out "$outFile" --pages 2 --min-bytes 8192

if ($LASTEXITCODE -ne 0) { throw "pdf_probe.py failed with exit code $LASTEXITCODE" }

Write-Section "Verify PDF"
if (-not (Test-Path $outFile)) { throw "Output PDF not found: $outFile" }
$size = (Get-Item $outFile).Length
if ($size -lt 8192) { throw "PDF size too small (< 8 KB). Size: $size" }
$sha = (Get-FileHash $outFile -Algorithm SHA256).Hash
Write-Host ("Size: {0:N0} bytes" -f $size)
Write-Host ("SHA256: $sha")

try { Start-Process $outFile | Out-Null } catch {}

Write-Host "`n✅ PDF Smoke Test: SUCCESS"
exit 0
