"""Publica os envelopes JSON locais em um tópico Kafka."""

import argparse
import json
import time
from pathlib import Path

from kafka import KafkaProducer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Produtor Kafka da Atividade 8")
    parser.add_argument("--data-dir", default="dados_json", help="Diretório das fontes JSON")
    parser.add_argument("--bootstrap", default="localhost:9092")
    parser.add_argument("--topic", default="dados-brutos")
    parser.add_argument("--delay", type=float, default=0.05)
    parser.add_argument("--limit", type=int, default=0, help="Limita mensagens; 0 publica todas")
    return parser.parse_args()


def iter_records(data_dir: Path):
    for source in sorted(data_dir.rglob("*.json")):
        with source.open(encoding="utf-8") as file:
            records = json.load(file)
        for record in records:
            yield record


def main() -> None:
    args = parse_args()
    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap,
        value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
        retries=5,
    )
    sent = 0
    try:
        for record in iter_records(Path(args.data_dir)):
            producer.send(args.topic, value=record)
            sent += 1
            if sent % 100 == 0:
                producer.flush()
            if args.delay:
                time.sleep(args.delay)
            if args.limit and sent >= args.limit:
                break
        producer.flush()
    finally:
        producer.close()
    print(f"Mensagens publicadas: {sent}")


if __name__ == "__main__":
    main()