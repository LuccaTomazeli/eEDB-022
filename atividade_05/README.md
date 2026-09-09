# Atividade 5 — Orquestração, Qualidade e Metadados

Curso de Especialização em Big Data — Escola Politécnica da USP
Ingestão de Dados eEDB-022

**Grupo:** Camila Faleiros, Fernando Luiz, Guilherme Sergio e Lucca Tomazeli

## 1. Objetivo

A Atividade 5 tem como objetivo integrar e orquestrar os processos desenvolvidos na Atividade 04, utilizando ferramentas voltadas para:

- Orquestração de pipelines: **Apache Airflow**
- Transformação de dados: **dbt**
- Qualidade de dados: **Great Expectations**
- Banco de dados: **PostgreSQL**
- Catálogo e metadados: **DataHub**
- Persistência/entrega dos dados: **Parquet**

A solução foi construída utilizando containers Docker, permitindo reproduzir o ambiente de execução localmente.

---

## 2. Arquitetura da solução

```
   AIRFLOW
                            │
                            ▼
                     ┌─────────────┐
                     │ ingest_raw  │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │  PostgreSQL │
                     │     RAW     │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │ depara_bcb  │
                     └──────┬──────┘
                            │
                            ▼
                     ┌─────────────┐
                     │     dbt     │
                     └──────┬──────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
        trusted_bancos  trusted_     trusted_
                       empregados   reclamacoes
              │             │             │
              └─────────────┼─────────────┘
                            │
                            ▼
                    delivery_final
                            │
                            ▼
                  Great Expectations
                            │
                            ▼
                     Quality Check
                            │
                            ▼
                       Parquet
                            │
                            ▼
                        DataHub

```

## 3. Tecnologias utilizadas

| Tecnologia         | Finalidade                                     |
| ------------------ | ---------------------------------------------- |
| Docker             | Containerização do ambiente                    |
| Docker Compose     | Orquestração dos containers                    |
| Apache Airflow     | Orquestração do pipeline                       |
| PostgreSQL         | Armazenamento dos dados                        |
| Python             | Scripts de ingestão, transformação e validação |
| dbt                | Transformação e modelagem                      |
| Great Expectations | Validação da qualidade dos dados               |
| DataHub            | Catálogo e gerenciamento de metadados          |
| Parquet            | Formato de armazenamento dos dados finais      |
| Git/GitHub         | Versionamento do projeto                       |



## 4. Estrutura do projeto

A estrutura principal da Atividade 5 é:

```
atividade_05/
│
├── dags/
│   ├── atividade_05_teste.py
│   └── atividade_05_pipeline.py
│
├── scripts/
│   ├── ingest_raw.py
│   ├── depara_bcb.py
│   ├── quality_check.py
│   └── export_parquet.py
│
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── datahub_dbt.yml
│   │
│   ├── models/
│   │   ├── trusted_bancos.sql
│   │   ├── trusted_empregados.sql
│   │   ├── trusted_reclamacoes.sql
│   │   └── delivery_final.sql
│   │
│   └── target/
│       ├── manifest.json
│       └── run_results.json
│
├── data/
│   ├── input/
│   ├── trusted/
│   └── delivery/
│
├── jars/
│   └── postgresql-42.7.4.jar
│
├── Dockerfile
├── docker-compose.yml
└── README.md

```

## 5. Banco de dados

Foi utilizado um PostgreSQL dedicado ao pipeline da Atividade 5.

Banco:

eedb022_a5

Schemas:

raw
trusted
delivery

O fluxo de dados é:

```text
raw
 │
 ▼
trusted
 │
 ▼
delivery
```

As principais tabelas/modelos são:

Trusted
trusted.trusted_bancos
trusted.trusted_empregados
trusted.trusted_reclamacoes
Delivery
delivery.delivery_final


Estrutura das camadas

### 5.1 Raw

Dados carregados das fontes com mínima transformação.

Principais tabelas:

- `raw.bancos`
- `raw.empregados`
- `raw.reclamacoes`
- `raw.depara_bcb`

### 5.2 Trusted

Dados tratados e preparados para consumo.

Principais tabelas:

- `trusted.trusted_bancos`
- `trusted.trusted_empregados`
- `trusted.trusted_reclamacoes`

### 5.3 Delivery

Camada final consolidada para análise:

- `delivery.delivery_final`

## 6. DAG principal

O pipeline principal é o **`pipeline_atividade_05`**, executado no Airflow com o seguinte fluxo:

