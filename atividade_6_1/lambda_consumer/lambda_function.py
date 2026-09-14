import json
import os

import pymysql


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
            connect_timeout=int(os.environ.get("SQL_CONNECT_TIMEOUT", "5")),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    return connection


def lambda_handler(event, context):
    records = event.get("Records", []) if isinstance(event, dict) else []
    if not records:
        return {"batchItemFailures": [], "recordsProcessed": 0}

    database_connection = get_connection()
    failures = []
    processed = 0

    with database_connection.cursor() as cursor:
        for record in records:
            message_id = record.get("messageId")
            try:
                payload = json.loads(record["body"])
                client_id = payload["id"]
                cursor.execute(
                    "SELECT id, nome, email FROM clientes WHERE id = %s",
                    (client_id,),
                )
                result = cursor.fetchone()
                print(json.dumps({"messageId": message_id, "client": result}, ensure_ascii=False))
                processed += 1
            except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
                print(json.dumps({"messageId": message_id, "error": str(error)}, ensure_ascii=False))
                if message_id:
                    failures.append({"itemIdentifier": message_id})

    return {
        "batchItemFailures": failures,
        "recordsProcessed": processed,
        "recordsFailed": len(failures),
    }
