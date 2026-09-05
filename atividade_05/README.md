# Atividade 4 — Orquestração, Qualidade e Metadados

Curso de Especialização em Big Data — Escola Politécnica da USP
Ingestão de Dados eEDB-022
Grupo: Camila Faleiros, Fernando Luiz, Guilherme Sergio e Lucca Tomazeli

## Objetivo

Utilizar ferramenta de orquestração dos processos realizados nas últimas 3 atividades. 
Neste laboratórios, vamos utilizar as fontes de dados da atividade 04, seguindo da seguinte forma:

- Orquestração
Airflow

- Qualidade
Great Expectations

- Metadados
DataHub

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

## Decisões técnicas

## Estrutura do projeto

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

## Pipeline

## Resultado final

## Reprodução


## Conclusão e Considerações


