import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError


def load_env():
    path = Path(__file__).resolve().parents[1] / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


def ensure_table(client, name, key):
    try:
        client.describe_table(TableName=name)
        print(f"Tabela DynamoDB pronta: {name}")
        return
    except client.exceptions.ResourceNotFoundException:
        pass
    client.create_table(
        TableName=name,
        KeySchema=[{"AttributeName": key, "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": key, "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    client.get_waiter("table_exists").wait(TableName=name)
    print(f"Tabela DynamoDB criada: {name}")


def main():
    load_env()
    account_id = boto3.client("sts").get_caller_identity()["Account"]
    prefix = os.environ.get("DDB_TABLE_PREFIX", f"atividade-6-1-{account_id}")
    client = boto3.client("dynamodb", region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"))
    for name in ("bancos", "empregados", "reclamacoes"):
        ensure_table(client, f"{prefix}-{name}", "origem_id")
    ensure_table(client, os.environ.get("DDB_ENRICHED_TABLE", f"{prefix}-dados-enriquecidos"), "banco_id")


if __name__ == "__main__":
    try:
        main()
    except ClientError as error:
        raise SystemExit(error)
