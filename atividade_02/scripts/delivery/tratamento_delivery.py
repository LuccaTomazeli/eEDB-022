import pandas as pd

# 1. ler as tres tabelas trusted
bancos = pd.read_parquet("data/trusted/bancos_trusted.parquet")
empregados = pd.read_parquet("data/trusted/empregados_trusted.parquet")
reclamacoes = pd.read_parquet("data/trusted/reclamacoes_trusted.parquet")

print(f"Bancos: {bancos.shape[0]} linhas")
print(f"Empregados: {empregados.shape[0]} linhas")
print(f"Reclamacoes: {reclamacoes.shape[0]} linhas")

# 2. criar coluna auxiliar de nome normalizado em bancos, so para o join
bancos["nome_join"] = bancos["Nome"].str.replace(" - PRUDENCIAL", "", regex=False).str.strip()
empregados["nome_join"] = empregados["Nome"].str.strip()

# 3. juntar bancos com empregados, usando nome_join (match exato)
colunas_glassdoor = [
    "nome_join", "employer_name", "Geral", "Cultura e valores",
    "Diversidade e inclusão", "Qualidade de vida", "Alta liderança",
    "Remuneração e benefícios", "Oportunidades de carreira",
    "reviews_count", "match_percent"
]
df = bancos.merge(empregados[colunas_glassdoor], on="nome_join", how="left")
print(f"Apos juntar com Empregados: {df.shape[0]} linhas")
print(f"Bancos com dado do Glassdoor: {df['Geral'].notnull().sum()}")

# 4a. agregar reclamacoes do tipo Banco/financeira (tem CNPJ), agrupando por CNPJ
reclamacoes_individual = reclamacoes[reclamacoes["Tipo"] == "Banco/financeira"]
agregado_individual = reclamacoes_individual.groupby("CNPJ IF").agg(
    total_reclamacoes=("Quantidade total de reclamações", lambda x: x.astype(float).sum()),
    indice_medio=("Índice", "mean"),
    trimestres_com_reclamacao=("Trimestre", "count")
).reset_index()
agregado_individual = agregado_individual.rename(columns={"CNPJ IF": "CNPJ"})
print(f"Instituicoes individuais com reclamacoes agregadas: {agregado_individual.shape[0]}")

# 4b. agregar reclamacoes do tipo Conglomerado (sem CNPJ), agrupando por nome normalizado
reclamacoes_conglomerado = reclamacoes[reclamacoes["Tipo"] == "Conglomerado"].copy()
reclamacoes_conglomerado["nome_join"] = reclamacoes_conglomerado["Instituição financeira"].str.replace(
    r"\s*\(conglomerado\)", "", regex=True
).str.strip()
agregado_conglomerado = reclamacoes_conglomerado.groupby("nome_join").agg(
    total_reclamacoes_cong=("Quantidade total de reclamações", lambda x: x.astype(float).sum()),
    indice_medio_cong=("Índice", "mean"),
    trimestres_com_reclamacao_cong=("Trimestre", "count")
).reset_index()
print(f"Conglomerados com reclamacoes agregadas: {agregado_conglomerado.shape[0]}")

# 5. juntar os dois agregados na tabela principal
df = df.merge(agregado_individual, on="CNPJ", how="left")
df = df.merge(agregado_conglomerado, on="nome_join", how="left")

# 6. unificar as colunas: usa o valor individual se existir, senao usa o de conglomerado
df["total_reclamacoes"] = df["total_reclamacoes"].fillna(df["total_reclamacoes_cong"])
df["indice_medio"] = df["indice_medio"].fillna(df["indice_medio_cong"])
df["trimestres_com_reclamacao"] = df["trimestres_com_reclamacao"].fillna(df["trimestres_com_reclamacao_cong"])
df = df.drop(columns=["total_reclamacoes_cong", "indice_medio_cong", "trimestres_com_reclamacao_cong"])

print(f"Apos juntar com Reclamacoes (individual + conglomerado): {df.shape[0]} linhas")
print(f"Bancos com dado de reclamacoes: {df['total_reclamacoes'].notnull().sum()}")
print(f"Bancos com Glassdoor E Reclamacoes: {(df['Geral'].notnull() & df['total_reclamacoes'].notnull()).sum()}")

# 7. remover coluna auxiliar
df = df.drop(columns=["nome_join"])

# 8. salvar como parquet na camada delivery
df.to_parquet("data/trusted/delivery_bancos.parquet", index=False)
print(f"Arquivo salvo com {len(df)} linhas e {len(df.columns)} colunas")