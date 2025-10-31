#Requires -Version 5.1
<#
  build_installer.ps1
  - Builds GunSonu.exe via PyInstaller
  - Then packages setup.exe via NSIS (installer.nsi)
  Output:
    .\dist\GunSonu\GunSonu.exe
    .\dist\setup.exe
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Section($t){ Write-Host "`n==== $t ====" }

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

# Prepare dist folder
if (-not (Test-Path ".\dist")) { New-Item -ItemType Directory -Path ".\dist" | Out-Null }

Write-Section "Python / venv"
$Py = "$Root\.venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
  Write-Host "Creating venv..."
  & python -m venv .venv
  $Py = "$Root\.venv\Scripts\python.exe"
}
& $Py -m pip install --upgrade pip wheel setuptools
if (Test-Path ".\requirements.txt") {
  & $Py -m pip install -r .\requirements.txt
}

Write-Section "PyInstaller build"
& $Py -m pip install pyinstaller
# Build single-folder (onedir) to avoid hidden deps issues
& $Root\.venv\Scripts\pyinstaller.exe --noconfirm --onedir --name "GunSonu" .\app.py

if (-not (Test-Path ".\dist\GunSonu\GunSonu.exe")) {
  throw "PyInstaller output not found: .\dist\GunSonu\GunSonu.exe"
}

Write-Section "NSIS build"
$makensis = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $makensis) {
  throw "NSIS 'makensis' not found in PATH. Install NSIS and add makensis.exe to PATH."
}

if (-not (Test-Path ".\installer.nsi")) {
  throw "Missing installer.nsi"
}
& $makensis.Source ".\installer.nsi"

if (-not (Test-Path ".\dist\setup.exe")) {
  throw "NSIS did not produce dist\setup.exe"
}

Write-Host "`n✅ Build successful:"
Write-Host "  EXE : .\dist\GunSonu\GunSonu.exe"
Write-Host "  SETUP: .\dist\setup.exe"
exit 0
