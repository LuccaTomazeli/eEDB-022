"""Carrega o JSON de enquadramento na tabela PostgreSQL usada pelo consumidor."""

import json
import os
import re
from pathlib import Path

import psycopg2


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower().strip())


def main() -> None:
    source = Path(os.getenv("LOOKUP_FILE", "dados_json/bancos/EnquadramentoInicia_v2.json"))
    with source.open(encoding="utf-8") as file:
        records = json.load(file)
    connection = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "atividade8"),
        user=os.getenv("POSTGRES_USER", "atividade8"),
        password=os.getenv("POSTGRES_PASSWORD", "atividade8"),
    )
    with connection, connection.cursor() as cursor:
        for record in records:
            data = record["dados"]
            cnpj = re.sub(r"\D", "", str(data.get("CNPJ", ""))) or f"sem-cnpj-{record['linha_origem']}"
            name = str(data.get("Nome", "")).strip()
            cursor.execute(
                """INSERT INTO banco_enquadramento (cnpj, nome, segmento, nome_normalizado)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cnpj) DO UPDATE SET nome = EXCLUDED.nome,
                    segmento = EXCLUDED.segmento, nome_normalizado = EXCLUDED.nome_normalizado""",
                (cnpj, name, data.get("Segmento"), normalize(name)),
            )
    print(f"Registros carregados: {len(records)}")


if __name__ == "__main__":
    main()