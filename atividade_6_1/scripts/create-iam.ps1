param(
    [string]$RoleName = "atividade-6-1-lambda-role",
    [string]$Region = "us-east-1"
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$iamDirectory = Join-Path $PSScriptRoot "..\iam"
$trustPolicy = Join-Path $iamDirectory "lambda-trust-policy.json"
$permissionsPolicy = Join-Path $iamDirectory "lambda-permissions-policy.json"

Write-Host "Criando ou verificando a Role $RoleName..."
$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
aws iam get-role --role-name $RoleName 2>$null | Out-Null
$roleLookupExitCode = $LASTEXITCODE
$ErrorActionPreference = $previousErrorActionPreference

if ($roleLookupExitCode -ne 0) {
    aws iam create-role --role-name $RoleName --assume-role-policy-document file://$trustPolicy | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel criar a Role. Verifique se sua identidade possui iam:CreateRole."
    }
}

aws iam attach-role-policy `
    --role-name $RoleName `
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel anexar a policy de logs. Verifique se sua identidade possui iam:AttachRolePolicy."
}

aws iam put-role-policy `
    --role-name $RoleName `
    --policy-name atividade-6-1-s3-sqs-policy `
    --policy-document file://$permissionsPolicy
if ($LASTEXITCODE -ne 0) {
    throw "Nao foi possivel aplicar a policy S3/SQS. Verifique se sua identidade possui iam:PutRolePolicy."
}

$role = aws iam get-role --role-name $RoleName | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) {
    throw "A Role nao foi encontrada apos a configuracao."
}
$role.Role.Arn | Set-Content -Path (Join-Path $PSScriptRoot "..\.lambda-role-arn") -NoNewline

Write-Host "Role configurada: $($role.Role.Arn)"