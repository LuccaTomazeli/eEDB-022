# Ingestao AWS: S3 -> Lambda -> SQS

Projeto academico de ingestao de registros JSON usando AWS S3, AWS Lambda, AWS SQS, IAM e CloudWatch.

## Arquitetura

```text
Arquivo JSON no S3
        |
        v
Lambda Python
        |
        v
Fila SQS
```

A Lambda le uma lista de registros JSON no S3 e envia cada registro como uma mensagem individual para a fila SQS.
Ela tambem aceita eventos de criacao de objetos no S3. O trigger automatico deste projeto observa somente o prefixo `entrada/`.

## Recursos utilizados

| Recurso | Valor |
| --- | --- |
| Regiao | `us-east-1` |
| Bucket S3 | `atividade-6-1-115651887176` |
| Objeto de teste | `dados/clientes.json` |
| Prefixo automatico | `entrada/` |
| Fila SQS | `atividade-6-1-fila` |
| Lambda | `atividade-6-1-ingestao` |
| Role Lambda | `LabRole` |
| Grupo de logs | `/aws/lambda/atividade-6-1-ingestao` |

## Pre-requisitos

- Windows PowerShell
- Python 3.12 ou superior
- AWS CLI configurado
- Conta AWS com acesso a S3, SQS e Lambda
- VS Code

O projeto usa credenciais temporarias armazenadas localmente em `.aws/credentials`. Esse arquivo nao deve ser versionado nem compartilhado.

## Preparar o terminal

Na pasta raiz do projeto:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

$env:AWS_SHARED_CREDENTIALS_FILE = "$PWD\.aws\credentials"
$env:AWS_DEFAULT_REGION = "us-east-1"

aws sts get-caller-identity
```

O ultimo comando deve retornar o Account ID e a identidade AWS atual.

## Estrutura

```text
atividade_6_1/
|-- data/clientes.json
|-- iam/
|   |-- lambda-permissions-policy.json
|   `-- lambda-trust-policy.json
|-- lambda/
|   |-- lambda_function.py
|   `-- requirements.txt
|-- scripts/
|   |-- create-s3.ps1
|   |-- create-sqs.ps1
|   |-- create-iam.ps1
|   |-- deploy-lambda.ps1
|   |-- configure-s3-trigger.ps1
|   `-- receive-sqs.ps1
|-- .gitignore
`-- README.md
```

Os arquivos `.queue-url`, `.lambda-role-arn`, `lambda.zip` e `lambda-response.json` sao gerados localmente e estao no `.gitignore`.

## Execucao inicial

### 1. Criar o bucket e enviar o JSON

```powershell
.\scripts\create-s3.ps1
```

O script cria ou verifica o bucket e envia `data/clientes.json` para:

```text
s3://atividade-6-1-115651887176/dados/clientes.json
```

### 2. Criar e testar a fila

```powershell
.\scripts\create-sqs.ps1
.\scripts\receive-sqs.ps1
```

O primeiro script salva a URL da fila em `.queue-url`, envia uma mensagem de teste e o segundo script recebe e remove essa mensagem.

### 3. IAM

Em uma conta com permissao para criar Roles, o script seria:

```powershell
.\scripts\create-iam.ps1
```

Neste ambiente de laboratorio, `iam:CreateRole` foi bloqueado. Por isso, a Lambda usa a Role pre-criada `LabRole`, que permite ser assumida pelo servico Lambda.

Em um ambiente profissional, crie uma Role propria com:

- `s3:GetObject` para o objeto de entrada
- `sqs:SendMessage` para a fila
- permissoes basicas de logs do CloudWatch

As policies de referencia estao em `iam/`.

### 4. Publicar a Lambda

```powershell
.\scripts\deploy-lambda.ps1
```

O script:

1. Empacota a pasta `lambda/` em `lambda.zip`.
2. Cria ou atualiza a Lambda `atividade-6-1-ingestao`.
3. Configura as variaveis `S3_BUCKET`, `S3_KEY` e `SQS_QUEUE_URL`.

O boto3 ja e fornecido pelo runtime Python da AWS Lambda, portanto nao e necessario instala-lo no pacote atual.

### 5. Configurar o trigger automatico

```powershell
.\scripts\configure-s3-trigger.ps1
```

O script concede permissao para o S3 invocar a Lambda e configura o evento `s3:ObjectCreated:Put` com prefixo `entrada/`.

## Teste manual da Lambda

```powershell
aws --no-cli-pager lambda invoke `
  --function-name atividade-6-1-ingestao `
  --payload '{}' `
  --cli-binary-format raw-in-base64-out `
  lambda-response.json

