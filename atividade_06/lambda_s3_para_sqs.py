"""Lambda produtora: lê objetos do bucket de origem e publica-os na SQS."""

import json
import os
from typing import Any
from urllib.parse import unquote_plus

import boto3

s3 = boto3.client("s3")
sqs = boto3.client("sqs")
QUEUE_URL = os.environ["QUEUE_URL"]


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Processa eventos do S3 e publica uma mensagem por objeto na SQS."""
    messages = []

    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])
        obj = s3.get_object(Bucket=bucket, Key=key)
        response = sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(
                {
                    "bucket": bucket,
                    "key": key,
                    "content_type": obj.get("ContentType"),
                },
                ensure_ascii=False,
            ),
        )
        messages.append({"key": key, "message_id": response["MessageId"]})

    return {"published": len(messages), "messages": messages}
