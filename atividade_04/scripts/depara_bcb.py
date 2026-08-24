import requests
import psycopg2

url = "https://olinda.bcb.gov.br/olinda/servico/BcBase/versao/v2/odata/EntidadesSupervisionadas(dataBase=@dataBase)?@dataBase='12-31-2024'&$top=10000&$format=json"

response = requests.get(url)
dados = response.json()["value"]

depara = {}
for registro in dados:
    cnpj = registro.get("codigoCNPJ8")
    nome = registro.get("nomeEntidadeInteresse")
    if cnpj and nome:
        depara[cnpj] = nome

print(f"Total de CNPJs no de-para: {len(depara)}")

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    user="postgres",
    password="postgres",
    dbname="eedb022_a4"
)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS raw.depara_bcb")
cur.execute("CREATE TABLE raw.depara_bcb (cnpj TEXT, nome TEXT)")

for cnpj, nome in depara.items():
    cur.execute("INSERT INTO raw.depara_bcb (cnpj, nome) VALUES (%s, %s)", (cnpj, nome))

conn.commit()
cur.close()
conn.close()

print("De-para carregado em raw.depara_bcb")