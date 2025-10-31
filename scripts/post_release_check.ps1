# Post-release quick checks
param(
  [string]$Zip = ".\dist\GunSonu_Bundle_latest.zip",
  [string]$Exe = ".\dist\GunSonu.exe"
)
Write-Host "=== HASH ==="
if (Test-Path $Zip) { Get-FileHash $Zip -Algorithm SHA256 }
if (Test-Path $Exe) { Get-FileHash $Exe -Algorithm SHA256 }
