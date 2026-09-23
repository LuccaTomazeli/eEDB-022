import argparse
import json
import os
from pathlib import Path

import pymysql


TABLES = ("bancos", "empregados", "reclamacoes")


def load_env_file():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main():
    parser = argparse.ArgumentParser(description="Consulta as tabelas do projeto.")
    parser.add_argument("--limit", type=int, default=2, help="Amostras por tabela.")
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit deve ser maior que zero")

    load_env_file()
    required = ("SQL_HOST", "SQL_USER", "SQL_PASSWORD", "SQL_DATABASE")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit(f"Variaveis ausentes: {', '.join(missing)}")

    connection = pymysql.connect(
        host=os.environ["SQL_HOST"],
        port=int(os.environ.get("SQL_PORT", "3306")),
        user=os.environ["SQL_USER"],
        password=os.environ["SQL_PASSWORD"],
        database=os.environ["SQL_DATABASE"],
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with connection.cursor() as cursor:
            print("=== CONTAGENS ===")
            for table in TABLES:
                cursor.execute(f"SELECT COUNT(*) AS total FROM {table}")
                print(f"{table}: {cursor.fetchone()['total']}")

            print("\n=== AMOSTRAS ===")
            for table in TABLES:
                cursor.execute(
                    f"""SELECT id, arquivo_origem, linha_origem, dados, criado_em
                        FROM {table} ORDER BY id DESC LIMIT %s""",
                    (args.limit,),
                )
                print(f"\n[{table}]")
                for row in cursor.fetchall():
                    row["dados"] = json.loads(row["dados"])
                    print(json.dumps(row, ensure_ascii=False, default=str, indent=2))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
