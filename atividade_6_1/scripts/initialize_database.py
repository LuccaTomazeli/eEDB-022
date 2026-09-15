import os
from pathlib import Path

import pymysql


TABLE_STATEMENTS = {
    "bancos": """CREATE TABLE IF NOT EXISTS bancos (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        arquivo_origem VARCHAR(255) NOT NULL,
        linha_origem INT NOT NULL,
        dados JSON NOT NULL,
        criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_bancos_origem (arquivo_origem, linha_origem)
    )""",
    "empregados": """CREATE TABLE IF NOT EXISTS empregados (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        arquivo_origem VARCHAR(255) NOT NULL,
        linha_origem INT NOT NULL,
        dados JSON NOT NULL,
        criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_empregados_origem (arquivo_origem, linha_origem)
    )""",
    "reclamacoes": """CREATE TABLE IF NOT EXISTS reclamacoes (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        arquivo_origem VARCHAR(255) NOT NULL,
        linha_origem INT NOT NULL,
        dados JSON NOT NULL,
        criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_reclamacoes_origem (arquivo_origem, linha_origem)
    )""",
    "dados_enriquecidos": """CREATE TABLE IF NOT EXISTS dados_enriquecidos (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        banco_id BIGINT NOT NULL,
        cnpj VARCHAR(30),
        nome_original VARCHAR(255),
        nome_normalizado VARCHAR(255) NOT NULL,
        segmento VARCHAR(50),
        empregado_match JSON NOT NULL,
        reclamacoes_resumo JSON NOT NULL,
        total_reclamacoes INT NOT NULL DEFAULT 0,
        indice_medio DECIMAL(12, 2),
        nota_media_empregados DECIMAL(5, 2),
        dados_tratados JSON NOT NULL,
        enriquecido_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_dados_enriquecidos_banco (banco_id)
    )""",
}


def load_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def main():
    load_env()
    connection = pymysql.connect(
        host=os.environ["SQL_HOST"],
        port=int(os.environ.get("SQL_PORT", "3306")),
        user=os.environ["SQL_USER"],
        password=os.environ["SQL_PASSWORD"],
        database=os.environ["SQL_DATABASE"],
        connect_timeout=10,
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            for table, statement in TABLE_STATEMENTS.items():
                cursor.execute(statement)
                print(f"Tabela pronta: {table}")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
