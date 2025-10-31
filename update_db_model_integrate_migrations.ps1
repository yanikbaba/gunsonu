
# update_db_model_integrate_migrations.ps1 — inject migration call into ensure_schema()
param(
  [Parameter(Mandatory=$false)]
  [string]$FilePath = ".\db_model.py"
)

if (!(Test-Path $FilePath)) { throw "File not found: $FilePath" }

$content = Get-Content $FilePath -Raw

if ($content -notmatch "import db_migrations") {
  $content = $content -replace "(?s)^(import sqlite3[^\n]*\n)", '$1import db_migrations' + "`n"
}

# Ensure ensure_schema calls migrate before opening connection
if ($content -match "def ensure_schema\(db_path") {
  $content = $content -replace "def ensure_schema\((.*?)\):\s*\n", "def ensure_schema(`$1):`n    db_migrations.migrate(db_path)`n"
}

Set-Content -Path $FilePath -Value $content -Encoding UTF8
Write-Host "✅ Patched: $FilePath"
