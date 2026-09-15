param(
    [string]$FunctionName = "atividade-6-1-consumidor-sql",
    [string]$Region = "us-east-1",
    [string]$RoleArn = "",
    [string]$SqlHost = $env:SQL_HOST,
    [string]$SqlPort = "3306",
    [string]$SqlUser = $env:SQL_USER,
    [string]$SqlPassword = $env:SQL_PASSWORD,
    [string]$SqlDatabase = $env:SQL_DATABASE,
    [string]$S3Bucket = $env:S3_BUCKET,
    [string]$S3OutputPrefix = $(if ($env:S3_OUTPUT_PREFIX) { $env:S3_OUTPUT_PREFIX } else { "processados" }),
    [string]$S3EnrichedKey = $(if ($env:S3_ENRICHED_KEY) { $env:S3_ENRICHED_KEY } else { "enriquecidos/dados_enriquecidos.json" })
)

$ErrorActionPreference = "Stop"
$env:AWS_DEFAULT_REGION = $Region

if (-not $env:AWS_SHARED_CREDENTIALS_FILE) {
    $env:AWS_SHARED_CREDENTIALS_FILE = Join-Path $PSScriptRoot "..\.aws\credentials"
}

$accountId = (aws sts get-caller-identity --query Account --output text).Trim()
$RoleArn = if ($RoleArn) { $RoleArn } else { "arn:aws:iam::${accountId}:role/LabRole" }
$S3Bucket = if ($S3Bucket) { $S3Bucket } else { "atividade-6-1-$accountId" }

$envFile = Join-Path $PSScriptRoot "..\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#=]+)\s*=\s*(.*)\s*$') {
            Set-Item -Path "Env:$($matches[1].Trim())" -Value $matches[2].Trim()
        }
    }
}

$S3Bucket = if ($env:S3_BUCKET) { $env:S3_BUCKET } else { $S3Bucket }
$S3OutputPrefix = if ($env:S3_OUTPUT_PREFIX) { $env:S3_OUTPUT_PREFIX } else { $S3OutputPrefix }
$S3EnrichedKey = if ($env:S3_ENRICHED_KEY) { $env:S3_ENRICHED_KEY } else { $S3EnrichedKey }
$SqlHost = if ($env:SQL_HOST) { $env:SQL_HOST } else { $SqlHost }
$SqlUser = if ($env:SQL_USER) { $env:SQL_USER } else { $SqlUser }
$SqlPassword = if ($env:SQL_PASSWORD) { $env:SQL_PASSWORD } else { $SqlPassword }
$SqlDatabase = if ($env:SQL_DATABASE) { $env:SQL_DATABASE } else { $SqlDatabase }

foreach ($value in @{SQL_HOST=$SqlHost; SQL_USER=$SqlUser; SQL_PASSWORD=$SqlPassword; SQL_DATABASE=$SqlDatabase}.GetEnumerator()) {
    if ([string]::IsNullOrWhiteSpace($value.Value)) { throw "Defina a variavel `$env:$($value.Key)." }
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
Copy-Item (Join-Path $lambdaPath "*.py") $packageDirectory
Compress-Archive -Path (Join-Path $packageDirectory "*") -DestinationPath $packagePath

$subnetIds = (aws ec2 describe-subnets --filters Name=vpc-id,Values=vpc-076c6cc7e13016221 Name=state,Values=available --query 'Subnets[].SubnetId' --output text).Trim() -split '\s+'
$environment = "Variables={SQL_HOST=$SqlHost,SQL_PORT=$SqlPort,SQL_USER=$SqlUser,SQL_PASSWORD=$SqlPassword,SQL_DATABASE=$SqlDatabase,S3_BUCKET=$S3Bucket,S3_OUTPUT_PREFIX=$S3OutputPrefix,S3_ENRICHED_KEY=$S3EnrichedKey}"
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
        --vpc-config "SubnetIds=$($subnetIds -join ','),SecurityGroupIds=sg-054d1289b9839ad60" `
        --environment $environment | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel criar a Lambda $FunctionName. Verifique as permissoes AWS."
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
        --timeout 30 `
        --vpc-config "SubnetIds=$($subnetIds -join ','),SecurityGroupIds=sg-054d1289b9839ad60" `
        --environment $environment | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel atualizar a configuracao da Lambda $FunctionName."
    }
}

Remove-Item $packageDirectory -Recurse -Force
Write-Host "Lambda consumidora publicada: $FunctionName"
