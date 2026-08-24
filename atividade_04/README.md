# Atividade 4 — Ingestão e ETL com Python + Spark + SQL

Curso de Especialização em Big Data — Escola Politécnica da USP
Ingestão de Dados eEDB-022
Grupo: Camila Faleiros, Fernando Luiz, Guilherme Sergio e Lucca Tomazeli

## Objetivo

Unir três fontes de dados (reclamações de instituições financeiras, cadastro de bancos e avaliações de empregador no Glassdoor) num banco de dados relacional, seguindo o padrão de camadas RAW → Trusted → Delivery, com:

- **Ingestão** feita em Python + PySpark
- **Transformação** feita inteiramente em SQL, via DBT
- **Banco relacional**: PostgreSQL (mesmo usado nas atividades anteriores)

## Decisões técnicas

| Decisão | Escolha |
|---|---|
| Banco relacional | PostgreSQL 16, rodando em Docker (`pg-eedb022-a4`, porta 5433) |
| Ferramenta de ingestão | PySpark (local) |
| Ferramenta de transformação SQL | DBT (dbt-postgres) |
| Formato da camada RAW | Tabelas no Postgres (schema `raw`), sem tratamento |
| Formato das camadas Trusted/Delivery | Parquet (disco local) + tabelas no Postgres (schemas `trusted` e `delivery`) |

## Estrutura do projeto

```
atividade_04/
├── data/
│   ├── trusted/          # Parquet das tabelas tratadas
│   └── delivery/         # Parquet da tabela final
├── eedb022_dbt/
│   ├── dbt_project.yml
│   ├── macros/
│   │   └── generate_schema_name.sql   # garante nome de schema exato (sem concatenar)
│   └── models/
│       ├── trusted_bancos.sql
│       ├── trusted_reclamacoes.sql
│       ├── trusted_empregados.sql
│       └── delivery_final.sql
├── jars/
│   └── postgresql-42.7.4.jar   # driver JDBC usado pelo Spark para escrever no Postgres
└── scripts/
    ├── ingest_raw.py        # ingestão da camada RAW via PySpark
    ├── depara_bcb.py        # de-para de nomes de bancos via API do Bacen
    └── export_parquet.py    # exporta Trusted/Delivery do Postgres para Parquet
```

## Pipeline

```
Dados/ (arquivos originais)
   │
   ▼
[1] ingest_raw.py (PySpark)  ──────────────►  raw.reclamacoes, raw.bancos, raw.empregados
   │
[2] depara_bcb.py (API Bacen) ─────────────►  raw.depara_bcb
   │
   ▼
[3] dbt run (SQL)  ─────────────────────────► trusted.trusted_bancos
                                               trusted.trusted_reclamacoes
                                               trusted.trusted_empregados
                                               delivery.delivery_final
   │
   ▼
[4] export_parquet.py  ─────────────────────► data/trusted/*.parquet
                                               data/delivery/delivery_final.parquet
```

## Camada RAW

Ingestão via PySpark dos três arquivos-fonte, sem qualquer tratamento, escritos direto no Postgres (schema `raw`):

- **Reclamações**: 7 arquivos trimestrais (2021 T1–T4, 2022 T1, T3, T4 — o T2/2022 não tem dados) → **918 linhas**
- **Bancos** (Enquadramento): 1 arquivo TSV → **1474 linhas**
- **Empregados** (Glassdoor): 1 arquivo CSV → **34 linhas**

O Spark precisa do driver JDBC do PostgreSQL (`postgresql-42.7.4.jar`) para conseguir escrever no banco.

## Camada Trusted

Toda a limpeza foi feita em SQL, através de models do DBT.

**`trusted_bancos`**
Padronizei os CNPJs para 8 dígitos completos, recuperando os zeros à esquerda que se perderam por estarem armazenados como número. Removi registros com CNPJ inválido (placeholder zero) e eliminei linhas duplicadas.

**`trusted_reclamacoes`**
Removi os registros sem CNPJ próprio (linhas de conglomerados que não têm identificação individual), padronizei os CNPJs para 8 dígitos completos, excluí colunas irrelevantes ou corrompidas geradas na ingestão, e eliminei linhas duplicadas.

**`trusted_empregados`**
Normalizei os nomes dos bancos (removendo espaços e padronizando em maiúsculo) para garantir compatibilidade no cruzamento com as demais fontes, removi registros sem nome de banco preenchido, e consolidei bancos com mais de uma avaliação no Glassdoor usando a média das notas (`GROUP BY` + `AVG`), eliminando duplicatas de cruzamento.

**Correção de encoding com de-para do Bacen**
O arquivo original de bancos veio com os nomes em encoding corrompido (acentos quebrados), um problema da própria fonte de dados. Resolvi criando o `depara_bcb.py`, que busca o de-para oficial de CNPJ → nome na API pública do Banco Central e carrega em `raw.depara_bcb`. O `trusted_bancos` usa esse de-para (com `COALESCE` para o nome original como plano B, caso algum CNPJ não seja encontrado), mantendo dois nomes separados: um "completo" (oficial, acentuado, para exibição) e um "de busca" (nome popular, usado só para o cruzamento com o Glassdoor, já que o nome oficial do Bacen costuma ser mais formal que o nome usado no Glassdoor).

## Camada Delivery

**`delivery_final`** une as três fontes tratadas por CNPJ e nome padronizados, agrega o total de reclamações por instituição, e trata os bancos sem reclamações registradas para exibir valor zero em vez de vazio (`LEFT JOIN` + `COALESCE`).

## Resultado final

| Tabela | Linhas |
|---|---|
| `trusted_bancos` | 1472 |
| `trusted_reclamacoes` | 437 |
| `trusted_empregados` | 32 |
| `delivery_final` | 1472 |
| `delivery_final` com nota do Glassdoor preenchida | 29 de 32 |

## Como reproduzir

```bash
# 1. Subir o Postgres
docker run --name pg-eedb022-a4 -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=eedb022_a4 -p 5433:5432 -d postgres:16

# 2. Criar os schemas
docker exec -it pg-eedb022-a4 psql -U postgres -d eedb022_a4 -c "CREATE SCHEMA raw; CREATE SCHEMA trusted; CREATE SCHEMA delivery;"

# 3. Ingestão RAW
python3 scripts/ingest_raw.py

# 4. De-para de bancos (Bacen)
python3 scripts/depara_bcb.py

# 5. Transformação (Trusted + Delivery)
cd eedb022_dbt
dbt run

# 6. Exportar Parquet
cd ..
python3 scripts/export_parquet.py
```

## Link do GitHub

[inserir link do repositório]
