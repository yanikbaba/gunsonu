# Run local smoke tests
Set-Location $PSScriptRoot\..
$py = ".\.venv\Scripts\python.exe"
if (!(Test-Path $py)) { $py = "python" }
& $py "src/smoke/smoke_tests.py"
exit $LASTEXITCODE
