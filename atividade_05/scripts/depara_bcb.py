import requests
import psycopg2


URL_BCB = (
    "https://olinda.bcb.gov.br/olinda/servico/BcBase/"
    "versao/v2/odata/EntidadesSupervisionadas"
    "(dataBase=@dataBase)?"
    "@dataBase='12-31-2024'"
    "&$top=10000"
    "&$format=json"
)

PG_CONFIG = {
    "host": "pipeline-postgres",
    "port": 5432,
    "user": "postgres",
    "password": "postgres",
    "dbname": "eedb022_a5",
}


print("========================================")
print("ATIVIDADE 5 - DE-PARA BCB")
print("========================================")

print("Consultando dados do Banco Central...")

response = requests.get(
    URL_BCB,
    timeout=60
)

response.raise_for_status()

dados = response.json()["value"]

print(f"Registros retornados pelo BCB: {len(dados)}")

depara = {}

for registro in dados:
    cnpj = registro.get("codigoCNPJ8")
    nome = registro.get("nomeEntidadeInteresse")

    if cnpj and nome:
        depara[cnpj] = nome

print(f"Total de CNPJs no de-para: {len(depara)}")


print("Conectando ao PostgreSQL...")

conn = psycopg2.connect(**PG_CONFIG)

cur = conn.cursor()


print("Recriando tabela raw.depara_bcb...")

cur.execute("DROP TABLE IF EXISTS raw.depara_bcb")

cur.execute(
    """
    CREATE TABLE raw.depara_bcb (
        cnpj TEXT,
        nome TEXT
    )
    """
)


print("Inserindo dados...")

for cnpj, nome in depara.items():

    cur.execute(
        """
        INSERT INTO raw.depara_bcb (cnpj, nome)
        VALUES (%s, %s)
        """,
        (cnpj, nome)
    )


conn.commit()

cur.close()
conn.close()


print("========================================")
print("DE-PARA BCB CONCLUÍDO!")
print(f"Total de registros carregados: {len(depara)}")
print("Tabela: raw.depara_bcb")
print("========================================")