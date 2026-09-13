param(
    [string]$FunctionName = "atividade-6-1-ingestao",
    [string]$Region = "us-east-1",
    [string]$RoleArn = "arn:aws:iam::115651887176:role/LabRole"
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$bucket = "atividade-6-1-115651887176"
$key = "dados/clientes.json"
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
} else {
    aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file fileb://$packagePath | Out-Null

    aws lambda wait function-updated-v2 --function-name $FunctionName

    aws lambda update-function-configuration `
        --function-name $FunctionName `
        --environment "Variables={S3_BUCKET=$bucket,S3_KEY=$key,SQS_QUEUE_URL=$queueUrl}" | Out-Null
}

Write-Host "Lambda publicada: $FunctionName"