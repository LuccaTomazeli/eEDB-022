import pandas as pd
pd.set_option("display.max_columns", None)

df = pd.read_parquet("data/trusted/empregados_trusted.parquet")
print(df.shape)
print(df[["employer_name", "Nome", "match_percent"]].to_string())