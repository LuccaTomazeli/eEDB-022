import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 250)

df = pd.read_parquet("data/delivery/delivery_bancos.parquet")
print(df.shape)
print(df.columns.tolist())
print()

# amostra de bancos que tem os dois: glassdoor e reclamacoes
com_ambos = df[df["Geral"].notnull() & df["total_reclamacoes"].notnull()]
print(f"Bancos com Glassdoor E Reclamacoes: {len(com_ambos)}")
print(com_ambos[["Nome", "Geral", "total_reclamacoes", "indice_medio"]].to_string())