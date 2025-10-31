
# update_db_model_expenses_v2.ps1 — ensure insert_expense writes category + branch safely
param(
  [Parameter(Mandatory=$false)]
  [string]$FilePath = ".\db_model.py"
)

if (!(Test-Path $FilePath)) { throw "File not found: $FilePath" }

$content = Get-Content $FilePath -Raw

# Ensure function signature includes category with default ''
$content = $content -replace "def insert_expense\([^\)]*\):", "def insert_expense(db_path: str, *, date: str, amount: float, description: str = \"\", branch: str = \"\", category: str = \"\"):

    # Failsafe: normalize category
    if category is None:
        category = \"\"
    con = _connect(db_path)
    try:
        cur = con.execute(
            \"INSERT INTO expenses(date, category, amount, description, branch) VALUES (?,?,?,?,?)\",
            (date, category, float(amount), description, branch)
        )
        con.commit()
        return int(cur.lastrowid)
    finally:
        con.close()
"

Set-Content -Path $FilePath -Value $content -Encoding UTF8
Write-Host "✅ Patched: $FilePath (V2)"