```text
ingest_raw
    ↓
depara_bcb
    ↓
dbt_run
    ↓
quality_check
    ↓
export_parquet
```

## 7. Descrição das etapas

**ingest_raw:** realiza a ingestão dos arquivos para a camada `raw`.

**depara_bcb:** aplica o relacionamento/de-para necessário aos dados do Banco Central.

**dbt_run:** executa os modelos de transformação do projeto dbt.

**quality_check:** executa as validações de qualidade dos dados.

**export_parquet:** exporta os dados finais para o formato Parquet.

## 8. DBT

O projeto dbt está organizado nos seguintes modelos:

```text
models/
├── delivery_final.sql
├── trusted_bancos.sql
├── trusted_empregados.sql
└── trusted_reclamacoes.sql
```

Os modelos principais são materializados como tabelas no PostgreSQL.

O `delivery_final` consolida informações das tabelas trusted e representa a camada final de consumo.

## 9. Qualidade de dados

O pipeline utiliza **Great Expectations** para validar os dados antes da exportação final.

Entre os controles aplicados estão validações de estrutura, preenchimento e consistência dos dados utilizados pelo pipeline.

## 10. Exportação Parquet

Após a execução das validações, os dados da camada final são exportados para arquivos **Parquet**, permitindo armazenamento em formato colunar e adequado para uso analítico.

## 11. DataHub

O **DataHub 1.7.0** foi utilizado para catalogação dos ativos e registro dos relacionamentos entre os conjuntos de dados.

Foi realizada a ingestão dos metadados do projeto dbt a partir de:

```text
/dbt/target/manifest.json
/dbt/target/run_results.json
```

A configuração utilizada está no arquivo:

```text
atividade_05/dbt/datahub_dbt.yml
```

O catálogo contém os modelos dbt e seus relacionamentos de lineage.

## 12. Lineage principal

O relacionamento principal da atividade é:

```text
trusted_bancos
        \
         \
trusted_empregados ---> delivery_final
         /
        /
trusted_reclamacoes
```

Ou, de forma simplificada:

```text
PostgreSQL Trusted
   ├── trusted_bancos
   ├── trusted_empregados
   └── trusted_reclamacoes
            |
            v
      dbt.delivery_final
```

Também foi registrada a lineage física entre os datasets PostgreSQL correspondentes.

## 13. Acessos locais

### DataHub

```text
http://localhost:9002
```

### Airflow

```text
http://localhost:8080
```


## 14. Reprodução

```bash
# 1. Verificar Versão Docker e Docker Compose
docker --version
docker compose version

# 2. Baixar imagem do Airflow
pull apache/airflow:3.3.1

# 3. Configurar arquivo docker-compose.yml
docker compose config

# 4. Subir o Airflow
docker compose up -d
docker compose ps

# 5. Verificar os Logs (Airflow)
docker compose logs airflow-init
docker compose logs airflow-apiserver
docker compose logs airflow-scheduler

# 6. Abrir o Airflow
http://localhost:8080/auth/login

# 7. Criar DAG Teste
atividade_05_teste (Acionar)

# 8. Configurar Postgres no (docker-compose)
docker compose up -d pipeline-postgres

# 9. Preparar Banco de Dados
docker compose exec pipeline-postgres psql -U postgres -d eedb022_a5 -c "CREATE SCHEMA IF NOT EXISTS raw; CREATE SCHEMA IF NOT EXISTS trusted; CREATE SCHEMA IF NOT EXISTS delivery;"
docker compose exec pipeline-postgres psql -U postgres -d eedb022_a5 -c "\dn"

# 10. Trazer os Scripts da Atividade 4
Invoke-WebRequest `
  -Uri "https://github.com/LuccaTomazeli/eEDB-022/archive/refs/heads/main.zip" `
  -OutFile ".\_atividade_04_temp\eEDB-022-main.zip"

Expand-Archive `
  -Path ".\_atividade_04_temp\eEDB-022-main.zip" `
  -DestinationPath ".\_atividade_04_temp\extraido" `
  -Force

# 11. Copiar os Scripts (Atividade 4)
Copy-Item `
  ".\_atividade_04_temp\extraido\eEDB-022-main\atividade_04\scripts\*.py" `
  ".\scripts\" `
  -Force

# 12. Copiar o Projeto DBT
Copy-Item `
  ".\_atividade_04_temp\extraido\eEDB-022-main\atividade_04\eedb022_dbt\*" `
  ".\dbt\" `
  -Recurse `
  -Force`

