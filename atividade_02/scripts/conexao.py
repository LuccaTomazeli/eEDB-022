import os
from sqlalchemy import create_engine

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "eedb022_a2")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "camila123")


def get_engine():
    connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(connection_string)
    return engine


if __name__ == "__main__":
    engine = get_engine()
    try:
        with engine.connect() as conn:
            print("Conexão com o banco funcionando :)")
    except Exception as e:
        print(f"Erro ao conectar: {e}")

        