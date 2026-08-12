import pandas as pd
import glob

# 1. listar todos os csvs de reclamacoes, exceto o vazio
arquivos = sorted(glob.glob("data/raw/Reclamacoes/*.csv"))
arquivos = [a for a in arquivos if "nao_ha_dados" not in a]
print(f"Arquivos a processar: {len(arquivos)}")
for a in arquivos:
    print(" -", a)

# 2. ler e empilhar todos os trimestres
dfs = []
for arq in arquivos:
    df_temp = pd.read_csv(arq, sep=";", encoding="latin1", dtype=str)
    dfs.append(df_temp)

df = pd.concat(dfs, ignore_index=True)
print(f"Total após empilhar todos os trimestres: {df.shape[0]} linhas")

# 3. remover a coluna fantasma (Unnamed: 14)
df = df.loc[:, ~df.columns.str.startswith("Unnamed")]

# 4. corrigir nomes de colunas com caractere quebrado (\x96 = travessão)
df.columns = [c.replace("\x96", "-") for c in df.columns]
print("Colunas finais:", list(df.columns))

# 5. tratar CNPJ vazio (esperado para linhas tipo Conglomerado)
df["CNPJ IF"] = df["CNPJ IF"].str.strip()
df["CNPJ IF"] = df["CNPJ IF"].replace("", "NAO_SE_APLICA")

# 6. tratar indice: sinalizar disponibilidade, remover separador de milhar, virgula -> ponto, converter para numero
df["Índice"] = df["Índice"].str.strip()
df["indice_disponivel"] = df["Índice"] != ""
df["Índice"] = df["Índice"].replace("", None)
df["Índice"] = df["Índice"].str.replace(".", "", regex=False)
df["Índice"] = df["Índice"].str.replace(",", ".", regex=False)
df["Índice"] = df["Índice"].astype(float)
print(f"Linhas com indice_disponivel = False: {(~df['indice_disponivel']).sum()}")

# 7. salvar como parquet na camada trusted
df.to_parquet("data/trusted/reclamacoes_trusted.parquet", index=False)
print(f"Arquivo salvo em data/trusted/reclamacoes_trusted.parquet com {len(df)} linhas")