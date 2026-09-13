$ErrorActionPreference = "Stop"
$queueUrlFile = Join-Path $PSScriptRoot "..\.queue-url"

if (-not (Test-Path $queueUrlFile)) {
    throw "Arquivo .queue-url nao encontrado. Execute scripts/create-sqs.ps1 primeiro."
}

$queueUrl = (Get-Content $queueUrlFile -Raw).Trim()
$response = aws sqs receive-message --queue-url $queueUrl --max-number-of-messages 1 --wait-time-seconds 5 | ConvertFrom-Json

if (-not $response.Messages) {
    Write-Host "Nenhuma mensagem encontrada."
    exit 0
}

$message = $response.Messages[0]
Write-Host "Mensagem recebida:"
Write-Output $message.Body

aws sqs delete-message --queue-url $queueUrl --receipt-handle $message.ReceiptHandle | Out-Null
Write-Host "Mensagem removida da fila apos a leitura."