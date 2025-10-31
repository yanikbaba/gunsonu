param(
    [string]$Tag = "v0.8.0",
    [string]$Title = "GunSonu v0.8.0",
    [string]$NotesFile = "RELEASE_NOTES_v0.8.0.md",
    [string]$ExePath = "dist\GunSonu.exe",
    [string]$ZipPath = "dist\GunSonu_Windows.zip"
)

$ErrorActionPreference = "Stop"

Write-Host "`n=== GUNSONU RELEASE ==="

# 0) Ön kontroller
git status
if (-not (Test-Path $ExePath)) { throw "EXE bulunamadı: $ExePath" }
if (-not (Test-Path $ZipPath)) { throw "ZIP bulunamadı: $ZipPath" }
if (-not (Test-Path $NotesFile)) { throw "Release notları bulunamadı: $NotesFile" }

# 1) Tag oluştur ve gönder
git tag $Tag -m $Title
git push --tags

# 2) GitHub CLI ile release oluştur (gh yüklü değilse: winget install GitHub.cli)
$hasGh = (Get-Command gh -ErrorAction SilentlyContinue) -ne $null
if (-not $hasGh) {
    Write-Warning "gh CLI bulunamadı. Yüklemek için: winget install GitHub.cli"
    Write-Host "Alternatif: GitHub web arayüzünden Release oluşturup EXE/ZIP ve notları yükleyin."
    exit 0
}

# 3) Release oluştur (varsa silmeden yeniden deneme koruması)
try {
    gh release create $Tag `
        $ExePath `
        $ZipPath `
        --title $Title `
        --notes-file $NotesFile
}
catch {
    Write-Warning "Release oluşturulamadı, muhtemelen tag veya release zaten var. Güncellemeyi deniyorum..."
    gh release upload $Tag $ExePath $ZipPath --clobber
    gh release edit $Tag --title $Title --notes-file $NotesFile
}

Write-Host "`n=== DONE ==="
