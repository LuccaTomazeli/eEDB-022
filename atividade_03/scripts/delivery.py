from pyspark.sql.functions import col, trim, regexp_replace, sum as _sum, avg, count, coalesce


def processar_delivery(spark, bancos, empregados, reclamacoes):
    bancos = bancos.withColumn("nome_join", trim(regexp_replace(col("Nome"), " - PRUDENCIAL", "")))
    empregados = empregados.withColumn("nome_join", trim(col("Nome")))

    colunas_glassdoor = [
        "nome_join", "employer_name", "Geral", "Cultura e valores",
        "Diversidade e inclusão", "Qualidade de vida", "Alta liderança",
        "Remuneração e benefícios", "Oportunidades de carreira",
        "reviews_count", "match_percent"
    ]
    empregados_sub = empregados.select(*colunas_glassdoor)
    df = bancos.join(empregados_sub, on="nome_join", how="left")

    reclamacoes_ind = reclamacoes.filter(col("Tipo") == "Banco/financeira")
    reclamacoes_ind = reclamacoes_ind.withColumn("qtd_reclamacoes_num", col("Quantidade total de reclamações").cast("double"))

    agregado_ind = reclamacoes_ind.groupBy("CNPJ IF").agg(
        _sum("qtd_reclamacoes_num").alias("total_reclamacoes"),
        avg("Índice").alias("indice_medio"),
        count("Trimestre").alias("trimestres_com_reclamacao")
    ).withColumnRenamed("CNPJ IF", "CNPJ")

    reclamacoes_cong = reclamacoes.filter(col("Tipo") == "Conglomerado")
    reclamacoes_cong = reclamacoes_cong.withColumn("nome_join", trim(regexp_replace(col("Instituição financeira"), "\\s*\\(conglomerado\\)", "")))
    reclamacoes_cong = reclamacoes_cong.withColumn("qtd_reclamacoes_num", col("Quantidade total de reclamações").cast("double"))

    agregado_cong = reclamacoes_cong.groupBy("nome_join").agg(
        _sum("qtd_reclamacoes_num").alias("total_reclamacoes_cong"),
        avg("Índice").alias("indice_medio_cong"),
        count("Trimestre").alias("trimestres_com_reclamacao_cong")
    )

    df = df.join(agregado_ind, on="CNPJ", how="left")
    df = df.join(agregado_cong, on="nome_join", how="left")

    df = df.withColumn("total_reclamacoes", coalesce(col("total_reclamacoes"), col("total_reclamacoes_cong")))
    df = df.withColumn("indice_medio", coalesce(col("indice_medio"), col("indice_medio_cong")))
    df = df.withColumn("trimestres_com_reclamacao", coalesce(col("trimestres_com_reclamacao"), col("trimestres_com_reclamacao_cong")))
    return df.drop("total_reclamacoes_cong", "indice_medio_cong", "trimestres_com_reclamacao_cong", "nome_join")
