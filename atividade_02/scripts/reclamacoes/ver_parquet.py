import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

df = pd.read_parquet("data/trusted/reclamacoes_trusted.parquet")
print(df.shape)
print(df[["Ano", "Trimestre", "Instituição financeira", "CNPJ IF", "Tipo", "Índice"]].head(15).to_string())
print()
print("Distribuição por Ano/Trimestre:")
print(df.groupby(["Ano", "Trimestre"]).size())