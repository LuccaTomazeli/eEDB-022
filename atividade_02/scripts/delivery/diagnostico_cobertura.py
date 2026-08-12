import pandas as pd

bancos = pd.read_parquet("data/trusted/bancos_trusted.parquet")
reclamacoes = pd.read_parquet("data/trusted/reclamacoes_trusted.parquet")
empregados = pd.read_parquet("data/trusted/empregados_trusted.parquet")

cnpjs_bancos = set(bancos["CNPJ"])
cnpjs_reclamacoes = set(reclamacoes["CNPJ IF"]) - {"NAO_SE_APLICA"}

print(f"CNPJs unicos em Bancos: {len(cnpjs_bancos)}")
print(f"CNPJs unicos em Reclamacoes: {len(cnpjs_reclamacoes)}")
print(f"CNPJs em comum: {len(cnpjs_bancos & cnpjs_reclamacoes)}")
print()

# testar especificamente Itau, Bradesco, Santander
for nome in ["ITAU", "BRADESCO", "SANTANDER"]:
    linha_bancos = bancos[bancos["Nome"].str.contains(nome, case=False, na=False)]
    print(f"--- {nome} em Bancos ---")
    print(linha_bancos[["Segmento", "CNPJ", "Nome"]].to_string())
    linha_reclamacoes = reclamacoes[reclamacoes["Instituição financeira"].str.contains(nome, case=False, na=False)]
    print(f"--- {nome} em Reclamacoes (CNPJs unicos) ---")
    print(linha_reclamacoes[["CNPJ IF","Instituição financeira"]].drop_duplicates().to_string())
    print()