import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres:postgres@localhost:5433/eedb022_a4")

tabelas_trusted = ["trusted_bancos", "trusted_reclamacoes", "trusted_empregados"]

for tabela in tabelas_trusted:
    df = pd.read_sql(f"SELECT * FROM trusted.{tabela}", engine)
    df.to_parquet(f"data/trusted/{tabela}.parquet", index=False)
    print(f"{tabela}: {len(df)} linhas exportadas")

df_delivery = pd.read_sql("SELECT * FROM trusted.delivery_final", engine)
df_delivery.to_parquet("data/delivery/delivery_final.parquet", index=False)
print(f"delivery_final: {len(df_delivery)} linhas exportadas")