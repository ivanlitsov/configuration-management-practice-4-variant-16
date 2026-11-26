"""Интерфейс командной строки для преобразования конфигураций в JSON."""

import argparse
import json
from pathlib import Path
import sys

from parser import parse_config


def convert(text, destination):
    """Преобразует конфигурацию и записывает JSON в UTF-8."""
    value = parse_config(text)
    output = json.dumps(value, ensure_ascii=False, indent=2)
    destination.write_bytes((output + "\n").encode("utf-8"))


def main():
    """Читает стандартный ввод и сохраняет результат по указанному пути."""
    cli = argparse.ArgumentParser(description="Перевод конфигурации в JSON")
    cli.add_argument("-o", "--output", type=Path, required=True,
                     help="путь к выходному JSON")
    args = cli.parse_args()
    try:
        text = sys.stdin.buffer.read().decode("utf-8-sig")
        convert(text, args.output)
    except (ValueError, OSError) as error:
        cli.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
