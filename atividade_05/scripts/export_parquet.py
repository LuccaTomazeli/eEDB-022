import os

import pandas as pd
from sqlalchemy import create_engine


PG_URL = "postgresql://postgres:postgres@pipeline-postgres:5432/eedb022_a5"

BASE_DIR = "/opt/atividade_05/data"

TRUSTED_DIR = os.path.join(
    BASE_DIR,
    "trusted"
)

DELIVERY_DIR = os.path.join(
    BASE_DIR,
    "delivery"
)


os.makedirs(TRUSTED_DIR, exist_ok=True)
os.makedirs(DELIVERY_DIR, exist_ok=True)


engine = create_engine(PG_URL)


print("========================================")
print("ATIVIDADE 5 - EXPORTAÇÃO PARQUET")
print("========================================")


tabelas_trusted = [
    "trusted_bancos",
    "trusted_reclamacoes",
    "trusted_empregados"
]


for tabela in tabelas_trusted:

    print(f"Lendo trusted.{tabela}...")

    df = pd.read_sql(
        f"SELECT * FROM trusted.{tabela}",
        engine
    )

    caminho = os.path.join(
        TRUSTED_DIR,
        f"{tabela}.parquet"
    )

    df.to_parquet(
        caminho,
        index=False
    )

    print(
        f"{tabela}: {len(df)} linhas exportadas"
    )


print("Lendo delivery.delivery_final...")

df_delivery = pd.read_sql(
    "SELECT * FROM delivery.delivery_final",
    engine
)


caminho_delivery = os.path.join(
    DELIVERY_DIR,
    "delivery_final.parquet"
)


df_delivery.to_parquet(
    caminho_delivery,
    index=False
)


print(
    f"delivery_final: {len(df_delivery)} linhas exportadas"
)


engine.dispose()


print("========================================")
print("EXPORTAÇÃO PARQUET CONCLUÍDA!")
print("========================================")