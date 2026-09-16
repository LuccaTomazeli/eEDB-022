# Ingestao AWS: S3 -> Lambda -> SQS -> Lambda -> SQL

Projeto academico de ingestao de registros JSON usando AWS S3, AWS Lambda, AWS SQS, IAM e CloudWatch.

python scripts/query_database.py --limit 5

## Arquitetura

```text
Arquivos JSON no S3
        |
        v
Lambda Python
        |
        v
      Fila SQS
        |
        v
      Lambda consumidora
        |
        v
      Banco RDS MySQL (AWS)
        |
        v
        S3
```

A Lambda le uma lista de registros JSON no S3 e envia cada registro como uma mensagem individual para a fila SQS.
Ela tambem aceita eventos de criacao de objetos no S3. O trigger automatico deste projeto observa somente o prefixo `entrada/`.
    A Lambda consumidora e acionada pela fila SQS, grava cada registro nas tabelas `bancos`, `empregados` ou `reclamacoes` e salva o resultado no mesmo bucket S3, no prefixo `processados/`.

## Recursos utilizados

| Recurso | Valor |
| --- | --- |
| Regiao | `us-east-1` |
| Bucket S3 | `atividade-6-1-115651887176` |
| Objetos de entrada | `entrada/{bancos,empregados,reclamacoes}/*.json` |
| Objetos processados | `processados/{tabela}/{id}/{messageId}.json` |
| Prefixo automatico | `entrada/` |
| Fila SQS | `atividade-6-1-fila` |
| Lambda | `atividade-6-1-ingestao` |
| Lambda consumidora | `atividade-6-1-consumidor-sql` |
| Role Lambda | `LabRole` |
| Grupo de logs | `/aws/lambda/atividade-6-1-ingestao` |

## Pre-requisitos

- Terraform 1.5 ou superior
- Python 3.12 ou superior
- AWS CLI ou credenciais AWS configuradas
- Conta AWS com acesso a S3, SQS e Lambda
- Docker opcional para dependencias nativas

O projeto usa credenciais temporarias armazenadas localmente em `.aws/credentials`. Esse arquivo nao deve ser versionado nem compartilhado.

## Preparar o terminal

Na pasta raiz do projeto, em Windows, Linux ou macOS:

Crie e ative um ambiente virtual Python conforme o procedimento do seu sistema operacional, instale `lambda_consumer/requirements.txt` e configure as credenciais AWS normalmente. A regiao principal e informada em `terraform/terraform.tfvars`.

O ultimo comando deve retornar o Account ID e a identidade AWS atual.

## Estrutura

