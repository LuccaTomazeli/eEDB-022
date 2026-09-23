import json
import re
import unicodedata
from decimal import Decimal, InvalidOperation


SOURCE_TABLES = ("bancos", "empregados", "reclamacoes")


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


def row_data(row):
    value = row["dados"]
    return json.loads(value) if isinstance(value, str) else value


def ensure_table(cursor):
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


def refresh(cursor):
    ensure_table(cursor)
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
            empregados_index.setdefault(key, []).append({"id": row["id"], "dados": data})

    reclamacoes_index = {}
    for row in reclamacoes:
        data = row_data(row)
        name_key = normalize_text(data.get("Instituição financeira"))
        cnpj_key = digits(data.get("CNPJ IF"))
        if name_key:
            reclamacoes_index.setdefault(("nome", name_key), []).append(data)
        if cnpj_key:
            reclamacoes_index.setdefault(("cnpj", cnpj_key), []).append(data)

    enriched = []
    for banco in bancos:
        data = row_data(banco)
        name = str(data.get("Nome", "")).strip()
        normalized_name = normalize_text(name)
        cnpj = digits(data.get("CNPJ"))
        employee_matches = empregados_index.get(normalized_name, [])
        complaint_matches = reclamacoes_index.get(("cnpj", cnpj), []) if cnpj else []
        if not complaint_matches:
            complaint_matches = reclamacoes_index.get(("nome", normalized_name), [])

        complaint_values = [
            value for value in (number(item.get("Quantidade total de reclamações")) for item in complaint_matches)
            if value is not None
        ]
        indices = [
            value for value in (number(item.get("Índice")) for item in complaint_matches)
            if value is not None
        ]
        employee_ratings = [
            value for value in (number(item["dados"].get("Geral")) for item in employee_matches)
            if value is not None
        ]
        complaint_summary = {
            "quantidade_registros": len(complaint_matches),
            "total_reclamacoes": int(sum(complaint_values)),
            "indice_medio": round(sum(indices) / len(indices), 2) if indices else None,
        }
        employee_payload = [
            {"id": item["id"], "dados": item["dados"]} for item in employee_matches
        ]
        treated = {
            "banco_id": banco["id"],
            "cnpj": cnpj or None,
            "nome": name,
            "nome_normalizado": normalized_name,
            "segmento": str(data.get("Segmento", "")).strip() or None,
            "tem_dados_empregados": bool(employee_matches),
            "tem_dados_reclamacoes": bool(complaint_matches),
        }
        average_rating = round(sum(employee_ratings) / len(employee_ratings), 2) if employee_ratings else None
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
                banco["id"], cnpj or None, name, normalized_name, treated["segmento"],
                json.dumps(employee_payload, ensure_ascii=False),
                json.dumps(complaint_summary, ensure_ascii=False),
                complaint_summary["total_reclamacoes"], complaint_summary["indice_medio"],
                average_rating, json.dumps(treated, ensure_ascii=False),
            ),
        )
        enriched.append({
            **treated,
            "empregados": employee_payload,
            "reclamacoes": complaint_summary,
            "nota_media_empregados": average_rating,
        })

    return {
        "tabela": "dados_enriquecidos",
        "total_registros": len(enriched),
        "registros": enriched,
    }
