param(
    [string]$FunctionName = "atividade-6-1-ingestao",
    [string]$BucketName = "",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if ([string]::IsNullOrWhiteSpace($BucketName)) {
    $accountId = (aws sts get-caller-identity --query Account --output text).Trim()
    $BucketName = "atividade-6-1-$accountId"
}

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$accountId = (aws sts get-caller-identity --query Account --output text).Trim()
$functionArn = aws lambda get-function --function-name $FunctionName --query Configuration.FunctionArn --output text
$statementId = "AllowS3InvokeActivity6"

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
aws lambda remove-permission --function-name $FunctionName --statement-id $statementId 2>$null | Out-Null
$ErrorActionPreference = $previousErrorActionPreference

aws lambda add-permission `
    --function-name $FunctionName `
    --statement-id $statementId `
    --action lambda:InvokeFunction `
    --principal s3.amazonaws.com `
    --source-arn "arn:aws:s3:::$BucketName" `
    --source-account $accountId | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel conceder permissao para o S3 invocar a Lambda."
}

$notification = @{
    LambdaFunctionConfigurations = @(
        @{
            LambdaFunctionArn = $functionArn
            Events = @("s3:ObjectCreated:Put")
            Filter = @{
                Key = @{
                    FilterRules = @(
                        @{
                            Name = "prefix"
                            Value = "entrada/"
                        }
                    )
                }
            }
        }
    )
} | ConvertTo-Json -Depth 10

$notificationPath = Join-Path $env:TEMP "atividade-6-1-s3-notification.json"
$notification | Set-Content -Path $notificationPath
aws s3api put-bucket-notification-configuration `
    --bucket $BucketName `
    --notification-configuration file://$notificationPath
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel configurar o trigger S3 no bucket $BucketName."
}

Write-Host "Trigger configurado: s3:ObjectCreated:Put com prefixo entrada/"