```text
atividade_6_1/
|-- Dados/
|   |-- Bancos/
|   |-- Empregados/
|   `-- Reclamacoes/
|-- dados_json/ (gerado pelo conversor)
|-- terraform/
|   |-- versions.tf
|   |-- variables.tf
|   |-- data.tf
|   |-- s3.tf
|   |-- sqs.tf
|   |-- lambda.tf
|   |-- outputs.tf
|   `-- terraform.tfvars.example
|-- iam/ (policies de referencia)
|   |-- lambda-permissions-policy.json
|   `-- lambda-trust-policy.json
|-- lambda/
|   |-- lambda_function.py
|   `-- requirements.txt
|-- lambda_consumer/
|   |-- lambda_function.py
|   `-- requirements.txt
|-- sql/schema.sql
|-- scripts/
|   |-- convert-data.py
|   |-- package_lambdas.py
|   |-- upload_data.py
|   |-- receive_sqs.py
|   |-- initialize_database.py
|   |-- enrich_database.py
|   `-- query_database.py
|-- .gitignore
`-- README.md
```

Os arquivos de `build/`, o estado do Terraform e os arquivos temporarios locais estao no `.gitignore`.

## Execucao inicial

### Fluxo automatico completo

Para preparar a infraestrutura, empacotar as Lambdas e configurar S3/SQS:

Copie `terraform/terraform.tfvars.example` para `terraform/terraform.tfvars`.

```bash
python scripts/package_lambdas.py
terraform -chdir=terraform init
terraform -chdir=terraform apply
```

Edite `terraform/terraform.tfvars` antes do `apply`. Informe especialmente as subnets privadas, o security group da Lambda e as credenciais do RDS. A `LabRole` do laboratorio e usada por padrao; em outra conta, informe uma `lambda_role_arn` propria.

Depois disso, cada novo JSON enviado para `entrada/` percorre automaticamente S3 -> Lambda -> SQS -> RDS MySQL -> tabela `dados_enriquecidos` -> S3. A tabela final e publicada em `enriquecidos/dados_enriquecidos.json`.

A fila SQS e os triggers sao recursos de infraestrutura gerenciados pelo Terraform; os uploads seguintes nao recriam esses recursos.

Se aparecer `voc-cancel-cred`, as credenciais temporarias do laboratorio foram revogadas ou a role atual recebeu um bloqueio explicito. Nesse caso, gere/renove as credenciais no laboratorio e execute o `terraform apply` novamente. O bloqueio nao pode ser removido usando a mesma identidade.

### 1. Converter os dados para JSON

Os arquivos originais em `Dados/` sao preservados. O conversor detecta CSV separado por `;` ou `|`, TSV e as codificacoes UTF-8, CP1252 e Latin-1. Cada registro recebe `tabela_origem`, `arquivo_origem`, `linha_origem` e `dados`.

```bash
python scripts/convert-data.py
```

O comando gera 2.114 registros em `dados_json/`, organizados nas tabelas `bancos`, `empregados` e `reclamacoes`.

### 2. Criar o bucket e enviar os JSON

```bash
python scripts/upload_data.py
```

O Terraform cria o bucket e o script envia os arquivos convertidos para:

```text
s3://atividade-6-1-115651887176/entrada/{bancos,empregados,reclamacoes}/*.json
```

O upload deve ser feito depois de configurar a Lambda e o trigger para que cada objeto dispare a ingestao.

### 3. Testar a fila

```bash
python scripts/receive_sqs.py
```

O Terraform cria a fila e o output `queue_url` fornece sua URL para os comandos Python.

### 4. IAM

Neste ambiente de laboratorio, `iam:CreateRole` foi bloqueado. Por isso, o Terraform usa a Role pre-criada `LabRole`. Em ambiente profissional, informe uma role propria em `lambda_role_arn`.

Em um ambiente profissional, crie uma Role propria com:

- `s3:GetObject` para o objeto de entrada
- `sqs:SendMessage` para a fila
- `sqs:ReceiveMessage`, `sqs:DeleteMessage` e `sqs:GetQueueAttributes` para a Lambda consumidora
- permissoes basicas de logs do CloudWatch

O RDS MySQL fica em uma VPC AWS e a Lambda consumidora usa o mesmo security group. O schema e criado automaticamente pela Lambda na primeira mensagem.

### Acesso ao banco pela interface

O RDS existente nao deve ser criado novamente pelo Console. A acao `rds:CreateDBInstance` esta bloqueada pela policy do laboratorio. O banco existente e privado e pode ser acessado pelo Cloud9 da mesma VPC, usando:

```bash
mysql -h atividade-6-1-mysql-aws.cpllji7cpbrb.us-east-1.rds.amazonaws.com \
  -P 3306 -u admin -p atividade
```

Nao crie um novo ambiente Cloud9: a role do laboratorio nao possui `cloud9:CreateEnvironmentEC2`, `cloud9:ListEnvironments` e `cloud9:DescribeEnvironmentMemberships`. Um administrador precisa liberar `cloud9:DescribeEnvironmentMemberships`, `cloud9:DescribeEnvironments` e `cloud9:ListEnvironments` para que o ambiente existente apareca no Console. O ambiente existente e `aws-cloud9-mycloud9-2ec1be7897bd46c996f6a0b3f7b4ee85`; abra o terminal dele no Console. O security group desse ambiente ja foi autorizado somente para TCP 3306 no RDS.

O AWS CloudShell e o AWS Toolkit no IDE sao alternativas para comandos AWS, mas nao acessam diretamente este RDS privado porque rodam fora da VPC. Para consultar o banco, use o terminal do Cloud9 existente ou um host/tunel dentro da VPC.

As policies de referencia estao em `iam/`.

Se o Console S3 mostrar a mensagem sobre `s3express:ListAllMyDirectoryBuckets`, um administrador deve adicionar essa acao a uma policy anexada a role/identidade usada no Console. Ela ja esta incluida na policy de referencia `iam/lambda-permissions-policy.json`, mas editar esse arquivo local nao altera automaticamente a role AWS `voclabs`. Depois da alteracao no IAM, atualize a pagina do S3.

### 5. Empacotamento e publicacao

```bash
python scripts/package_lambdas.py
terraform -chdir=terraform apply
```

O empacotador Python:

1. Instala as dependencias da Lambda consumidora em formato compativel com Linux.
2. Gera o pacote em `build/consumer-lambda.zip`.
3. O Terraform cria ou atualiza as duas Lambdas e suas variaveis.

O boto3 ja e fornecido pelo runtime Python da AWS Lambda, portanto nao e necessario instala-lo no pacote atual.

O trigger S3 e o mapeamento SQS da Lambda consumidora sao recursos declarados em Terraform.

## Teste manual da Lambda

```bash
aws --no-cli-pager lambda invoke \
  --function-name atividade-6-1-ingestao \
  --payload '{}' \
  --cli-binary-format raw-in-base64-out \
  lambda-response.json
