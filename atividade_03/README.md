# Atividade 03 - Pipeline de Ingestao de Dados com PySpark e PostgreSQL

Pipeline ELT/ETL containerizada para ingestao, tratamento, integracao e carga das bases de dados de Bancos, Empregados (Glassdoor) e Reclamacoes (BACEN) organizadas nos schemas `raw`, `trusted` e `delivery` do PostgreSQL.

---

## Execucao

### Prerequisitos
- Docker Engine e Docker Compose.

### Como Executar

1. Navegue ate a pasta do Docker:
```bash
cd eEDB-022/atividade_03/docker
```

2. Suba o banco de dados e execute a pipeline:
```bash
docker compose up -d postgres
docker compose run --rm --build pipeline
```

3. (Opcional) Limpeza completa pos-execucao (preservando imagens):
```bash
docker compose down -v
docker container prune -f && docker volume prune -f && docker network prune -f
```

---

## Arquitetura Tecnica e Responsabilidades

### Stack
- **Linguagem**: Python 3.11
- **Processamento Distribuido**: PySpark 3.5.1
- **Banco de Dados**: PostgreSQL 15 (Alpine)
- **Gerenciamento de Pacotes**: `uv` (Astral)
- **Formatos de Saida**: Apache Parquet (single-file via PyArrow/Pandas)

### Schemas e Tabelas no PostgreSQL (`banco_atividade_3`)

1. **Schema `raw`**:
   - `raw.bancos`: Tabela de enquadramento de Bancos bruta.
   - `raw.empregados`: Tabela de avaliacoes do Glassdoor bruta.
   - `raw.reclamacoes`: Tabela de relatorios de reclamacoes do BACEN bruta.
   - `raw.tb_aux_bcb`: Tabela auxiliar de DePara de nomes do BACEN.

2. **Schema `trusted`**:
   - `trusted.bancos`: Cadastro de bancario limpo, com CNPJ formatado e DePara aplicado.
   - `trusted.empregados`: Avaliacoes de empregados sem empresas duplicadas/invalidas.
   - `trusted.reclamacoes`: Reclamacoes sanitizadas e com indice numerico padronizado.

3. **Schema `delivery`**:
   - `delivery.bancos`: Visao consolidada unificando Bancos, Glassdoor e agregacoes de reclamacoes por CNPJ e conglomerado.

### Divisao de Responsabilidades dos Scripts (`atividade_03/scripts/`)

- **`orquestrador.py`**:
  Orquestrador central da pipeline. Instancia a `SparkSession`, gerencia conexoes com o PostgreSQL, cria os schemas (`raw`, `trusted`, `delivery`), salva os arquivos `.parquet` nos volumes e efetua as cargas JDBC/SQLAlchemy no PostgreSQL.

- **`raw.py`**:
  Encarregado unica e exclusivamente de ler e preparar os DataFrames das fontes brutas.

- **`trusted.py`**:
  Encarregado unica e exclusivamente do tratamento, sanitizacao, DePara e geracao dos DataFrames da camada Trusted.

- **`delivery.py`**:
  Encarregado unica e exclusivamente da integracao das bases tratadas e agregacao de metricas da camada Delivery.

---

## Estrutura do Projeto

```text
atividade_03/
├── docker/
│   ├── .env                 <- Parametros do PostgreSQL (DB_NAME, USER, PASS, PORT)
│   ├── Dockerfile           <- Build Python 3.11 + Java JRE + uv
│   ├── docker-compose.yml   <- Servicos postgres e pipeline (command: python scripts/orquestrador.py)
│   └── requirements.txt     <- Dependencias fixadas
├── scripts/
│   ├── orquestrador.py      <- Orquestrador principal da pipeline e conexoes com banco/volumes
│   ├── raw.py               <- Leitura e preparacao das bases brutas
│   ├── trusted.py           <- Tratamento e sanitizacao da camada trusted
│   └── delivery.py          <- Integracao e agregacoes da camada delivery
└── volume/
    ├── raw/
    │   └── tb_aux_bcb.json  <- Tabela auxiliar DePara do BACEN
    ├── trusted/             <- Parquets da camada trusted (.gitignore)
    └── delivery/            <- Parquet final da camada delivery (.gitignore)
```
