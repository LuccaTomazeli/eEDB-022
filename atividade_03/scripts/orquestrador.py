import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from sqlalchemy import create_engine, text
from raw import processar_raw
from trusted import processar_trusted
from delivery import processar_delivery


def get_spark_session():
    spark = (
        SparkSession.builder.appName("PipelineAtividade03")
        .config("spark.driver.memory", "2g")
        .config("spark.jars.ivy", "/tmp/.ivy2")
        .config("spark.hadoop.user.name", "spark")
        .config("spark.driver.extraJavaOptions", "-Duser.name=spark")
        .config("spark.executor.extraJavaOptions", "-Duser.name=spark")
        .config("spark.jars.packages", "org.postgresql:postgresql:42.7.3")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def get_db_connection_info():
    db_host = os.getenv("DB_HOST", "postgres")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "banco_atividade_3")
    db_user = os.getenv("DB_USER", "root")
    db_pass = os.getenv("DB_PASSWORD", "root")
    url = f"jdbc:postgresql://{db_host}:{db_port}/{db_name}"
    conn_str = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return db_user, db_pass, url, conn_str


def criar_schemas():
    _, _, _, conn_str = get_db_connection_info()
    engine = create_engine(conn_str)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS trusted;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS delivery;"))
        conn.commit()


def carregar_tabela_pg(df, dbtable):
    db_user, db_pass, url, conn_str = get_db_connection_info()
    try:
        df.write.format("jdbc").option("url", url).option("dbtable", dbtable) \
            .option("user", db_user).option("password", db_pass) \
            .option("driver", "org.postgresql.Driver").mode("overwrite").save()
        print(f"Tabela '{dbtable}' criada no Postgres via JDBC: {df.count()} linhas")
    except Exception as e:
        print(f"Fallback para SQLAlchemy na tabela '{dbtable}' devido a: {e}")
        engine = create_engine(conn_str)
        schema, table_name = dbtable.split(".")
        df_pd = df.toPandas()
        df_pd.to_sql(table_name, engine, schema=schema, if_exists="replace", index=False)
        print(f"Tabela '{dbtable}' criada no Postgres via SQLAlchemy com {len(df_pd)} linhas")


def salvar_single_parquet(df, filepath):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.toPandas().to_parquet(filepath, index=False)


def main():
    spark = get_spark_session()
    try:
        print("Iniciando Orquestracao da Pipeline com PySpark...")
        criar_schemas()

        print("--- Executando Camada Raw ---")
        df_bancos_raw, df_emp_raw, df_rec_raw, df_aux_raw = processar_raw(spark)
        carregar_tabela_pg(df_bancos_raw, "raw.bancos")
        carregar_tabela_pg(df_emp_raw, "raw.empregados")
        carregar_tabela_pg(df_rec_raw, "raw.reclamacoes")
        carregar_tabela_pg(df_aux_raw, "raw.tb_aux_bcb")

        print("--- Executando Camada Trusted ---")
        df_bancos_tr, df_emp_tr, df_rec_tr = processar_trusted(spark)
        salvar_single_parquet(df_bancos_tr, "volume/trusted/bancos_trusted.parquet")
        salvar_single_parquet(df_emp_tr, "volume/trusted/empregados_trusted.parquet")
        salvar_single_parquet(df_rec_tr, "volume/trusted/reclamacoes_trusted.parquet")
        carregar_tabela_pg(df_bancos_tr, "trusted.bancos")
        carregar_tabela_pg(df_emp_tr, "trusted.empregados")
        carregar_tabela_pg(df_rec_tr, "trusted.reclamacoes")

        print("--- Executando Camada Delivery ---")
        df_delivery = processar_delivery(spark)
        salvar_single_parquet(df_delivery, "volume/delivery/delivery_bancos.parquet")
        carregar_tabela_pg(df_delivery, "delivery.bancos")

        print("Pipeline finalizada com sucesso!")
    except Exception as e:
        print(f"Erro na execucao da pipeline: {e}")
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
