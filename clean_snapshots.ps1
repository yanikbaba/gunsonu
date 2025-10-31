# .\.snapshots klasörünü güvenli biçimde temizler (yalnızca test ortamında kullanın)
$dir = ".\.snapshots"
if (Test-Path $dir) {
  Get-ChildItem -Path $dir -Filter *.sqlite | Remove-Item -Force -ErrorAction SilentlyContinue
  Write-Host "🧹 .snapshots temizlendi."
} else {
  Write-Host "Bilgi: .snapshots klasörü yok."
}
