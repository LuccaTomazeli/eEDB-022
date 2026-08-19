# Atividade 03 - Pipeline de Ingestao de Dados com PySpark e PostgreSQL

**Apresentação - Disciplina de Ingestão de Dados**

Este projeto apresenta uma pipeline ELT/ETL containerizada e distribuida construida com **PySpark 3.5.1** e **PostgreSQL 15**, encarregada de realizar a ingestao, sanitizacao, integracao e carga das bases de dados bancarias, avaliacoes de empregados (Glassdoor) e relatorios de reclamacoes do Banco Central do Brasil (BACEN).

---

## Execução Rápida

### Prerequisitos
- Docker Engine e Docker Compose.

### Como Executar

1. Acesse o diretorio do Docker:
```bash
cd eEDB-022/atividade_03/docker
```

2. Inicialize o banco de dados e execute a pipeline:
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

## 1: DevOps

A arquitetura do projeto foi projetada para garantir **reprodutibilidade**, **paralelismo distribuído** e **execução sem privilégios de root**.

```text
atividade_03/
├── docker/
│   ├── .env                 <- Parametros de conexao do PostgreSQL
│   ├── Dockerfile           <- Build Python 3.11 + Java JRE + uv
│   ├── docker-compose.yml   <- Orquestracao dos servicos postgres e pipeline
│   └── requirements.txt     <- Dependencias python
├── scripts/
│   ├── orquestrador.py      <- Ponto de entrada, conexoes JDBC, schemas e gravacao de volumes
│   ├── raw.py               <- Leitura e preparacao das fontes brutas
│   ├── trusted.py           <- Tratamento, sanitizacao e DePara da camada Trusted
│   └── delivery.py          <- Integracao final e agregacoes da camada Delivery
└── volume/
    ├── raw/                 <- Tabela auxiliar DePara do BACEN
    ├── trusted/             <- Arquivos Parquet da camada Trusted
    └── delivery/            <- Arquivo Parquet final da camada Delivery
```

### Docker

- **Mapeamento Dinamico de Permissoes do Host (`user: "${UID:-1000}:${GID:-1000}"`)**:
  Em ambientes Linux, containers que criam arquivos em volumes bind-mounted frequentemente geram arquivos pertencentes ao usuário `root`, impedindo a deleção ou substituição pelo usuário comum do sistema operacional. O `docker-compose.yml` utiliza a variável de ambiente nativa `${UID}` e `${GID}` do host (com fallback para `1000:1000`), garantindo que todas as pastas e arquivos gerados em `volume/` pertençam ao próprio usuário que executou o comando.

- **Resolução de Contrato JNI/JAAS sem Root (`/etc/passwd`)**:
  Ao executar containers com UIDs não mapeados (ex: UID `1001`), o módulo `UnixLoginModule` da JVM do PySpark dispara a exceção `NullPointerException: invalid null input: name` por não encontrar o usuário no arquivo `/etc/passwd`. Para corrigir essa limitação sem necessidade de rodar o container como `root`, o `Dockerfile` pré-popula o intervalo de UIDs de `1000` a `1010` no `/etc/passwd`.

- **Gerenciador de Pacotes (`uv`)**:
  A imagem utiliza o instalador `uv` (Astral). As dependências Python fixadas no `requirements.txt` são instaladas em modo `--no-cache`, reduzindo o tamanho da imagem.

### PySpark

- **Execucao Distribuida nos Workers**:
  O uso de `toPandas()` transfere todo o conjunto de dados para a memória do nó Driver em um processo Python single-threaded. A função `salvar_single_parquet` foi usada para utilizar a API distribuída nativa do PySpark (`df.coalesce(1).write.mode("overwrite").parquet(...)`), mantendo toda a computação nos Worker nodes.

- **Encadeamento de DataFrames em Memoria**:
  A execução da pipeline conecta o Grafo de Execução (DAG) do Spark diretamente entre as etapas. Os DataFrames produzidos por `raw.py` são repassados diretamente em memória para `trusted.py`, e os DataFrames produzidos por `trusted.py` alimentam diretamente `delivery.py`, eliminando a necessidade de re-ler arquivos intermediários do disco.

- **Otimizacao de Shuffle com Broadcast Join**:
  No tratamento da camada Trusted, a associação com a tabela auxiliar de DePara (`tb_aux_bcb`, 5.576 linhas) utiliza a indicação `df.join(broadcast(df_aux_bcb), on="CNPJ", how="left")`. Isso elimina o *network shuffle* entre as partições, enviando a tabela de referência diretamente para a memória de cada executor.

