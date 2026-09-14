param(
    [string]$FunctionName = "atividade-6-1-consumidor-sql",
    [string]$Region = "us-east-1",
    [string]$RoleArn = "arn:aws:iam::115651887176:role/LabRole",
    [string]$SqlHost = $env:SQL_HOST,
    [string]$SqlPort = $(if ($env:SQL_PORT) { $env:SQL_PORT } else { "3306" }),
    [string]$SqlUser = $env:SQL_USER,
    [string]$SqlPassword = $env:SQL_PASSWORD,
    [string]$SqlDatabase = $env:SQL_DATABASE
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$envFile = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)\s*=\s*(.*)\s*$') {
            [Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim())
        }
    }
}

$SqlHost = if ($env:SQL_HOST) { $env:SQL_HOST } else { $SqlHost }
$SqlPort = if ($env:SQL_PORT) { $env:SQL_PORT } else { $SqlPort }
$SqlUser = if ($env:SQL_USER) { $env:SQL_USER } else { $SqlUser }
$SqlPassword = if ($env:SQL_PASSWORD) { $env:SQL_PASSWORD } else { $SqlPassword }
$SqlDatabase = if ($env:SQL_DATABASE) { $env:SQL_DATABASE } else { $SqlDatabase }

foreach ($value in @{
    SQL_HOST = $SqlHost
    SQL_USER = $SqlUser
    SQL_PASSWORD = $SqlPassword
    SQL_DATABASE = $SqlDatabase
}.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($value.Value)) {
        throw "Defina a variavel `$env:$($value.Key) ou informe o parametro correspondente."
    }
}

$packagePath = Join-Path $PSScriptRoot "..\consumer-lambda.zip"
$packageDirectory = Join-Path $env:TEMP "atividade-6-1-consumer-package"
$lambdaPath = Join-Path $PSScriptRoot "..\lambda_consumer"

if (Test-Path $packagePath) {
    Remove-Item $packagePath -Force
}
if (Test-Path $packageDirectory) {
    Remove-Item $packageDirectory -Recurse -Force
}
New-Item -ItemType Directory -Path $packageDirectory | Out-Null

python -m pip install --disable-pip-version-check --no-compile `
    --target $packageDirectory `
    --platform manylinux2014_x86_64 `
    --implementation cp `
    --python-version 3.12 `
    --only-binary=:all: `
    --requirement (Join-Path $lambdaPath "requirements.txt")
Copy-Item (Join-Path $lambdaPath "lambda_function.py") $packageDirectory
Compress-Archive -Path (Join-Path $packageDirectory "*") -DestinationPath $packagePath

$environment = "Variables={SQL_HOST=$SqlHost,SQL_PORT=$SqlPort,SQL_USER=$SqlUser,SQL_PASSWORD=$SqlPassword,SQL_DATABASE=$SqlDatabase}"
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
        --timeout 30 `
        --environment $environment | Out-Null
} else {
    aws lambda update-function-code `
        --function-name $FunctionName `
        --zip-file fileb://$packagePath | Out-Null
    aws lambda wait function-updated-v2 --function-name $FunctionName
    aws lambda update-function-configuration `
        --function-name $FunctionName `
        --timeout 30 `
        --environment $environment | Out-Null
}

Remove-Item $packageDirectory -Recurse -Force
Write-Host "Lambda consumidora publicada: $FunctionName"
