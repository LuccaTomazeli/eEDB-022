param(
    [string]$FunctionName = "atividade-6-1-consumidor-sql",
    [string]$Region = "us-east-1",
    [int]$MaximumConcurrency = 2
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$queueUrlFile = Join-Path $PSScriptRoot "..\.queue-url"
if (-not (Test-Path $queueUrlFile)) {
    throw "Arquivo .queue-url nao encontrado. Execute scripts/create-sqs.ps1 primeiro."
}

$queueUrl = (Get-Content $queueUrlFile -Raw).Trim()
$queueArn = aws sqs get-queue-attributes `
    --queue-url $queueUrl `
    --attribute-names QueueArn `
    --query Attributes.QueueArn `
    --output text
$functionArn = aws lambda get-function `
    --function-name $FunctionName `
    --query Configuration.FunctionArn `
    --output text

$mappingUuid = aws lambda list-event-source-mappings `
    --function-name $functionArn `
    --event-source-arn $queueArn `
    --query "EventSourceMappings[0].UUID" `
    --output text

if (-not $mappingUuid -or $mappingUuid -eq "None") {
    aws lambda create-event-source-mapping `
        --function-name $functionArn `
        --event-source-arn $queueArn `
        --batch-size 10 `
        --function-response-types ReportBatchItemFailures `
        --scaling-config "MaximumConcurrency=$MaximumConcurrency" `
        --enabled | Out-Null
} else {
    aws lambda update-event-source-mapping `
        --uuid $mappingUuid `
        --batch-size 10 `
        --function-response-types ReportBatchItemFailures `
        --scaling-config "MaximumConcurrency=$MaximumConcurrency" `
        --enabled | Out-Null
}

Write-Host "Consumidor conectado a SQS: $FunctionName"
