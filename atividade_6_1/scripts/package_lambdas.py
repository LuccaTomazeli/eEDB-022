"""Build Lambda ZIP files in a platform-independent way."""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
CONSUMER_BUILD = BUILD / "consumer"
CONSUMER_SOURCE = ROOT / "lambda_consumer"


def copy_python_sources(destination: Path) -> None:
    for source in CONSUMER_SOURCE.glob("*.py"):
        shutil.copy2(source, destination / source.name)


def zip_directory(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in source.rglob("*"):
            if file_path.is_file():
                archive.write(file_path, file_path.relative_to(source))


def main() -> None:
    if not CONSUMER_SOURCE.exists():
        raise SystemExit(f"Diretorio ausente: {CONSUMER_SOURCE}")

    if BUILD.exists():
        shutil.rmtree(BUILD)
    CONSUMER_BUILD.mkdir(parents=True)

    requirements = CONSUMER_SOURCE / "requirements.txt"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-compile",
            "--target",
            str(CONSUMER_BUILD),
            "--platform",
            "manylinux2014_x86_64",
            "--implementation",
            "cp",
            "--python-version",
            "3.12",
            "--only-binary=:all:",
            "--requirement",
            str(requirements),
        ],
        check=True,
    )
    copy_python_sources(CONSUMER_BUILD)
    zip_directory(CONSUMER_BUILD, BUILD / "consumer-lambda.zip")
    print(f"Pacote criado: {BUILD / 'consumer-lambda.zip'}")


if __name__ == "__main__":
    main()
