import json
import glob
from pyspark.sql.functions import col, lpad, when, trim, regexp_replace


def processar_bancos(spark):
    with open("volume/raw/tb_aux_bcb.json", encoding="utf-8") as f:
        depara_dict = json.load(f)
    depara_data = [(k, v) for k, v in depara_dict.items()]
    df_depara = spark.createDataFrame(depara_data, ["CNPJ", "Nome_DePara"])

    df = spark.read.option("header", "true").option("delimiter", "\t").csv("../Dados/Bancos/EnquadramentoInicia_v2.tsv")
    df = df.withColumn("CNPJ", lpad(col("CNPJ"), 8, "0"))
    df = df.withColumn("nome_quebrado", col("Nome").contains("\ufffd"))
    df = df.join(df_depara, on="CNPJ", how="left")
    df = df.withColumn(
        "Nome",
        when(col("nome_quebrado") & col("Nome_DePara").isNotNull(), col("Nome_DePara")).otherwise(col("Nome"))
    )
    df = df.fillna({"Nome": "NAO_INFORMADO", "Segmento": "NAO_INFORMADO"})
    return df.drop("nome_quebrado", "Nome_DePara")


def processar_empregados(spark):
    df = spark.read.option("header", "true").option("delimiter", "|").csv("../Dados/Empregados/glassdoor_consolidado_join_match_v2.csv")
    empresas_excluidas = ["Apex Group", "J.P. Morgan", "Votorantim"]
    df = df.filter(~col("employer_name").isin(empresas_excluidas))
    return df.fillna({"employer-founded": "NAO_INFORMADO"})


def processar_reclamacoes(spark):
    arquivos = sorted(glob.glob("../Dados/Reclamacoes/*.csv"))
    arquivos = [a for a in arquivos if "nao_ha_dados" not in a]
    df = spark.read.option("header", "true").option("delimiter", ";").option("encoding", "latin1").csv(arquivos)
    colunas_validas = [c for c in df.columns if not c.startswith("Unnamed")]
    df = df.select(colunas_validas)

    for c in df.columns:
        novo_nome = c.replace("\x96", "-").replace("\u0096", "-")
        if novo_nome != c:
            df = df.withColumnRenamed(c, novo_nome)

    df = df.withColumn("CNPJ IF", trim(col("CNPJ IF")))
    df = df.withColumn("CNPJ IF", when((col("CNPJ IF") == "") | col("CNPJ IF").isNull(), "NAO_SE_APLICA").otherwise(col("CNPJ IF")))
    df = df.withColumn("indice_limpo", trim(col("Índice")))
    df = df.withColumn("indice_disponivel", when((col("indice_limpo") != "") & col("indice_limpo").isNotNull(), True).otherwise(False))
    df = df.withColumn("indice_temp", regexp_replace(col("indice_limpo"), "\\.", ""))
    df = df.withColumn("indice_temp", regexp_replace(col("indice_temp"), ",", "."))
    df = df.withColumn("Índice", when(col("indice_disponivel"), col("indice_temp").cast("float")).otherwise(None))
    return df.drop("indice_limpo", "indice_temp")


def processar_trusted(spark):
    df_bancos = processar_bancos(spark)
    df_empregados = processar_empregados(spark)
    df_reclamacoes = processar_reclamacoes(spark)
    return df_bancos, df_empregados, df_reclamacoes
