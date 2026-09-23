"""Read and delete one message from the configured SQS queue."""

import argparse
import os

import boto3


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue-url", default=os.environ.get("SQS_QUEUE_URL"))
    parser.add_argument("--queue-name", default="atividade-6-1-fila")
    args = parser.parse_args()
    if not args.queue_url:
        sqs = boto3.client("sqs", region_name=os.environ.get("AWS_DEFAULT_REGION"))
        args.queue_url = sqs.get_queue_url(QueueName=args.queue_name)["QueueUrl"]

    sqs = boto3.client("sqs", region_name=os.environ.get("AWS_DEFAULT_REGION"))
    response = sqs.receive_message(
        QueueUrl=args.queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=5,
    )
    messages = response.get("Messages", [])
    if not messages:
        print("Nenhuma mensagem encontrada.")
        return

    message = messages[0]
    print(message["Body"])
    sqs.delete_message(
        QueueUrl=args.queue_url,
        ReceiptHandle=message["ReceiptHandle"],
    )
    print("Mensagem removida da fila.")


if __name__ == "__main__":
    main()
