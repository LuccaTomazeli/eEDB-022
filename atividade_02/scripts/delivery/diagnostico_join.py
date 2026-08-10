import pandas as pd

bancos = pd.read_parquet("data/trusted/bancos_trusted.parquet")
empregados = pd.read_parquet("data/trusted/empregados_trusted.parquet")

print("Amostra de Nome em Bancos:")
print(bancos["Nome"].head(10).tolist())
print()
print("Amostra de Nome em Empregados:")
print(empregados["Nome"].head(10).tolist())
print()
# conferir se BTG PACTUAL bate exatamente
print("BTG em Bancos:", bancos[bancos["Nome"].str.contains("BTG", na=False)]["Nome"].tolist())
print("BTG em Empregados:", empregados[empregados["Nome"].str.contains("BTG", na=False)]["Nome"].tolist())