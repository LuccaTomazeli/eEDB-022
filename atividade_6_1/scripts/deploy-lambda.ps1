param(
    [string]$FunctionName = "atividade-6-1-ingestao",
    [string]$Region = "us-east-1",
    [string]$RoleArn = ""
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$accountId = (aws sts get-caller-identity --query Account --output text).Trim()
$bucket = "atividade-6-1-$accountId"
if ([string]::IsNullOrWhiteSpace($RoleArn)) {
    $RoleArn = "arn:aws:iam::${accountId}:role/LabRole"
}
$key = "entrada/bancos/EnquadramentoInicia_v2.json"
$queueUrl = (Get-Content (Join-Path $PSScriptRoot "..\.queue-url") -Raw).Trim()
$packagePath = Join-Path $PSScriptRoot "..\lambda.zip"
$lambdaPath = Join-Path $PSScriptRoot "..\lambda"

if (Test-Path $packagePath) {
    Remove-Item $packagePath -Force
}

Compress-Archive -Path (Join-Path $lambdaPath "*") -DestinationPath $packagePath

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
aws lambda get-function --function-name $FunctionName 2>$null | Out-Null
$functionLookupExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

if ($functionLookupExitCode -ne 0) {
    aws lambda create-function `
        --function-name $FunctionName `
        --runtime python3.12 `
        --handler lambda_function.lambda_handler `
        --role $RoleArn `
        --zip-file fileb://$packagePath `
        --environment "Variables={S3_BUCKET=$bucket,S3_KEY=$key,SQS_QUEUE_URL=$queueUrl}"
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel criar a Lambda $FunctionName."
    }
} else {
    aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file fileb://$packagePath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel atualizar o codigo da Lambda $FunctionName."
    }

    aws lambda wait function-updated-v2 --function-name $FunctionName

    aws lambda update-function-configuration `
        --function-name $FunctionName `
        --environment "Variables={S3_BUCKET=$bucket,S3_KEY=$key,SQS_QUEUE_URL=$queueUrl}" | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel atualizar a configuracao da Lambda $FunctionName."
    }
}

Write-Host "Lambda publicada: $FunctionName"