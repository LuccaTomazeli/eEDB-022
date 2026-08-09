import requests
import json

url = "https://olinda.bcb.gov.br/olinda/servico/BcBase/versao/v2/odata/EntidadesSupervisionadas(dataBase=@dataBase)?@dataBase='12-31-2024'&$top=10000&$format=json"

response = requests.get(url)
dados = response.json()["value"]

print(f"Total de registros recebidos: {len(dados)}")

depara = {}
for registro in dados:
    cnpj = registro.get("codigoCNPJ8")
    nome = registro.get("nomeEntidadeInteresse")
    if cnpj and nome:
        depara[cnpj] = nome

print(f"Total de CNPJs únicos no de-para: {len(depara)}")

with open("data/raw/depara_bcb.json", "w", encoding="utf-8") as f:
    json.dump(depara, f, ensure_ascii=False, indent=2)

print("De-para salvo em data/raw/depara_bcb.json")