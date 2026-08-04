# Atividade 1 - Ingestão de Dados eEDB-022
read.me gerado por IA, com base no relatório de execução ;)

Curso de Especialização em Big Data, Escola Politécnica da USP
Disciplina: Ingestão de Dados (eEDB-022)

Grupo: Camila Faleiros, Fernando Luiz, Guilherme Sergio e Lucca Tomazeli

## Objetivo

Realizar a ingestão e o tratamento (ETL) de três fontes de dados distintas, utilizando uma ferramenta visual, e gravar os dados tratados e unidos em uma tabela final dentro de um banco de dados relacional open source.

## Stack utilizada

- Banco de dados: PostgreSQL, executado via Docker
- Ferramenta de ETL: Apache Hop
- Ambiente: macOS, container `pg_eedb022`

## Ambiente

O banco PostgreSQL foi subido em um container Docker (`pg-eedb022`) e a conexão foi validada via `psql` diretamente dentro do container. Em seguida, o Apache Hop foi instalado e um projeto chamado `eEDB-022` foi configurado, apontando para a pasta local do repositório do curso. A conexão do Hop com o PostgreSQL (host localhost, porta 5433, banco `eedb022`) foi testada com sucesso.

## Fontes de dados e pipelines

### 1. Bancos

Arquivo `EnquadramentoInicial_v2.tsv` lido através de um transform de leitura de arquivo texto, com os campos Segmento, CNPJ e Nome. Foi identificado que os CNPJs apareciam sem os zeros à esquerda; a padronização foi deixada para a etapa de tratamento e join final.

Ao gravar os dados na tabela `stg_bancos`, ocorreu um erro porque a coluna Nome era menor do que o necessário. A coluna foi alterada para `VARCHAR(255)` diretamente no PostgreSQL e o pipeline passou a rodar com sucesso.

### 2. Empregados

Os dados vieram divididos em dois arquivos (`glassdoor_consolidado_join_match_v2.csv` e `glassdoor_consolidado_join_match_less_v2.csv`), resultado de duas estratégias de casamento com a base de Bancos: a primeira por Segmento mais Nome, a segunda por CNPJ mais Nome, usada como alternativa para os registros que não bateram pelo nome.

Como cada arquivo possui uma coluna que o outro não tem (Segmento em um, CNPJ no outro), o pipeline:

1. Lê os dois arquivos separadamente
2. Adiciona a coluna faltante como vazia em cada fluxo
3. Reordena os campos para garantir a mesma sequência de colunas nos dois lados
4. Une os fluxos via Append streams
5. Grava o resultado consolidado na tabela `stg_empregados`

O pipeline uniu 39 registros das duas fontes sem erros na execução.

### 3. Reclamações

Os dados vieram divididos em oito arquivos trimestrais (2021 e 2022), todos com a mesma estrutura de colunas. O transform de leitura usa wildcard para ler automaticamente todos os arquivos CSV da pasta, excluindo o arquivo `2022_tri_02_nao_ha_dados.csv`, identificado como vazio e sem relevância para a ingestão. Como os sete arquivos válidos compartilham a mesma estrutura, o próprio Text file input já consolida todos eles em um único fluxo, sem necessidade de um passo de união, e o resultado é gravado na tabela `stg_reclamacoes`.

Durante a execução desse pipeline, foram encontrados e corrigidos os seguintes problemas, em sequência:

1. A coluna Categoria tinha valores mais longos do que o `VARCHAR(16)` definido pela detecção automática de tipos. Corrigido aumentando a coluna para `VARCHAR(50)` no PostgreSQL, e depois novamente para `VARCHAR(100)` quando um valor ainda maior apareceu.
2. Algumas colunas numéricas continham espaços em branco em vez de valores, impedindo a conversão para Integer. Corrigido ajustando o Trim Type dos campos numéricos no Hop.
3. As colunas do tipo Number continham valores no padrão brasileiro (ponto como separador de milhar e vírgula como decimal), enquanto o Hop estava configurado para o padrão americano. Corrigido invertendo as configurações de Decimal e Group dos campos numéricos no Text file input.

Após essas correções, o pipeline processou os sete arquivos com sucesso.

## Pipeline final

Com as três tabelas de staging (`stg_bancos`, `stg_empregados`, `stg_reclamacoes`) já carregadas, a pipeline final segue os passos abaixo:

1. Leitura da tabela `stg_reclamacoes`, usada como fato por ser a maior das três
2. Padronização dos CNPJs em todas as três origens, concatenando oito zeros à esquerda e mantendo os últimos 8 caracteres, garantindo o mesmo formato em todas as tabelas
3. Stream lookup em Bancos, buscando o segmento e o nome da instituição correspondente a cada reclamação
4. Stream lookup em Empregados, a partir do resultado já enriquecido, buscando as notas de avaliação do Glassdoor daquele mesmo banco
5. Gravação do resultado final, unindo dados de reclamações, identificação do banco e notas dos funcionários, na tabela `tb_final_bancos_reclamacoes`

## Resultado

A tabela `tb_final_bancos_reclamacoes` foi criada e populada com sucesso no PostgreSQL, reunindo dados de reclamações, identificação das instituições financeiras e avaliações dos funcionários em um único conjunto de dados tratado.
