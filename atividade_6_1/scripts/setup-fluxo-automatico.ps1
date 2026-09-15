param(
    [string]$Region = "us-east-1",
    [string]$BucketName = ""
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$python = Join-Path $projectRoot ".venv\Scripts\python.exe"
$env:AWS_DEFAULT_REGION = $Region
$env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $projectRoot ".aws\credentials"

if ([string]::IsNullOrWhiteSpace($BucketName)) {
    $accountId = (aws sts get-caller-identity --query Account --output text).Trim()
    $BucketName = "atividade-6-1-$accountId"
}

if (-not (Test-Path $python)) {
    throw "Python do ambiente virtual nao encontrado: $python"
}

function Invoke-Step([string]$Path) {
    & $Path
    if ($LASTEXITCODE -ne 0) {
        throw "Etapa falhou: $Path"
    }
}

function Test-AwsAccess {
    $previousErrorActionPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    aws sts get-caller-identity --no-cli-pager | Out-Null
    $stsExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($stsExitCode -ne 0) {
        throw "Credenciais AWS invalidas ou expiradas. Atualize .aws\credentials."
    }

    $ErrorActionPreference = "Continue"
    $ErrorActionPreference = "Continue"
    aws lambda list-functions --max-items 1 --no-cli-pager | Out-Null
    $lambdaExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousErrorActionPreference
    if ($lambdaExitCode -ne 0) {
        throw "A identidade AWS nao tem permissao para operar Lambda. Remova o explicit deny voc-cancel-cred ou use credenciais/role autorizadas."
    }
}

Write-Host "0/8 Validando acesso AWS..."
Test-AwsAccess

Write-Host "1/9 Preparando o banco RDS..."
Write-Host "O schema sera criado pela Lambda consumidora dentro da VPC do RDS."

Write-Host "2/9 Convertendo dados para JSON..."
& $python (Join-Path $PSScriptRoot "convert-data.py")
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: convert-data.py" }

Write-Host "3/9 Criando ou verificando SQS..."
& (Join-Path $PSScriptRoot "create-sqs.ps1")
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: create-sqs.ps1" }

Write-Host "4/9 Criando ou verificando o bucket..."
& (Join-Path $PSScriptRoot "create-s3.ps1") -BucketName $BucketName -Region $Region -SkipUpload
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: create-s3.ps1 (criacao do bucket)" }

Write-Host "5/9 Publicando Lambda de ingestao..."
& (Join-Path $PSScriptRoot "deploy-lambda.ps1")
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: deploy-lambda.ps1" }

Write-Host "6/9 Configurando trigger S3..."
& (Join-Path $PSScriptRoot "configure-s3-trigger.ps1")
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: configure-s3-trigger.ps1" }

Write-Host "7/9 Publicando Lambda consumidora com enriquecimento..."
& (Join-Path $PSScriptRoot "deploy-consumer-lambda.ps1")
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: deploy-consumer-lambda.ps1" }

Write-Host "8/9 Conectando SQS ao consumidor..."
& (Join-Path $PSScriptRoot "configure-sqs-consumer.ps1")
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: configure-sqs-consumer.ps1" }

Write-Host "9/9 Enviando dados ao S3 e disparando o fluxo..."
& (Join-Path $PSScriptRoot "create-s3.ps1") -BucketName $BucketName -Region $Region
if ($LASTEXITCODE -ne 0) { throw "Etapa falhou: create-s3.ps1 (upload)" }

Write-Host "Fluxo automatico configurado e dados enviados."
