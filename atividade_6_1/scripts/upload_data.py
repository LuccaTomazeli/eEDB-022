"""Upload converted JSON files to the configured S3 input prefix."""

import argparse
import os
from pathlib import Path

import boto3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="dados_json", type=Path)
    parser.add_argument("--prefix", default="entrada")
    parser.add_argument("--bucket", default=os.environ.get("S3_BUCKET"))
    args = parser.parse_args()

    if not args.bucket:
        account_id = boto3.client("sts").get_caller_identity()["Account"]
        args.bucket = f"atividade-6-1-{account_id}"
    if not args.directory.is_dir():
        raise SystemExit(f"Diretorio nao encontrado: {args.directory}")

    s3 = boto3.client("s3", region_name=os.environ.get("AWS_DEFAULT_REGION"))
    uploaded = 0
    for path in sorted(args.directory.rglob("*.json")):
        key = f"{args.prefix.strip('/')}/{path.relative_to(args.directory).as_posix()}"
        s3.upload_file(str(path), args.bucket, key)
        uploaded += 1
        print(f"Enviado: s3://{args.bucket}/{key}")
    print(f"Total enviado: {uploaded}")


if __name__ == "__main__":
    main()
