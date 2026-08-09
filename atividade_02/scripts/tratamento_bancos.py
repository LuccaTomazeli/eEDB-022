import pandas as pd
import json
import unicodedata

# carregar o de-para de cnpj -> nome oficial
with open("data/raw/depara_bcb.json", encoding="utf-8") as f:
    depara = json.load(f)

# 2. ler o tsv original
df = pd.read_csv("data/raw/Bancos/EnquadramentoInicia_v2.tsv", sep="\t", dtype=str)

print(f"Total de linhas lidas: {len(df)}")
print(f"Valores nulos por coluna:\n{df.isnull().sum()}")

# 3. normalizar o cnpj (zero à esquerda, 8 dígitos)
df["CNPJ"] = df["CNPJ"].str.zfill(8)

# 4. identificar linhas com nome quebrado
df["nome_quebrado"] = df["Nome"].str.contains("\ufffd", na=False)
print(f"Linhas com nome quebrado antes da correção: {df['nome_quebrado'].sum()}")

# 5. corrigir os nomes usando o de-para (quando encontrado)
def corrigir_nome(row):
    if row["nome_quebrado"] and row["CNPJ"] in depara:
        return depara[row["CNPJ"]]
    return row["Nome"]

df["Nome"] = df.apply(corrigir_nome, axis=1)

# 6. verificar quantos ainda ficaram quebrados (cnpj não encontrado no de-para)
df["nome_ainda_quebrado"] = df["Nome"].str.contains("\ufffd", na=False)
print(f"Linhas com nome ainda quebrado após correção: {df['nome_ainda_quebrado'].sum()}")

# 7. tratar nulos remanescentes
df["Nome"] = df["Nome"].fillna("NAO_INFORMADO")
df["Segmento"] = df["Segmento"].fillna("NAO_INFORMADO")

# 8. remover colunas auxiliares que criamos só para o diagnóstico
df = df.drop(columns=["nome_quebrado", "nome_ainda_quebrado"])

# 9. salvar como parquet na camada trusted
df.to_parquet("data/trusted/bancos_trusted.parquet", index=False)

print(f"Arquivo salvo em data/trusted/bancos_trusted.parquet com {len(df)} linhas")