Get-Content lambda-response.json
```

Resultado esperado:

```json
{
  "statusCode": 200,
  "recordsSent": 2,
  "body": "2 registros enviados para SQS"
}
```

Depois, leia as mensagens:

```powershell
.\scripts\receive-sqs.ps1
```

## Teste automatico S3 -> Lambda -> SQS

Envie um novo arquivo para o prefixo monitorado:

```powershell
aws s3 cp data\clientes.json `
  s3://atividade-6-1-115651887176/entrada/novo-teste.json
```

O upload dispara a Lambda automaticamente. Para verificar as mensagens:

```powershell
.\scripts\receive-sqs.ps1
```

Cada registro do JSON aparece como uma mensagem separada na fila.

## CloudWatch Logs

O grupo de logs e criado automaticamente pela Lambda:

```text
/aws/lambda/atividade-6-1-ingestao
```

Para verificar pelo AWS CLI:

```powershell
aws --no-cli-pager logs describe-log-groups `
  --log-group-name-prefix /aws/lambda/atividade-6-1-ingestao
```

No Console AWS:

1. Abra **CloudWatch**.
2. Acesse **Logs > Log groups**.
3. Abra `/aws/lambda/atividade-6-1-ingestao`.
4. Selecione o log stream mais recente.

## Erros comuns

### NoCredentials ou Unable to locate credentials

Confirme o caminho das credenciais:

```powershell
$env:AWS_SHARED_CREDENTIALS_FILE = "$PWD\.aws\credentials"
aws sts get-caller-identity
```

### NoRegion

Configure a regiao no terminal:

```powershell
$env:AWS_DEFAULT_REGION = "us-east-1"
```

### AccessDenied em IAM

A identidade usada precisa poder criar ou reutilizar a Role. Em laboratorios AWS, use a Role fornecida, como `LabRole`, ou solicite ao administrador uma Role propria para Lambda.

### ResourceConflictException na Lambda

Uma atualizacao ainda esta em andamento. Aguarde a funcao ficar `Active` e execute novamente:

```powershell
aws --no-cli-pager lambda get-function-configuration `
  --function-name atividade-6-1-ingestao `
  --query '{State:State,LastUpdateStatus:LastUpdateStatus}'
```

O script `deploy-lambda.ps1` ja aguarda a atualizacao do codigo antes de atualizar a configuracao.

### Nenhuma mensagem na SQS

Verifique se:

- O upload foi feito no prefixo `entrada/`.
- A Lambda esta `Active`.
- A URL em `.queue-url` e a fila correta.
- A mensagem nao foi removida por um teste anterior.

## Limpeza dos recursos

Execute somente quando nao precisar mais da demonstracao:

```powershell
$env:AWS_DEFAULT_REGION = "us-east-1"
$bucket = "atividade-6-1-115651887176"
$queueUrl = (Get-Content .queue-url -Raw).Trim()

aws s3 rb "s3://$bucket" --force
aws sqs delete-queue --queue-url $queueUrl
aws lambda delete-function --function-name atividade-6-1-ingestao
```

A exclusao da Lambda e dos demais recursos pode ser impedida pelas politicas do laboratorio.