# Atividade 5 — Orquestração, Qualidade e Metadados

Curso de Especialização em Big Data — Escola Politécnica da USP
Ingestão de Dados eEDB-022

Grupo: Camila Faleiros, Fernando Luiz, Guilherme Sergio e Lucca Tomazeli

## Objetivo

Utilizar ferramenta de orquestração dos processos realizados nas últimas 3 atividades. 

Neste laboratório, vamos utilizar as fontes de dados da atividade 04, seguindo da seguinte forma:

- **Orquestração:**  Airflow
- **Qualidade:** Great Expectations
- **Metadados:** DataHub (DBT, PostgreSQL, Docker)

```
                  AIRFLOW
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    ingest_raw.py         depara_bcb.py
          │                     │
          └──────────┬──────────┘
                     ▼
                 PostgreSQL
                     │
                     ▼
                   DBT
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Trusted    Trusted    Trusted
          │          │          │
          └──────────┼──────────┘
                     ▼
                  Delivery
                     │
                     ▼
             GREAT EXPECTATIONS
                     │
                     ▼
                Validação OK?
                  /       \
                SIM       NÃO
                 │         │
                 ▼         ▼
              DATAHUB    STOP
```

## Decisões técnicas

Inserir texto


## Estrutura do projeto

Inserir texto


```
eEDB-022/
│
└── atividade_05/
    │
    ├── airflow/
    │   ├── dags/
    │   │   └── pipeline_atividade_05.py
    │   └── Dockerfile
    │
    ├── great_expectations/
    │   ├── expectations/
    │   └── ...
    │
    ├── datahub/
    │   └── ...
    │
    ├── docker-compose.yml
    ├── README.md
    └── relatorio-atividade-5.pdf
```

## Pipeline

Inserir texto


## Resultado final

Inserir texto


## Reprodução

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



```


## Conclusão e Considerações

Inserir texto



