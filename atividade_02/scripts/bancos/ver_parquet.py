import pandas as pd

df = pd.read_parquet("data/trusted/bancos_trusted.parquet")
print(df.shape)
print(df.head(10))
print(df[df["Nome"].str.contains("PARAN", na=False)])