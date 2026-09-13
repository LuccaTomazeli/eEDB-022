param(
    [string]$BucketName = "atividade-6-1-115651887176",
    [string]$Region = "us-east-1",
    [string]$FilePath = "data/clientes.json",
    [string]$ObjectKey = "dados/clientes.json"
)

$ErrorActionPreference = "Stop"

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$env:AWS_DEFAULT_REGION = $Region

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

Write-Host "Enviando $FilePath para s3://$BucketName/$ObjectKey..."
aws s3 cp $FilePath "s3://$BucketName/$ObjectKey"

Write-Host "Objeto enviado com sucesso."
aws s3api head-object --bucket $BucketName --key $ObjectKey