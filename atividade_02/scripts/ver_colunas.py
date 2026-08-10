import pandas as pd

bancos = pd.read_parquet("data/trusted/bancos_trusted.parquet")
empregados = pd.read_parquet("data/trusted/empregados_trusted.parquet")
reclamacoes = pd.read_parquet("data/trusted/reclamacoes_trusted.parquet")

print("BANCOS:", list(bancos.columns))
print()
print("EMPREGADOS:", list(empregados.columns))
print()
print("RECLAMACOES:", list(reclamacoes.columns))