- **Adaptive Query Execution (AQE)**:
  A `SparkSession` é instanciada com `.config("spark.sql.adaptive.enabled", "true")`. O AQE ajusta dinamicamente o número de partições de shuffle e otimiza junções com *data skew* durante as agregações de reclamações por CNPJ e conglomerado.

---

## 2: Tratamento de Dados

A engenharia de dados segue a arquitetura **Medallion (Raw ➔ Trusted ➔ Delivery)**, aplicando regras progressivas de qualidade, tratamento e agregação de dados.

### 1. Camada Raw (`raw.py`)
- **Leitura Heterogenea**: Carregamento das fontes brutas em seus formatos de origem:
  - `Bancos`: Arquivo TSV (`\t`) com cabeçalho.
  - `Empregados`: Arquivo CSV delimitado por pipe (`|`).
  - `Reclamacoes`: Arquivos CSV trimestrais combinados (encoding `latin1`, delimitador `;`), filtrando tabelas vazias (`nao_ha_dados`).
  - `Auxiliar BACEN`: Leitura de JSON multiline contendo o mapeamento de CNPJs.
- **Carga Relacional Bruta**: As 4 bases são persistidas sem alterações de esquema no schema `raw` do PostgreSQL (`raw.bancos`, `raw.empregados`, `raw.reclamacoes` e `raw.tb_aux_bcb`).

### 2. Camada Trusted (`trusted.py`)
- **Padronizacao de Chaves Primarias (CNPJ)**: Aplicação de `lpad(col("CNPJ"), 8, "0")` para garantir a formatação uniforme do CNPJ do banco em 8 dígitos com zeros à esquerda.
- **Correcao de Nomes Corrompidos via DePara**: Identificação de caracteres corrompidos (`\ufffd`) no nome das instituições e substituição condicional pelos nomes oficiais mapeados na tabela auxiliar do BACEN.
- **Higienizacao de Avaliacoes de Empregados**: Filtragem de empresas excluídas do escopo (`Apex Group`, `J.P. Morgan`, `Votorantim`) e imputação de valores nulos no ano de fundação (`NAO_INFORMADO`).
- **Sanitizacao de Reclamacoes BACEN**:
  - Remoção de espaços em branco (`trim`) no campo `CNPJ IF` e imputação do valor `"NAO_SE_APLICA"`.
  - Normalização da coluna `Índice`: substituição de vírgulas por pontos decimais, conversão de tipo para `float` e criação da flag booleana `indice_disponivel`.
- **Persistencia**: Salvamento dos arquivos Parquet sanitizados em `volume/trusted/` e carga no schema `trusted` do PostgreSQL (`trusted.bancos`, `trusted.empregados` e `trusted.reclamacoes`).

### 3. Camada Delivery (`delivery.py`)
- **Normalização para Join**: Limpeza dos nomes de bancos (remoção do sufixo ` - PRUDENCIAL`) para realizar o cruzamento `LEFT JOIN` com a base do Glassdoor.
- **Estrategia Dupla de Agregacao de Reclamacoes**:
  - **Agregação por CNPJ Individual**: Soma do total de reclamações, cálculo do índice médio e contagem de trimestres para instituições do tipo `"Banco/financeira"`.
  - **Agregação por Conglomerado**: Tratamento do nome da instituição financeira (remoção de regex `\s*\(conglomerado\)`) e agregação agrupada por conglomerado.
- **Consolidação via Fallback (`coalesce`)**: Junção das agregações individuais e de conglomerado, utilizando `coalesce()` para atribuir a métrica individual e, caso ausente, adotar a métrica agregada do conglomerado correspondente.
- **Persistencia Final**: Gravação do dataset unificado em `volume/delivery/delivery_bancos.parquet` e carga relacional na tabela `delivery.bancos` do schema `delivery` no PostgreSQL.

---

## Schemas no PostgreSQL (`banco_atividade_3`)

```text
banco_atividade_3
├── 📁 raw
│   ├── raw.bancos       (1.474 linhas)
│   ├── raw.empregados   (34 linhas)
│   ├── raw.reclamacoes  (918 linhas)
│   └── raw.tb_aux_bcb   (5.576 linhas)
├── 📁 trusted
│   ├── trusted.bancos       (1.474 linhas)
│   ├── trusted.empregados   (31 linhas)
│   └── trusted.reclamacoes  (918 linhas)
└── 📁 delivery
    └── delivery.bancos  (1.474 linhas)
```
