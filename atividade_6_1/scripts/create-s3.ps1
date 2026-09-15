param(
    [string]$BucketName = "",
    [string]$Region = "us-east-1",
    [string]$FilePath = "dados_json",
    [string]$ObjectPrefix = "entrada",
    [switch]$SkipUpload
)

$ErrorActionPreference = "Stop"

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$env:AWS_DEFAULT_REGION = $Region

if ([string]::IsNullOrWhiteSpace($BucketName)) {
    $accountId = (aws sts get-caller-identity --query Account --output text).Trim()
    $BucketName = "atividade-6-1-$accountId"
}

Write-Host "Criando ou verificando o bucket $BucketName..."
$bucketExists = $true
$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
aws s3api head-bucket --bucket $BucketName 2>$null
$headBucketExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference
if ($headBucketExitCode -ne 0) {
    $bucketExists = $false
}

if (-not $bucketExists) {
    if ($Region -eq "us-east-1") {
        aws s3api create-bucket --bucket $BucketName --region $Region
    } else {
        aws s3api create-bucket --bucket $BucketName --region $Region --create-bucket-configuration LocationConstraint=$Region
    }
}

if ($SkipUpload) {
    Write-Host "Bucket pronto: $BucketName"
    exit 0
}

if (Test-Path $FilePath -PathType Container) {
    Write-Host "Enviando os JSON de $FilePath para s3://$BucketName/$ObjectPrefix/..."
    aws s3 sync $FilePath "s3://$BucketName/$ObjectPrefix" --exclude "*" --include "*.json"
    Write-Host "Arquivos JSON enviados com sucesso."
} else {
    $objectKey = "$ObjectPrefix/$(Split-Path $FilePath -Leaf)"
    Write-Host "Enviando $FilePath para s3://$BucketName/$objectKey..."
    aws s3 cp $FilePath "s3://$BucketName/$objectKey"
    Write-Host "Arquivo enviado com sucesso."
}