# 13. Adaptar conteúdo em 'scripts\ingest_raw.py'
De >> localhost:5433/eedb022_a4
Para >> pipeline-postgres:5432/eedb022_a5  

# 14. Criar pasta 'data\input' e três subpastas
New-Item -ItemType Directory -Force .\data\input
New-Item -ItemType Directory -Force .\data\input\Bancos
New-Item -ItemType Directory -Force .\data\input\Empregados
New-Item -ItemType Directory -Force .\data\input\Reclamacoes

# 15. Copiar os dados originais
- BANCOS
Copy-Item `
  "C:\Users\ferna\Documents\Github\eEDB-022\Dados\Bancos\*" `
  ".\data\input\Bancos\" `
  -Force

- EMPREGADOS
Copy-Item `
  "C:\Users\ferna\Documents\Github\eEDB-022\Dados\Empregados\*" `
  ".\data\input\Empregados\" `
  -Force

- FUNCIONARIOS
Copy-Item `
  "C:\Users\ferna\Documents\Github\eEDB-022\Dados\Reclamacoes\*" `
  ".\data\input\Reclamacoes\" `
  -Force

Get-ChildItem .\data\input -Recurse


# 16. Copiar o driver JDBC
New-Item -ItemType Directory -Force .\jars

Copy-Item `
  ".\_atividade_04_temp\extraido\eEDB-022-main\atividade_04\jars\postgresql-42.7.4.jar" `
  ".\jars\" `
  -Force

Get-ChildItem .\jars

# 17. Atualizar o docker-compose alterando o 'airflow-scheduler'
- ./data:/opt/atividade_05/data
- ./scripts:/opt/atividade_05/scripts
- ./dbt:/opt/atividade_05/dbt
- ./jars:/opt/atividade_05/jars

# 18. Criar arquivo 'Dockerfile'
-- atividade_05/Dockerfile

# 19. Verficar versões: Java, PySpark, DBT e Great Expectations
docker compose exec airflow-scheduler java -version
docker compose exec airflow-scheduler python -c "import pyspark; print('PySpark:', pyspark.__version__)"
docker compose exec airflow-scheduler dbt --version
docker compose exec airflow-scheduler python -c "import great_expectations as gx; print('Great Expectations:', gx.__version__)"

# 20. Adaptar conteúdo em 'scripts\depara_bcb.py'
host = pipeline-postgres
port = 5432
database = eedb022_a5

# 21. Adaptar conteúdo em 'scripts\export_parquet.py'
trusted.trusted_bancos
trusted.trusted_reclamacoes
trusted.trusted_empregados

delivery.delivery_final

# 22. Criar o 'dbt\profiles.yml'
eedb022_dbt:
  target: dev

  outputs:
    dev:
      type: postgres
      host: pipeline-postgres
      user: postgres
      password: postgres
      port: 5432
      dbname: eedb022_a5
      schema: trusted
      threads: 4

# 23. Criar o 'dbt\dbt_project.yml'
name: 'eedb022_dbt'

version: '1.0.0'

profile: 'eedb022_dbt'

model-paths:
  - models

macro-paths:
  - macros

models:
  eedb022_dbt:
    +materialized: table

# 24. Executar o 'scripts\ingest_raw.py'
python ingest_raw.py

# 25. Consultar tabelas criadas e registros no Postgres
SELECT
    schemaname,
    tablename
FROM pg_tables
WHERE schemaname = 'raw'
ORDER BY tablename;

# 26. Executar o 'scripts\depara_bcb.py'
python depara_bcb.py


# 27. Executar o DBT profiles dir
cd /opt/atividade_05/dbt
dbt run --profiles-dir .

# 28. Exportar para Parquet 'scripts\export_parquet.py'
python export_parquet.py

# 29. Criar/Executar Validação do Great Expectations
cd /opt/atividade_05/scripts
python quality_check.py

# 30. Criar/Construir DAG 'atividade_05_pipeline.py'
atividade_05/dags/atividade_05_pipeline.py

# 31. Disparar o Pipeline pelo Airflow (Orquestrador)
http://localhost:8080/dags/pipeline_atividade_05/tasks

# 32. Realizar Download/Instalação e QuickStart do DataHub
pip install acryl-datahub
datahub docker quickstart
docker system df

# 33. Acessar o DataHub
http://localhost:9002/

# 34. Cadastrar Fonte de Dados no DataHub
Menu >> Criar Fonte >> Postgres

