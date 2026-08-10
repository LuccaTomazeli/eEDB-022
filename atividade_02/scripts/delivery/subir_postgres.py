import pandas as pd
import sys
sys.path.append("scripts")
from conexao import get_engine

df = pd.read_parquet("data/trusted/delivery_bancos.parquet")

engine = get_engine()
df.to_sql("delivery_bancos", engine, if_exists="replace", index=False)

print(f"Tabela 'delivery_bancos' criada no Postgres com {len(df)} linhas")