cat lambda-response.json
```

Resultado esperado:

```json
{
  "statusCode": 200,
  "recordsSent": 3,
  "body": "3 registros enviados para SQS"
}
```

Depois, leia as mensagens:

```bash
python scripts/receive_sqs.py
```

## Teste automatico S3 -> Lambda -> SQS

Para repetir somente o upload dos dados convertidos:

```bash
python scripts/upload_data.py
```

O upload dispara a Lambda automaticamente. Para verificar as mensagens:

```bash
python scripts/receive_sqs.py
```

Cada registro do JSON aparece como uma mensagem separada na fila.

### 7. Configurar o RDS MySQL e o consumidor

O RDS MySQL e criado na VPC AWS como `atividade-6-1-mysql-aws`. As tabelas `bancos`, `empregados`, `reclamacoes` e `dados_enriquecidos` sao criadas automaticamente pela Lambda consumidora:

O Terraform publica a Lambda consumidora e conecta a fila por meio de `aws_lambda_event_source_mapping`.

### 8. Tratar, enriquecer e salvar no S3

Depois que os registros estiverem nas tabelas brutas, execute:

```bash
python scripts/enrich_database.py
```

O processo cria ou atualiza a tabela MySQL `dados_enriquecidos`. Ele normaliza nomes e CNPJs, converte metricas numericas, soma reclamacoes e relaciona os registros correspondentes de empregados e reclamacoes. O resultado completo e salvo em:

```text
s3://atividade-6-1-481958198557/enriquecidos/dados_enriquecidos.json
```

Para escolher outro caminho no S3:

```bash
S3_ENRICHED_KEY="enriquecidos/versao-2.json" python scripts/enrich_database.py
```

Para cada mensagem dos novos arquivos, a Lambda insere o registro bruto em sua tabela de origem, combina a mensagem com o registro persistido e salva o JSON enriquecido no bucket configurado por `S3_BUCKET`. O prefixo pode ser alterado por `S3_OUTPUT_PREFIX` e usa `processados` por padrao.

O objeto gerado tem esta estrutura:

```json
{
  "mensagem_original": {
    "tabela_origem": "bancos",
    "arquivo_origem": "EnquadramentoInicia_v2.tsv",
    "linha_origem": 2,
    "dados": { "Segmento": "S1", "CNPJ": "0", "Nome": "BANCO DO BRASIL - PRUDENCIAL" }
  },
  "registro_inserido": { "id": 1, "arquivo_origem": "EnquadramentoInicia_v2.tsv" },
  "processamento": {
    "message_id": "...",
    "processado_em": "2026-09-14T12:00:00+00:00",
    "status": "persistido"
  }
}
```

Mensagens invalidas sao devolvidas em `batchItemFailures` para retry; uma falha de conexao, consulta SQL ou escrita no S3 faz o lote inteiro falhar.

## CloudWatch Logs

O grupo de logs e criado automaticamente pela Lambda:

```text
/aws/lambda/atividade-6-1-ingestao
```

Os logs do consumidor ficam em `/aws/lambda/atividade-6-1-consumidor-sql`.

Para verificar pelo AWS CLI:

```bash
aws --no-cli-pager logs describe-log-groups \
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

```bash
aws sts get-caller-identity
```

### NoRegion

Use a regiao informada em `terraform.tfvars` ou na configuracao padrao da AWS CLI.

### AccessDenied em IAM

A identidade usada precisa poder criar ou reutilizar a Role. Em laboratorios AWS, use a Role fornecida, como `LabRole`, ou solicite ao administrador uma Role propria para Lambda.

### ResourceConflictException na Lambda

Uma atualizacao ainda esta em andamento. Aguarde a funcao ficar `Active` e execute novamente:

```bash
aws --no-cli-pager lambda get-function-configuration \
  --function-name atividade-6-1-ingestao \
  --query '{State:State,LastUpdateStatus:LastUpdateStatus}'
```

O Terraform aguarda o estado consistente dos recursos antes de concluir o `apply`.

### Nenhuma mensagem na SQS

Verifique se:

- O upload foi feito no prefixo `entrada/`.
- A Lambda esta `Active`.
- A fila `atividade-6-1-fila` existe e esta na regiao configurada.
- A mensagem nao foi removida por um teste anterior.

## Limpeza dos recursos

Execute somente quando nao precisar mais da demonstracao:

```bash
terraform -chdir=terraform destroy
```

A exclusao da Lambda e dos demais recursos pode ser impedida pelas politicas do laboratorio.