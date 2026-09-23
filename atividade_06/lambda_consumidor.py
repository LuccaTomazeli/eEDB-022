"""Lambda consumidora: recebe SQS, relê o objeto no S3 e grava no RDS."""

import json
import os
from typing import Any

import boto3

s3 = boto3.client("s3")
rds_data = boto3.client("rds-data")

RDS_CLUSTER_ARN = os.environ["RDS_CLUSTER_ARN"]
RDS_SECRET_ARN = os.environ["RDS_SECRET_ARN"]
RDS_DATABASE = os.environ["RDS_DATABASE"]
DESTINATION_BUCKET = os.environ.get("DESTINATION_BUCKET")


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Processa mensagens individualmente; falha a invocacao para reentrega SQS."""
    processed = 0

    for record in event.get("Records", []):
        message = json.loads(record["body"])
        bucket = message["bucket"]
        key = message["key"]
        content = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        payload = content.decode("utf-8")

        rds_data.execute_statement(
            resourceArn=RDS_CLUSTER_ARN,
            secretArn=RDS_SECRET_ARN,
            database=RDS_DATABASE,
            sql=(
                "INSERT INTO ingestao_raw (bucket_origem, chave_objeto, payload) "
                "VALUES (:bucket, :chave, :payload)"
            ),
            parameters=[
                {"name": "bucket", "value": {"stringValue": bucket}},
                {"name": "chave", "value": {"stringValue": key}},
                {"name": "payload", "value": {"stringValue": payload}},
            ],
        )

        if DESTINATION_BUCKET:
            destination_key = f"processed/{key}"
            s3.put_object(
                Bucket=DESTINATION_BUCKET,
                Key=destination_key,
                Body=content,
                ContentType=message.get("content_type") or "application/octet-stream",
            )

        processed += 1

    return {"processed": processed}
