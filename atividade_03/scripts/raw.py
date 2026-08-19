import json
import glob


def processar_raw_bancos(spark):
    return spark.read.option("header", "true").option("delimiter", "\t").csv("../Dados/Bancos/EnquadramentoInicia_v2.tsv")


def processar_raw_empregados(spark):
    return spark.read.option("header", "true").option("delimiter", "|").csv("../Dados/Empregados/glassdoor_consolidado_join_match_v2.csv")


def processar_raw_reclamacoes(spark):
    arquivos = sorted(glob.glob("../Dados/Reclamacoes/*.csv"))
    arquivos = [a for a in arquivos if "nao_ha_dados" not in a]
    df = spark.read.option("header", "true").option("delimiter", ";").option("encoding", "latin1").csv(arquivos)
    colunas_validas = [c for c in df.columns if not c.startswith("Unnamed")]
    return df.select(colunas_validas)


def processar_raw_aux_bcb(spark):
    with open("volume/raw/tb_aux_bcb.json", encoding="utf-8") as f:
        depara_dict = json.load(f)
    depara_data = [(k, v) for k, v in depara_dict.items()]
    return spark.createDataFrame(depara_data, ["CNPJ", "Nome_DePara"])


def processar_raw(spark):
    df_bancos = processar_raw_bancos(spark)
    df_empregados = processar_raw_empregados(spark)
    df_reclamacoes = processar_raw_reclamacoes(spark)
    df_aux_bcb = processar_raw_aux_bcb(spark)
    return df_bancos, df_empregados, df_reclamacoes, df_aux_bcb
