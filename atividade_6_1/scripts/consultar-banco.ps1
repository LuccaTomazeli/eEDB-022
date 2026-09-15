param(
    [int]$Limit = 2
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$script = Join-Path $PSScriptRoot "query_database.py"

if (-not (Test-Path $python)) {
    throw "Python do ambiente virtual nao encontrado: $python"
}

if ($Limit -lt 1) {
    throw "O parametro -Limit deve ser maior que zero."
}

& $python $script --limit $Limit
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