# 35. Configuração da Fonte de Dados (Host Docker - Base Postgres)
Host:       host.docker.internal
Port:       5433 (no Windows)
Database:   eedb022_a5
Username:   postgres
Password:   postgres

# 36. Testar conexão pelo DataHub
Opção >> Testar Conexão

# 37. DataHub - Definir nome da fonte de dados
PostgreSQL - eEDB-022 - Atividade 5

# 38. DataHub - Executar o shedule
Executar

# 39. DataHub - Verificar Tabelas Catalogadas
Pesquisar:
- trusted_bancos
- trusted_empregados
- trusted_reclamacoes
- delivery_final

# 40. Baixar e Extrair Camadas da Imagem de Ingestão
docker pull acryldata/datahub-ingestion:v1.7.0

# 41. Criar Arquivo de Configuração 'dbt/datahub_dbt.yml'
dbt\datahub_dbt.yml

# 42. Testar Arquivo de Ingestão
docker run --rm `
  -v "C:\Users\ferna\Documents\Github\eEDB-022\atividade_05\dbt:/dbt" `
  acryldata/datahub-ingestion:v1.7.0 `
  ingest run -c /dbt/datahub_dbt.yml --dry-run`

# 43. Executar Ingestão (relacionamentos) para DataHub
docker run --rm `
  -v "${PWD}\dbt:/dbt" `
  acryldata/datahub-ingestion:v1.7.0 `
  ingest -c /dbt/datahub_dbt.yml`

# 44. DataHub - Validar Lineage de 'trusted_bancos'


```

## 15. Evidências

Todas as evidências apresentandas no item anterior estão no diretório: `atividade_05\prints`


## 16. Validações realizadas

Foi validado que:

- O PostgreSQL está disponível para o pipeline.
- O projeto dbt possui conexão válida com o banco.
- Os modelos dbt são executados sobre a camada trusted.
- Os metadados dbt são enviados ao DataHub.
- A lineage entre `trusted_*` e `delivery_final` foi registrada no DataHub.
- Os datasets PostgreSQL estão presentes no catálogo do DataHub.

## 17. Problemas/Dificuldades Enfrentadas

Durante a implementação foram encontrados alguns problemas de ambiente e integração:

- **DataHub e OpenSearch**

O DataHub apresentou instabilidade durante a recuperação do serviço de OpenSearch, incluindo períodos em que os índices ficaram indisponíveis ou em recuperação. Após a inicialização do OpenSearch, os índices voltaram a ser processados.

- **Índices do DataHub**

Foi identificado que os metadados dos modelos dbt permaneciam armazenados no GMS, mas alguns datasets dbt não estavam sendo retornados pelo índice de busca do OpenSearch. Isso dificultou a visualização dos ativos pela interface web.

- **Interface do DataHub**

Em alguns momentos a interface do DataHub (`localhost:9002`) apresentou carregamento lento, associado à alta utilização de CPU dos serviços, principalmente do Kafka, durante as atividades de recuperação e ingestão.

- **Airflow 3.3.1**

Houve dificuldade inicial para gerenciamento do usuário devido à utilização do `SimpleAuthManager`. A configuração encontrada indicava:

```text
admin:admin
```

como usuário configurado, enquanto a senha era gerada e armazenada pelo próprio mecanismo de autenticação.

- **Comandos de ingestão DataHub**

Na tentativa de executar uma nova ingestão, foi necessário corrigir o diretório utilizado no volume Docker. O erro ocorreu porque o arquivo `datahub_dbt.yml` não estava disponível no caminho `/dbt` dentro do container.

- **Instabilidade de recursos**

Durante o laboratório, alguns serviços Docker apresentaram consumo elevado de CPU, principalmente o Kafka. Foi necessário monitorar os containers com `docker stats` e `docker ps` para identificar os serviços responsáveis pela lentidão.

## 18. Conclusão

A atividade 5 implementou um pipeline completo de engenharia de dados, integrando ingestão, tratamento, transformação, validação, exportação e catalogação.

O pipeline principal foi estruturado da seguinte forma:

```text
Ingestão
   ↓
RAW
   ↓
De/Para
   ↓
Trusted
   ↓
Delivery
   ↓
Quality Check
   ↓
Parquet
   ↓
DataHub
```

O fluxo utiliza Airflow para orquestração, PostgreSQL para persistência, dbt para transformação, Great Expectations para qualidade, Parquet para exportação e DataHub para catálogo e lineage, atendendo aos objetivos propostos para o laboratório.
