#Requires -Version 5.1
<#
  build_installer_autopath.ps1
  - Builds GunSonu.exe via PyInstaller
  - Auto-discovers makensis.exe (NSIS) without requiring PATH
  - Packages setup.exe via NSIS (installer.nsi)
  Output:
    .\dist\GunSonu\GunSonu.exe
    .\dist\setup.exe
#>

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Section($t){ Write-Host "`n==== $t ====" }
function Find-Makensis {
  # 1) If in PATH:
  $cmd = Get-Command makensis -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }

  # 2) Common install dirs:
  $candidates = @(
    "C:\Program Files\NSIS\makensis.exe",
    "C:\Program Files (x86)\NSIS\makensis.exe"
  )
  foreach ($p in $candidates) { if (Test-Path $p) { return $p } }

  # 3) Registry (x64 & x86)
  $keys = @(
    "HKLM:\SOFTWARE\NSIS",
    "HKLM:\SOFTWARE\WOW6432Node\NSIS"
  )
  foreach ($k in $keys) {
    try {
      $inst = (Get-ItemProperty -Path $k -ErrorAction Stop).InstallDir
      if ($inst) {
        $exe = Join-Path $inst "makensis.exe"
        if (Test-Path $exe) { return $exe }
      }
    } catch {}
  }

  # 4) Chocolatey / Scoop defaults (if any)
  $more = @(
    "$env:ChocolateyInstall\lib\nsis\tools\makensis.exe",
    "$env:USERPROFILE\scoop\apps\nsis\current\makensis.exe"
  )
  foreach ($p in $more) { if ($p -and (Test-Path $p)) { return $p } }

  throw "NSIS 'makensis' not found. Install via: winget install NSIS.NSIS  (veya) choco install nsis"
}

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
& $Root\.venv\Scripts\pyinstaller.exe --noconfirm --onedir --name "GunSonu" .\app.py

if (-not (Test-Path ".\dist\GunSonu\GunSonu.exe")) {
  throw "PyInstaller output not found: .\dist\GunSonu\GunSonu.exe"
}

Write-Section "Resolve makensis"
$Makensis = Find-Makensis
Write-Host ("makensis: " + $Makensis)

Write-Section "NSIS build"
if (-not (Test-Path ".\installer.nsi")) {
  throw "Missing installer.nsi"
}
& "$Makensis" ".\installer.nsi"

if (-not (Test-Path ".\dist\setup.exe")) {
  throw "NSIS did not produce dist\setup.exe"
}

Write-Host "`n✅ Build successful:"
Write-Host "  EXE : .\dist\GunSonu\GunSonu.exe"
Write-Host "  SETUP: .\dist\setup.exe"
exit 0
