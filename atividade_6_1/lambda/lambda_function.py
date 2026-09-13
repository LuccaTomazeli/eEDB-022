import json
import os
from urllib.parse import unquote_plus

import boto3


s3 = boto3.client("s3")
sqs = boto3.client("sqs")


def lambda_handler(event, context):
    bucket = os.environ["S3_BUCKET"]
    key = os.environ["S3_KEY"]
    queue_url = os.environ["SQS_QUEUE_URL"]

    s3_records = event.get("Records", []) if isinstance(event, dict) else []
    if s3_records and s3_records[0].get("eventSource") == "aws:s3":
        s3_object = s3_records[0]["s3"]
        bucket = s3_object["bucket"]["name"]
        key = unquote_plus(s3_object["object"]["key"])

    response = s3.get_object(Bucket=bucket, Key=key)
    content = response["Body"].read().decode("utf-8")
    records = json.loads(content)

    if not isinstance(records, list):
        raise ValueError("O arquivo S3 deve conter uma lista JSON de registros")

    for record in records:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(record, ensure_ascii=False),
        )

    return {
        "statusCode": 200,
        "recordsSent": len(records),
        "body": f"{len(records)} registros enviados para SQS",
    }