#Requires -Version 5.1
<#
  installer_smoke.ps1 — Robust uninstall check & fallback
#>

param(
  [Parameter(Mandatory=$true)][string]$SetupPath,
  [string]$InstallDir = "C:\Program Files\GunSonu",
  [string]$ExeName = "GunSonu.exe",
  [string]$ProbePath = "",
  [string]$LogDir = ".\reports"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Write-Section([string]$t){ Write-Host "`n==== $t ====" }
function Fail([string]$msg){ throw $msg }
function Log([string]$m){ $m | Tee-Object -FilePath $Log -Append | Out-Null }

# Normalize SetupPath
$SetupPath = (Resolve-Path $SetupPath).Path
if (-not (Test-Path $SetupPath)) { Fail "SetupPath not found: $SetupPath" }

# Logs
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$Log = Join-Path $LogDir "installer_smoke.log"
"GunSonu Installer Smoke Test" | Out-File -FilePath $Log -Encoding UTF8

Write-Section "Install (silent)"
$flags = @("/S", "/silent", "/verysilent")
$installed = $false
foreach ($f in $flags) {
  try {
    Log "Running: `"$SetupPath`" $f"
    & "$SetupPath" $f | Out-Null
    Start-Sleep -Seconds 4
    if (Test-Path $InstallDir) { $installed = $true; break }
  } catch {
    Log "Install attempt with flag $f failed: $($_.Exception.Message)"
  }
}

function Resolve-ActualInstallDir {
  $candidates = @(
    "C:\Program Files\GunSonu",
    "C:\Program Files (x86)\GunSonu"
  )
  foreach ($p in $candidates) { if (Test-Path $p) { return $p } }
  $lnks = @(
    "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\GunSonu\GunSonu.lnk",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\GunSonu\GunSonu.lnk"
  )
  foreach ($l in $lnks) {
    if (Test-Path $l) {
      $sh = New-Object -ComObject WScript.Shell
      $sc = $sh.CreateShortcut($l)
      if ($sc -and $sc.TargetPath) {
        $dir = Split-Path $sc.TargetPath -Parent
        if (Test-Path $dir) { return $dir }
      }
    }
  }
  $keys = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GunSonu",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\GunSonu"
  )
  foreach ($k in $keys) {
    try {
      $loc = (Get-ItemProperty -Path $k -ErrorAction Stop).InstallLocation
      if ($loc -and (Test-Path $loc)) { return $loc }
    } catch {}
  }
  return $null
}

if (-not $installed) {
  $auto = Resolve-ActualInstallDir
  if ($auto) {
    Log "Auto-detected InstallDir: $auto"
    $InstallDir = $auto
    $installed = $true
  }
}
if (-not $installed) { Fail "Install directory not found. Tried: '$InstallDir' and common locations." }

Write-Section "Validate files"
$exe = Join-Path $InstallDir $ExeName
Log "Expecting EXE: $exe"
if (-not (Test-Path $exe)) { Fail "Main executable not found: $exe" }

Write-Section "Launch app"
try {
  $p = Start-Process -FilePath $exe -PassThru
  Start-Sleep -Seconds 5
  if (!$p.HasExited) {
    Log "Stopping process (test end)"
    Stop-Process -Id $p.Id -Force
  }
} catch {
  Fail "Failed to launch/stop app: $($_.Exception.Message)"
}

if ($ProbePath -ne "") {
  Write-Section "PDF Probe"
  $ProbePath = (Resolve-Path $ProbePath).Path
  if (-not (Test-Path $ProbePath)) { Fail "ProbePath not found: $ProbePath" }
  $dist = Join-Path (Split-Path $ProbePath -Parent) "dist"
  if (-not (Test-Path $dist)) { New-Item -ItemType Directory -Path $dist | Out-Null }
  $pdf = Join-Path $dist "gunsonu_pdf_smoke_installed.pdf"
  Log "Running probe: python `"$ProbePath`" --out `"$pdf`""
  & python "$ProbePath" --out "$pdf" --pages 2 --min-bytes 8192 | Tee-Object -FilePath (Join-Path $LogDir "installer_pdf_probe.log")
  if ($LASTEXITCODE -ne 0) { Fail "PDF probe failed with exit $LASTEXITCODE" }
  if (-not (Test-Path $pdf)) { Fail "Expected PDF not found: $pdf" }
}

Write-Section "Uninstall (silent)"
$uninstCandidates = @(
  (Join-Path $InstallDir "uninstall.exe"),
  (Join-Path $InstallDir "unins000.exe")
) + (Get-ChildItem -Path $InstallDir -Filter "unins*.exe" -File -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })

$uninstalled = $false
foreach ($u in $uninstCandidates) {
  if (Test-Path $u) {
    foreach ($f in @("/S", "/silent", "/verysilent")) {
      try {
        Log "Running uninstall: `"$u`" $f"
        & "$u" $f | Out-Null
        # Wait up to 20s for folder to disappear (async/lock safe)
        for ($i=0; $i -lt 20; $i++) {
          if (-not (Test-Path $InstallDir)) { $uninstalled = $true; break }
          Start-Sleep -Seconds 1
        }
        if ($uninstalled) { break }
      } catch {
        Log "Uninstall attempt with $f failed: $($_.Exception.Message)"
      }
    }
  }
  if ($uninstalled) { break }
}

# Fallback: use ARP UninstallString if still present
if (-not $uninstalled) {
  $keys = @(
    "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\GunSonu",
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\GunSonu"
  )
  foreach ($k in $keys) {
    try {
      $uninst = (Get-ItemProperty -Path $k -ErrorAction Stop).UninstallString
      if ($uninst) {
        Log "Fallback ARP uninstall: $uninst"
        & cmd /c $uninst + " /S" | Out-Null
        for ($i=0; $i -lt 20; $i++) {
          if (-not (Test-Path $InstallDir)) { $uninstalled = $true; break }
          Start-Sleep -Seconds 1
        }
        if ($uninstalled) { break }
      }
    } catch {}
  }
}

if (-not $uninstalled) {
  Log "Leftover files:"
  Get-ChildItem -Path $InstallDir -Recurse -Force -ErrorAction SilentlyContinue | ForEach-Object { Log $_.FullName }
  Fail "Uninstall did not remove InstallDir: $InstallDir"
}

Write-Host "`n✅ Installer Smoke: SUCCESS"
Log "SUCCESS"
exit 0
