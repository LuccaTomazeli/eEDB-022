"""Consumidor PySpark Structured Streaming com enriquecimento JDBC."""

import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import coalesce, col, current_timestamp, lower, regexp_replace, trim


def normalize(value):
    return regexp_replace(
        lower(trim(value)),
        r"[^a-z0-9]",
        "",
    )


def create_spark() -> SparkSession:
    return SparkSession.builder.appName("atividade8-enriquecimento").getOrCreate()


def read_lookup(spark: SparkSession) -> DataFrame:
    return (
        spark.read.format("jdbc")
        .option("url", os.getenv("JDBC_URL", "jdbc:postgresql://postgres:5432/atividade8"))
        .option("dbtable", "banco_enquadramento")
        .option("user", os.getenv("POSTGRES_USER", "atividade8"))
        .option("password", os.getenv("POSTGRES_PASSWORD", "atividade8"))
        .option("driver", "org.postgresql.Driver")
        .load()
    )


def enrich_batch(batch: DataFrame, batch_id: int) -> None:
    if batch.rdd.isEmpty():
        return
    spark = batch.sparkSession
    lookup = read_lookup(spark).select(
        col("cnpj").alias("lookup_cnpj"),
        col("nome").alias("banco_nome"),
        col("segmento"),
        col("nome_normalizado").alias("lookup_nome_normalizado"),
    )
    data = batch.select("payload", "kafka_timestamp", "kafka_partition", "kafka_offset")
    enriched = (
        data.withColumn(
            "cnpj_chave",
            regexp_replace(
                coalesce(col("payload").getItem("CNPJ IF"), col("payload").getItem("CNPJ")),
                r"\\D",
                "",
            ),
        )
        .withColumn(
            "nome_chave",
            normalize(
                coalesce(
                    col("payload").getItem("Instituição financeira"),
                    col("payload").getItem("Nome"),
                )
            ),
        )
        .join(
            lookup,
            (col("cnpj_chave") == col("lookup_cnpj"))
            | (col("nome_chave") == col("lookup_nome_normalizado")),
            "left",
        )
        .withColumn("enriquecido", col("lookup_cnpj").isNotNull() | col("lookup_nome_normalizado").isNotNull())
        .withColumn("processado_em", current_timestamp())
        .drop("cnpj_chave", "nome_chave", "lookup_cnpj", "lookup_nome_normalizado")
    )
    (
        enriched.write.mode("append")
        .partitionBy("enriquecido")
        .json(os.getenv("OUTPUT_DIR", "/opt/atividade8/saida/enriquecido"))
    )


def main() -> None:
    spark = create_spark()
    spark.sparkContext.setLogLevel(os.getenv("SPARK_LOG_LEVEL", "WARN"))
    stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", os.getenv("KAFKA_BOOTSTRAP", "kafka:29092"))
        .option("subscribe", os.getenv("KAFKA_TOPIC", "dados-brutos"))
        .option("startingOffsets", os.getenv("STARTING_OFFSETS", "earliest"))
        .load()
        .selectExpr("CAST(value AS STRING) AS json_value", "timestamp AS kafka_timestamp", "partition AS kafka_partition", "offset AS kafka_offset")
        .selectExpr("from_json(json_value, 'struct<tabela_origem:string,arquivo_origem:string,linha_origem:long,dados:map<string,string>>') AS envelope", "kafka_timestamp", "kafka_partition", "kafka_offset")
        .select(col("envelope.dados").alias("payload"), "kafka_timestamp", "kafka_partition", "kafka_offset")
    )
    query = (
        stream.writeStream.foreachBatch(enrich_batch)
        .option("checkpointLocation", os.getenv("CHECKPOINT_DIR", "/opt/atividade8/saida/checkpoint"))
        .trigger(processingTime=os.getenv("TRIGGER_INTERVAL", "10 seconds"))
        .start()
    )
    query.awaitTermination()


if __name__ == "__main__":
    main()