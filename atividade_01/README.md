# 🚀 Atividade 01 - Pipeline de Ingestão e Tratamento de Dados (ETL)

**Curso de Especialização em Big Data — Escola Politécnica da USP**  
**Disciplina**: Ingestão de Dados (eEDB-022)  
**Grupo**: Camila Faleiros, Fernando Luiz, Guilherme Sergio e Lucca Tomazeli  

---

## 🎯 1. Objetivo do Projeto

Realizar a ingestão, tratamento e consolidação (processo ETL) de três fontes de dados distintas (bancos, empregados e reclamações do BACEN), utilizando o **Apache Hop** como ferramenta visual de integração de dados, e armazenar os dados tratados e consolidados em um banco de dados relacional **PostgreSQL** containerizado.

---

## 🛠️ 2. Stack Utilizada

- **Banco de Dados Relacional**: PostgreSQL
- **Ferramenta de ETL & Orquestração**: Apache Hop Web (imagem `apache/hop-web:latest`)
- **Ambiente & Orquestração de Containers**: Docker e Docker Compose
- **Formatos de Pipelines/Workflows**: Apache Hop XML (`.hpl` para pipelines e `.hwf` para workflows)

---

## 📖 3. Guia de Uso (Como Executar)

### Pré-requisitos
- [Docker Engine](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/) instalados na sua máquina.

### Passo 1: Subir os Containers
Navegue até o diretório `atividade_01` e execute o comando:

```bash
cd atividade_01
docker compose up -d --build
```

Isso iniciará os dois serviços necessários:
- **`postgres_atividade_01`**: Banco de dados PostgreSQL escutando na porta `5432` (Banco: `atividade_01`, Usuário: `root`, Senha: `root`).
- **`hop_atividade_01`**: Apache Hop Web acessível na porta `8080`.

---

### Passo 2: Acessar a Interface do Apache Hop Web
Abra o navegador de sua preferência e acesse:
```text
http://localhost:8080/
```
O Apache Hop Web abrirá o projeto `default` automaticamente, apontando para a pasta montada no repositório.

---

### Passo 3: Executar o Workflow Principal

Você pode executar o fluxo de carga de duas maneiras:

#### Opção A: Pela Interface Web (Apache Hop GUI / Web)
1. No menu principal do Hop Web, abra o arquivo `workflow_principal.hwf` localizado dentro da pasta `atividade_01`.
2. Clique no ícone de execução ▶️ (**Run**) na barra de ferramentas superior.
3. Selecione a configuração de execução **`local`** e clique em **Launch**.

#### Opção B: Via Linha de Comando (CLI sem interface)
Para disparar a execução de ponta a ponta em segundo plano via terminal:

```bash
docker exec hop_atividade_01 /usr/local/tomcat/webapps/ROOT/hop-run.sh \
  -j default \
  -r local \
  -f /usr/local/tomcat/webapps/ROOT/config/projects/default/atividade_01/workflow_principal.hwf
```

---

## 🔄 4. Descrição dos Tratamentos Realizados

O projeto é orquestrado por 1 Workflow (`.hwf`) que coordena 4 Pipelines (`.hpl`):


---

### 🔹 Step 0: Orquestrador (`workflow_principal.hwf`)
Garante a execução completa em ambientes totalmente limpos (sem necessidade de criação manual prévia de estruturas no banco):
1. **Execução SQL Inicial (`criar_tabelas_sql`)**: Executa DDLs `CREATE TABLE IF NOT EXISTS` garantindo que as tabelas de staging e a tabela final existam com os tipos de dados e nomes de colunas corretos.
2. **Execução Sequencial Síncrona**: Chama cada pipeline aguardando o término da execução (`wait_until_finished = Y`) antes de iniciar o próximo passo.

---

### 🔹 Pipeline 1: Ingestão de Bancos (`pipeline_ingestao_bancos.hpl`)
- **Origem**: `${DADOS_HOME}/Bancos/EnquadramentoInicia_v2.tsv` (Arquivo TSV).
- **Tratamentos**:
  - Leitura com encoding `ISO-8859-1` e separador de tabulação (`\t`).
  - Ampliação do tamanho do campo `Nome` para `VARCHAR(255)` para suportar nomes extensos de cooperativas e instituições financeiras.
- **Destino**: Tabela staging `stg_bancos` (**1.474 registros**).

---

### 🔹 Pipeline 2: Ingestão de Empregados (`pipeline_ingestao_empregados.hpl`)
- **Origem**: Dois arquivos com dados do Glassdoor (`glassdoor_consolidado_join_match_v2.csv` e `glassdoor_consolidado_join_match_less_v2.csv`), decorrentes de duas estratégias de pareamento (uma por Nome+Segmento e outra alternativa por Nome+CNPJ).
- **Tratamentos**:
  - Como cada arquivo possuía uma coluna ausente em relação ao outro (`Segmento` em um, `CNPJ` no outro), foi adicionada a coluna faltante como valor nulo em cada fluxo.
  - Reordenação e padronização das colunas dos dois fluxos.
  - Consolidação dos fluxos via transform `Append streams`.
- **Destino**: Tabela staging `stg_empregados` (**39 registros**).

---

### 🔹 Pipeline 3: Ingestão de Reclamações (`pipeline_ingestao_reclamacoes.hpl`)
- **Origem**: Arquivos trimestrais de reclamações do BACEN referentes aos anos de 2021 e 2022 (`${DADOS_HOME}/Reclamacoes/*.csv`).
- **Tratamentos**:
  - Leitura multi-arquivo através de padrão wildcard, ignorando o arquivo `2022_tri_02_nao_ha_dados.csv` (sem dados).
  - Ajuste na formatação de números (vírgula `,` para decimal e ponto `.` para agrupamento de milhar).
  - Remoção de espaços em branco (trimming) para prevenir falhas de conversão em campos vazios.
- **Destino**: Tabela staging `stg_reclamacoes` (**918 registros**).

---

### 🔹 Pipeline 4: Tratamento e Consolidação Final (`pipeline_tratamento_final.hpl`)
- **Origem**: Leitura das 3 tabelas staging (`stg_reclamacoes`, `stg_bancos`, `stg_empregados`).
- **Tratamentos**:
  - **Padronização de CNPJ**: Aplicação da fórmula `RIGHT(CONCATENATE("00000000", [cnpj]), 8)` em todos os três fluxos para formatar os CNPJs com exatamente 8 dígitos com zeros à esquerda (ex: `00000000`, `00000001` etc.).
  - **Stream Lookup 1 (Bancos)**: Junção pelo CNPJ padronizado para resgatar o Nome e Segmento oficial de cada instituição financeira em cada reclamação.
  - **Stream Lookup 2 (Empregados)**: Junção pelo CNPJ padronizado para anexar as métricas de avaliação dos funcionários (Geral, Cultura e Valores, Remuneração e Benefícios, Total de Reviews).
- **Destino**: Tabela final `tb_final_bancos_reclamacoes` (**918 registros**).

---

### 📊 Tabela Final Resultante

| Tabela no PostgreSQL | Registros Populados | Função no Pipeline |
| :--- | :---: | :--- |
| `stg_bancos` | 1.474 | Staging de Instituições Financeiras |
| `stg_empregados` | 39 | Staging de Avaliações do Glassdoor |
| `stg_reclamacoes` | 918 | Staging de Reclamações do BACEN |
| **`tb_final_bancos_reclamacoes`** | **918** | **Tabela Final Consolidada (DW/Analytics)** |
