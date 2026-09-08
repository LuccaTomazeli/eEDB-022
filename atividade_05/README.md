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

raw
 │
 ▼
trusted
 │
 ▼
delivery

As principais tabelas/modelos são:

Trusted
trusted.trusted_bancos
trusted.trusted_empregados
trusted.trusted_reclamacoes
Delivery
delivery.delivery_final


## 6. Resultado final

Inserir texto


## 7. Reprodução

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

# 43. Executar Ingestão para DataHub
docker run --rm `
  -v "C:\Users\ferna\Documents\Github\eEDB-022\atividade_05\dbt:/dbt" `
  acryldata/datahub-ingestion:v1.7.0 `
  ingest run -c /dbt/datahub_dbt.yml `

# 44. DataHub - Validar Lineage de 'trusted_bancos'



```
## 8. Evidências



## 9. Conclusão e Considerações

A Atividade 5 implementou um pipeline de dados integrado utilizando Airflow como orquestrador, PostgreSQL como banco de dados, dbt para transformação, Great Expectations para validação da qualidade e DataHub para catalogação e gerenciamento dos metadados.

O pipeline principal foi estruturado da seguinte forma:

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

Foram validadas as principais etapas de execução do ambiente, incluindo:

funcionamento do Docker;
execução do Airflow;
conexão com PostgreSQL;
execução do dbt;
geração do manifesto dbt;
criação dos modelos Trusted;
criação do modelo Delivery;
exportação para Parquet;
catalogação das tabelas no DataHub;
ingestão dos metadados dbt no DataHub.


