import pandas as pd

# 1. ler apenas o match_v2, que já contém todas as empresas
df = pd.read_csv("data/raw/Empregados/glassdoor_consolidado_join_match_v2.csv", sep="|", dtype=str)
print(f"match_v2: {df.shape[0]} linhas, {df.shape[1]} colunas")

# 2. remover os matches identificados como incorretos ou duplicados
empresas_excluidas = ["Apex Group", "J.P. Morgan"]  # Apex Group: match incorreto | J.P. Morgan: duplicata do JPMorgan Chase & Co (menos reviews)
df = df[~df["employer_name"].isin(empresas_excluidas)]
print(f"Total após exclusão: {df.shape[0]} linhas")

# 3. tratar nulos em employer-founded
print(f"Nulos em employer-founded antes: {df['employer-founded'].isnull().sum()}")
df["employer-founded"] = df["employer-founded"].fillna("NAO_INFORMADO")

# 4. salvar como parquet na camada trusted
df.to_parquet("data/trusted/empregados_trusted.parquet", index=False)
print(f"Arquivo salvo em data/trusted/empregados_trusted.parquet com {len(df)} linhas")

