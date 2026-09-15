import json
import os
import re
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import boto3
import pymysql


DEFAULT_BUCKET = "atividade-6-1-115651887176"
OUTPUT_KEY = os.environ.get("S3_ENRICHED_KEY", "enriquecidos/dados_enriquecidos.json")


def load_env_file():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def normalize_text(value):
    text = str(value or "").strip().upper()
    return "".join(
        character
        for character in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(character)
    )


def digits(value):
    return re.sub(r"\D", "", str(value or ""))


def number(value):
    text = str(value or "").strip().replace("%", "")
    if not text:
        return None
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(Decimal(text))
    except InvalidOperation:
        return None


def json_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime,)):
        return value.isoformat()
    return value


def row_data(row):
    value = row["dados"]
    return json.loads(value) if isinstance(value, str) else value


def connect():
    return pymysql.connect(
        host=os.environ["SQL_HOST"],
        port=int(os.environ.get("SQL_PORT", "3306")),
        user=os.environ["SQL_USER"],
        password=os.environ["SQL_PASSWORD"],
        database=os.environ["SQL_DATABASE"],
        connect_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def main():
    load_env_file()
    os.environ.setdefault("S3_BUCKET", DEFAULT_BUCKET)
    required = ("SQL_HOST", "SQL_USER", "SQL_PASSWORD", "SQL_DATABASE")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        raise SystemExit(f"Variaveis ausentes: {', '.join(missing)}")

    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS dados_enriquecidos (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    banco_id BIGINT NOT NULL,
                    cnpj VARCHAR(30),
                    nome_original VARCHAR(255),
                    nome_normalizado VARCHAR(255) NOT NULL,
                    segmento VARCHAR(50),
                    empregado_match JSON NOT NULL,
                    reclamacoes_resumo JSON NOT NULL,
                    total_reclamacoes INT NOT NULL DEFAULT 0,
                    indice_medio DECIMAL(12, 2),
                    nota_media_empregados DECIMAL(5, 2),
                    dados_tratados JSON NOT NULL,
                    enriquecido_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uq_dados_enriquecidos_banco (banco_id)
                )"""
            )
            cursor.execute("SELECT id, dados FROM bancos ORDER BY id")
            bancos = cursor.fetchall()
            cursor.execute("SELECT id, dados FROM empregados")
            empregados = cursor.fetchall()
            cursor.execute("SELECT id, dados FROM reclamacoes")
            reclamacoes = cursor.fetchall()

            empregados_index = {}
            for row in empregados:
                data = row_data(row)
                key = normalize_text(data.get("Nome") or data.get("employer_name"))
                if key:
                    empregados_index.setdefault(key, []).append(
                        {"id": row["id"], "dados": data}
                    )

            reclamacoes_index = {}
            for row in reclamacoes:
                data = row_data(row)
                key = normalize_text(data.get("Instituição financeira"))
                cnpj = digits(data.get("CNPJ IF"))
                if key:
                    reclamacoes_index.setdefault(("nome", key), []).append(data)
                if cnpj:
                    reclamacoes_index.setdefault(("cnpj", cnpj), []).append(data)

            enriched = []
            for banco in bancos:
                data = row_data(banco)
                name = data.get("Nome", "")
                normalized_name = normalize_text(name)
                cnpj = digits(data.get("CNPJ"))
                employee_matches = empregados_index.get(normalized_name, [])
                complaint_matches = reclamacoes_index.get(("cnpj", cnpj), []) if cnpj else []
                if not complaint_matches:
                    complaint_matches = reclamacoes_index.get(
                        ("nome", normalized_name), []
                    )

                complaint_values = [
                    number(item.get("Quantidade total de reclamações"))
                    for item in complaint_matches
                ]
                complaint_values = [value for value in complaint_values if value is not None]
                indices = [
                    number(item.get("Índice"))
                    for item in complaint_matches
                ]
                indices = [value for value in indices if value is not None]
                employee_ratings = [
                    number(item["dados"].get("Geral")) for item in employee_matches
                ]
                employee_ratings = [value for value in employee_ratings if value is not None]
                employee_payload = [
                    {"id": item["id"], "dados": item["dados"]}
                    for item in employee_matches
                ]
                complaint_summary = {
                    "quantidade_registros": len(complaint_matches),
                    "total_reclamacoes": int(sum(complaint_values)),
                    "indice_medio": round(sum(indices) / len(indices), 2) if indices else None,
                }
                treated = {
                    "banco_id": banco["id"],
                    "cnpj": cnpj or None,
                    "nome": str(name).strip(),
                    "nome_normalizado": normalized_name,
                    "segmento": str(data.get("Segmento", "")).strip() or None,
                    "tem_dados_empregados": bool(employee_matches),
                    "tem_dados_reclamacoes": bool(complaint_matches),
                }
                cursor.execute(
                    """INSERT INTO dados_enriquecidos (
                        banco_id, cnpj, nome_original, nome_normalizado, segmento,
                        empregado_match, reclamacoes_resumo, total_reclamacoes,
                        indice_medio, nota_media_empregados, dados_tratados
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        cnpj = VALUES(cnpj), nome_original = VALUES(nome_original),
                        nome_normalizado = VALUES(nome_normalizado), segmento = VALUES(segmento),
                        empregado_match = VALUES(empregado_match),
                        reclamacoes_resumo = VALUES(reclamacoes_resumo),
                        total_reclamacoes = VALUES(total_reclamacoes),
                        indice_medio = VALUES(indice_medio),
                        nota_media_empregados = VALUES(nota_media_empregados),
                        dados_tratados = VALUES(dados_tratados),
                        enriquecido_em = CURRENT_TIMESTAMP""",
                    (
                        banco["id"], cnpj or None, str(name).strip(), normalized_name,
                        treated["segmento"], json.dumps(employee_payload, ensure_ascii=False),
                        json.dumps(complaint_summary, ensure_ascii=False),
                        complaint_summary["total_reclamacoes"], complaint_summary["indice_medio"],
                        round(sum(employee_ratings) / len(employee_ratings), 2)
                        if employee_ratings else None,
                        json.dumps(treated, ensure_ascii=False),
                    ),
                )
                enriched.append({
                    **treated,
                    "empregados": employee_payload,
                    "reclamacoes": complaint_summary,
                    "nota_media_empregados": round(sum(employee_ratings) / len(employee_ratings), 2)
                    if employee_ratings else None,
                })

            export = {
                "tabela": "dados_enriquecidos",
                "gerado_em": datetime.now(timezone.utc).isoformat(),
                "total_registros": len(enriched),
                "registros": enriched,
            }
            s3 = boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
            s3.put_object(
                Bucket=os.environ["S3_BUCKET"],
                Key=OUTPUT_KEY,
                Body=json.dumps(export, ensure_ascii=False, default=json_value).encode("utf-8"),
                ContentType="application/json",
            )
            print(json.dumps({
                "tabela": "dados_enriquecidos",
                "registros": len(enriched),
                "s3": f"s3://{os.environ['S3_BUCKET']}/{OUTPUT_KEY}",
            }, ensure_ascii=False))
    finally:
        connection.close()


if __name__ == "__main__":
    main()
