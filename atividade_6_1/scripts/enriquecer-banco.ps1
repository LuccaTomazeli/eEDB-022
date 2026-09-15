param(
    [string]$OutputKey = "enriquecidos/dados_enriquecidos.json"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$script = Join-Path $PSScriptRoot "enrich_database.py"

if (-not (Test-Path $python)) {
    throw "Python do ambiente virtual nao encontrado: $python"
}

$env:S3_ENRICHED_KEY = $OutputKey
& $python $script
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
