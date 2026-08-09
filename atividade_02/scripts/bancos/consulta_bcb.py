import requests

url = "https://olinda.bcb.gov.br/olinda/servico/BcBase/versao/v2/odata/EntidadesSupervisionadas(dataBase=@dataBase)?@dataBase='12-31-2024'&$top=3&$format=json"

response = requests.get(url)
print(response.status_code)
print(response.json())