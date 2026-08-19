from pyspark.sql.functions import col, lpad, when, trim, regexp_replace, broadcast


def processar_bancos(spark, df_bancos_raw, df_aux_bcb):
    df = df_bancos_raw.withColumn("CNPJ", lpad(col("CNPJ"), 8, "0"))
    df = df.withColumn("nome_quebrado", col("Nome").contains("\ufffd"))
    df = df.join(broadcast(df_aux_bcb), on="CNPJ", how="left")
    df = df.withColumn(
        "Nome",
        when(col("nome_quebrado") & col("Nome_DePara").isNotNull(), col("Nome_DePara")).otherwise(col("Nome"))
    )
    df = df.fillna({"Nome": "NAO_INFORMADO", "Segmento": "NAO_INFORMADO"})
    return df.drop("nome_quebrado", "Nome_DePara")


def processar_empregados(spark, df_emp_raw):
    empresas_excluidas = ["Apex Group", "J.P. Morgan", "Votorantim"]
    df = df_emp_raw.filter(~col("employer_name").isin(empresas_excluidas))
    return df.fillna({"employer-founded": "NAO_INFORMADO"})


def processar_reclamacoes(spark, df_rec_raw):
    df = df_rec_raw
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


def processar_trusted(spark, df_bancos_raw, df_emp_raw, df_rec_raw, df_aux_bcb):
    df_bancos_tr = processar_bancos(spark, df_bancos_raw, df_aux_bcb)
    df_emp_tr = processar_empregados(spark, df_emp_raw)
    df_rec_tr = processar_reclamacoes(spark, df_rec_raw)
    return df_bancos_tr, df_emp_tr, df_rec_tr
