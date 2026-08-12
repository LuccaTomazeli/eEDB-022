import pandas as pd

bancos = pd.read_parquet("data/trusted/bancos_trusted.parquet")
empregados = pd.read_parquet("data/trusted/empregados_trusted.parquet")

bancos["nome_join"] = bancos["Nome"].str.replace(" - PRUDENCIAL", "", regex=False).str.strip()
empregados["nome_join"] = empregados["Nome"].str.strip()

matches = empregados.merge(bancos[["nome_join", "CNPJ"]], on="nome_join", how="left")
print(f"Empregados com CNPJ encontrado (match exato): {matches['CNPJ'].notnull().sum()} de {len(matches)}")
print()
print("Empresas SEM match:")
print(matches[matches["CNPJ"].isnull()][["employer_name", "Nome"]].to_string())