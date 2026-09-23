# Atividade 8 - Pipeline Streaming com PySpark e Kafka

Pipeline local: arquivos JSON -> produtor Python -> Kafka -> PySpark Structured Streaming -> PostgreSQL (enriquecimento) -> JSON local.

## Pré-requisitos

- Docker Desktop com Compose
- Python 3.10+ para o produtor e o carregador da tabela
- Java 17 para executar PySpark fora do container

## Execução recomendada

No PowerShell, a partir deste diretório:

```powershell
docker compose up -d zookeeper kafka postgres spark-master spark-worker
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python load_lookup.py
docker compose exec kafka kafka-topics --create --if-not-exists --topic dados-brutos --bootstrap-server kafka:29092 --partitions 1 --replication-factor 1
docker compose exec spark-master /opt/spark/bin/spark-submit --master spark://spark-master:7077 --jars /opt/atividade8/jars/spark-sql-kafka-0-10_2.12-3.5.3.jar,/opt/atividade8/jars/spark-token-provider-kafka-0-10_2.12-3.5.3.jar,/opt/atividade8/jars/kafka-clients-3.4.1.jar,/opt/atividade8/jars/commons-pool2-2.11.1.jar,/opt/atividade8/jars/postgresql-42.7.4.jar /opt/atividade8/consumer.py
python producer.py --delay 0.01
```

O consumidor fica executando continuamente. Os resultados aparecem em `saida/enriquecido/enriquecido=true` e as mensagens sem correspondência em `enriquecido=false`. Para acompanhar uma carga menor, use `python producer.py --limit 100`.

O banco pode ser consultado com `docker compose exec postgres psql -U atividade8 -d atividade8 -c "SELECT * FROM banco_enquadramento LIMIT 5"`.

O PostgreSQL fica disponivel em `localhost:5432` e a interface do Spark em `http://localhost:8080`.

## Observações técnicas

- O tópico `dados-brutos` é criado automaticamente pelo broker local.
- O `foreachBatch` lê o micro-batch, consulta a tabela PostgreSQL por JDBC e grava JSON particionado.
- A chave de enriquecimento é CNPJ; quando ausente, o consumidor tenta o nome normalizado.
- O checkpoint está em `saida/checkpoint`, permitindo reinício do streaming sem reler mensagens já confirmadas.

## Terraform opcional

O arquivo `terraform/main.tf` demonstra a criação de uma rede Docker e um PostgreSQL isolado. Ele e alternativo ao Compose e usa a porta local `5432`:

```powershell
cd terraform
terraform init
terraform apply
```

Para limpar os serviços do Compose: `docker compose down -v`.

## Fluxograma

O fluxo do projeto esta representado em [docs/fluxograma.svg](docs/fluxograma.svg).