from pyspark.sql import SparkSession

JDBC_JAR = "jars/postgresql-42.7.4.jar"

PG_URL = "jdbc:postgresql://localhost:5433/eedb022_a4"
PG_PROPS = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

DADOS_DIR = "../Dados"

spark = SparkSession.builder \
    .appName("ingestao_raw_atividade4") \
    .config("spark.jars", JDBC_JAR) \
    .getOrCreate()

print("Lendo reclamações...")
trimestres = [
    "2021_tri_01.csv", "2021_tri_02.csv", "2021_tri_03.csv", "2021_tri_04.csv",
    "2022_tri_01.csv", "2022_tri_03.csv", "2022_tri_04.csv"
]
caminhos = [f"{DADOS_DIR}/Reclamacoes/{arquivo}" for arquivo in trimestres]

df_reclamacoes = spark.read.csv(
    caminhos,
    sep=";",
    encoding="ISO-8859-1",
    header=True,
    inferSchema=True
)
print(f"Reclamações: {df_reclamacoes.count()} linhas")

print("Lendo bancos (Enquadramento)...")
df_bancos = spark.read.csv(
    f"{DADOS_DIR}/Bancos/EnquadramentoInicia_v2.tsv",
    sep="\t",
    encoding="ISO-8859-1",
    header=True,
    inferSchema=True
)
print(f"Bancos: {df_bancos.count()} linhas")

print("Lendo Glassdoor...")
df_glassdoor = spark.read.csv(
    f"{DADOS_DIR}/Empregados/glassdoor_consolidado_join_match_v2.csv",
    sep="|",
    header=True,
    inferSchema=True
)
print(f"Glassdoor: {df_glassdoor.count()} linhas")

print("Escrevendo no Postgres (schema raw)...")
df_reclamacoes.write.jdbc(PG_URL, "raw.reclamacoes", mode="overwrite", properties=PG_PROPS)
df_bancos.write.jdbc(PG_URL, "raw.bancos", mode="overwrite", properties=PG_PROPS)
df_glassdoor.write.jdbc(PG_URL, "raw.empregados", mode="overwrite", properties=PG_PROPS)

print("Ingestão RAW concluída!")
spark.stop()