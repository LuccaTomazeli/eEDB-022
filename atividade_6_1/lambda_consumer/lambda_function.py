import json
import os
from datetime import datetime, timezone

import boto3
import pymysql
from enrichment import refresh


s3 = boto3.client("s3")
connection = None


def get_connection():
    global connection
    if connection is None or not connection.open:
        connection = pymysql.connect(
            host=os.environ["SQL_HOST"],
            port=int(os.environ.get("SQL_PORT", "3306")),
            user=os.environ["SQL_USER"],
            password=os.environ["SQL_PASSWORD"],
            database=os.environ["SQL_DATABASE"],
            connect_timeout=10,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )
    return connection


def ensure_schema(cursor):
    for table, key in (("bancos", "origem"), ("empregados", "origem"), ("reclamacoes", "origem")):
        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table} (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            arquivo_origem VARCHAR(255) NOT NULL,
            linha_origem INT NOT NULL,
            dados JSON NOT NULL,
            criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY uq_{table}_origem (arquivo_origem, linha_origem)
        )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS dados_enriquecidos (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        banco_id BIGINT NOT NULL,
        cnpj VARCHAR(30), nome_original VARCHAR(255), nome_normalizado VARCHAR(255) NOT NULL,
        segmento VARCHAR(50), empregado_match JSON NOT NULL, reclamacoes_resumo JSON NOT NULL,
        total_reclamacoes INT NOT NULL DEFAULT 0, indice_medio DECIMAL(12,2),
        nota_media_empregados DECIMAL(5,2), dados_tratados JSON NOT NULL,
        enriquecido_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE KEY uq_dados_enriquecidos_banco (banco_id)
    )""")


def persist_record(cursor, payload):
    table_name = payload.get("tabela_origem")
    if table_name not in {"bancos", "empregados", "reclamacoes"}:
        raise ValueError(f"Tabela de origem invalida: {table_name}")
    cursor.execute(
        f"""INSERT INTO {table_name} (arquivo_origem, linha_origem, dados)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id), dados = VALUES(dados)""",
        (payload.get("arquivo_origem"), payload.get("linha_origem"), json.dumps(payload.get("dados", {}), ensure_ascii=False)),
    )
    record_id = cursor.lastrowid
    cursor.execute(f"SELECT id, arquivo_origem, linha_origem, dados, criado_em FROM {table_name} WHERE id = %s", (record_id,))
    return table_name, record_id, cursor.fetchone()


def lambda_handler(event, context):
    records = event.get("Records", []) if isinstance(event, dict) else []
    if not records:
        return {"batchItemFailures": [], "recordsProcessed": 0}
    database_connection = get_connection()
    bucket = os.environ["S3_BUCKET"]
    prefix = os.environ.get("S3_OUTPUT_PREFIX", "processados").strip("/")
    failures = []
    processed = 0
    with database_connection.cursor() as cursor:
        ensure_schema(cursor)
        for record in records:
            message_id = record.get("messageId")
            try:
                payload = json.loads(record["body"])
                table_name, record_id, inserted = persist_record(cursor, payload)
                output_key = f"{prefix}/{table_name}/{record_id}/{message_id or record_id}.json"
                output = {"mensagem_original": payload, "registro_inserido": inserted, "processamento": {"message_id": message_id, "processado_em": datetime.now(timezone.utc).isoformat(), "status": "persistido"}}
                s3.put_object(Bucket=bucket, Key=output_key, Body=json.dumps(output, ensure_ascii=False, default=str).encode("utf-8"), ContentType="application/json")
                processed += 1
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                print(json.dumps({"messageId": message_id, "error": str(error)}, ensure_ascii=False))
                if message_id:
                    failures.append({"itemIdentifier": message_id})
        if processed and not failures:
            export = refresh(cursor)
            enriched_key = os.environ.get("S3_ENRICHED_KEY", "enriquecidos/dados_enriquecidos.json")
            export["processado_em"] = datetime.now(timezone.utc).isoformat()
            s3.put_object(Bucket=bucket, Key=enriched_key, Body=json.dumps(export, ensure_ascii=False, default=str).encode("utf-8"), ContentType="application/json")
    return {"batchItemFailures": failures, "recordsProcessed": processed, "recordsFailed": len(failures)}
