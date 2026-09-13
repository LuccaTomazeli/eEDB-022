param(
    [string]$QueueName = "atividade-6-1-fila",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

Write-Host "Criando ou verificando a fila $QueueName..."
$queueUrl = aws sqs create-queue --queue-name $QueueName --attributes VisibilityTimeout=30 | ConvertFrom-Json | Select-Object -ExpandProperty QueueUrl
$queueUrl | Set-Content -Path (Join-Path $PSScriptRoot "..\.queue-url") -NoNewline

Write-Host "URL da fila: $queueUrl"

$testMessage = '{"id":0,"nome":"Teste SQS","email":"teste@email.com"}'
aws sqs send-message --queue-url $queueUrl --message-body $testMessage | Out-Null

Write-Host "Mensagem de teste enviada com sucesso."