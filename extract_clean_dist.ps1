param(
    [string]$ZipPath = "C:\Users\Muhasebe\Desktop\gunsonu\dist\GunSonu_Dist_Clean_20251031_122624.zip",
    [string]$TargetDist = "C:\Users\Muhasebe\Desktop\gunsonu\dist"
)

$ErrorActionPreference = "Stop"
Write-Host "`n=== GUNSONU DIST DEPLOY ==="

# 0) Ön kontrol
if (-not (Test-Path $ZipPath)) { throw "ZIP bulunamadı: $ZipPath" }
if (-not (Test-Path $TargetDist)) { New-Item -ItemType Directory -Path $TargetDist | Out-Null }

# 1) Var olan dist'i yedekle
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupZip = Join-Path (Split-Path $TargetDist -Parent) ("dist_backup_{0}.zip" -f $ts)

Write-Host "Yedek alınıyor -> $BackupZip"
if (Test-Path $BackupZip) { Remove-Item -Force $BackupZip }
Compress-Archive -Path (Join-Path $TargetDist "*") -DestinationPath $BackupZip -Force -ErrorAction SilentlyContinue

# 2) Temp dizini hazırla
$Temp = Join-Path $env:TEMP ("gunsonu_dist_extract_{0}" -f $ts)
if (Test-Path $Temp) { Remove-Item -Recurse -Force $Temp }
New-Item -ItemType Directory -Path $Temp | Out-Null

# 3) Zip'i temp'e aç
Write-Host "ZIP açılıyor -> $Temp"
Expand-Archive -Path $ZipPath -DestinationPath $Temp -Force

# 4) Hedef dist içeriğini sil (klasörü değil)
Write-Host "dist temizleniyor -> $TargetDist"
Get-ChildItem $TargetDist -Force | ForEach-Object {
    try {
        if ($_.PSIsContainer) { Remove-Item -Recurse -Force $_.FullName }
        else { Remove-Item -Force $_.FullName }
    } catch {}
}

# 5) Temp içeriğini dist'e taşı
Write-Host "Yeni dist kopyalanıyor..."
Get-ChildItem $Temp -Force | ForEach-Object {
    $src = $_.FullName
    $dst = Join-Path $TargetDist $_.Name
    Copy-Item $src $dst -Recurse -Force
}

# 6) Temp'i temizle
Remove-Item -Recurse -Force $Temp

# 7) Kontrol çıktısı
Write-Host "`n=== SON DURUM (dist içeriği) ==="
Get-ChildItem $TargetDist -Recurse | Select-Object FullName, Length, LastWriteTime

Write-Host "`nTamamlandı. Yedek:" $BackupZip
