import csv
import json
import re
import sys
from pathlib import Path


DATA_ROOT = Path(__file__).resolve().parents[1] / "Dados"
OUTPUT_ROOT = Path(__file__).resolve().parents[1] / "dados_json"
TABLE_BY_FOLDER = {
    "Bancos": "bancos",
    "Empregados": "empregados",
    "Reclamações": "reclamacoes",
}


def read_text(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise UnicodeError(f"Nao foi possivel decodificar {path}")


def detect_delimiter(path, text):
    if path.suffix.lower() == ".tsv":
        return "\t"
    header = text.splitlines()[0] if text.splitlines() else ""
    return "|" if header.count("|") > header.count(";") else ";"


def normalize_key(key):
    return re.sub(r"\s+", " ", key.strip())


def convert_file(source_path, table_name):
    text = read_text(source_path)
    reader = csv.DictReader(text.splitlines(), delimiter=detect_delimiter(source_path, text))
    if not reader.fieldnames:
        raise ValueError(f"Arquivo sem cabecalho: {source_path}")

    records = []
    for row_number, row in enumerate(reader, start=2):
        data = {
            normalize_key(key): (value.strip() if value is not None else None)
            for key, value in row.items()
            if key is not None and normalize_key(key)
        }
        records.append(
            {
                "tabela_origem": table_name,
                "arquivo_origem": source_path.name,
                "linha_origem": row_number,
                "dados": data,
            }
        )

    output_path = OUTPUT_ROOT / table_name / f"{source_path.stem}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path, len(records)


def main():
    if not DATA_ROOT.exists():
        raise FileNotFoundError(f"Pasta de dados nao encontrada: {DATA_ROOT}")

    total = 0
    for source_path in sorted(DATA_ROOT.rglob("*")):
        if not source_path.is_file() or source_path.suffix.lower() not in {".csv", ".tsv"}:
            continue
        table_name = TABLE_BY_FOLDER.get(source_path.parent.name)
        if table_name is None:
            raise ValueError(f"Pasta de dados desconhecida: {source_path.parent.name}")
        output_path, count = convert_file(source_path, table_name)
        total += count
        print(f"{source_path} -> {output_path} ({count} registros)")

    print(f"Total convertido: {total} registros")


if __name__ == "__main__":
    try:
        main()
    except (FileNotFoundError, UnicodeError, ValueError) as error:
        print(f"Erro: {error}", file=sys.stderr)
        raise SystemExit(1)
