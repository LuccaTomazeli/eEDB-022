# Atividade 06 - Ingestao em AWS

A ingestao segue o desenho proposto:

```text
S3 (origem) -> Lambda produtora -> SQS -> Lambda consumidora -> RDS -> S3 (destino)
```

## Componentes

- `lambda_s3_para_sqs.py`: acionada por `ObjectCreated` no bucket de origem. Lê os metadados do objeto e publica na SQS apenas `bucket` e `key`. O conteúdo não é duplicado na mensagem, evitando o limite de 256 KiB da SQS.
- `lambda_consumidor.py`: acionada pela SQS. Busca o objeto no S3, insere o payload na tabela `ingestao_raw` via RDS Data API e grava uma cópia processada no bucket de destino.
- `template.yaml`: infraestrutura AWS SAM com dois buckets S3, SQS principal, DLQ, duas Lambdas, permissões IAM e integrações de eventos.
- `schema_rds.sql`: tabela usada pela Lambda consumidora.

O texto do enunciado chama de “consumidor” a Lambda que busca no S3 e envia para a fila. Esse comportamento está implementado em `lambda_s3_para_sqs.py`, que é a produtora no desenho; o consumidor da fila é `lambda_consumidor.py`.

## Pré-requisitos

- AWS CLI configurada.
- AWS SAM CLI instalado.
- Aurora compatível com RDS Data API e um segredo no AWS Secrets Manager.
- A tabela do `schema_rds.sql` criada no banco informado em `RdsDatabase`.

## Teste local de sintaxe

```powershell
python -m py_compile lambda_s3_para_sqs.py lambda_consumidor.py
```

## Deploy

```powershell
sam build --template-file template.yaml
sam deploy --guided --template-file .aws-sam/build/template.yaml
```

Informe os valores de `RdsClusterArn`, `RdsSecretArn` e `RdsDatabase` durante o deploy. Depois, envie um arquivo para o bucket retornado em `OrigemBucket`:

```powershell
aws s3 cp .\arquivo.csv s3://<OrigemBucket>/raw/arquivo.csv
aws sqs get-queue-attributes --queue-url <IngestaoQueueUrl> --attribute-names ApproximateNumberOfMessages
```

A SQS tem uma DLQ com três tentativas. Uma falha no RDS ou no acesso ao S3 faz a mensagem retornar para a fila e, após as tentativas, ser encaminhada para a DLQ.
