"""Точка входа CLI (этап 1 — только конфигурация)."""

import argparse
import sys
from pathlib import Path

from config import Config, dump_config, load_config
from errors import ConfigError


def _build_parser() -> argparse.ArgumentParser:
    """Создать argparse-парсер."""
    parser = argparse.ArgumentParser(
        prog="apk-dep-graph",
        description=(
            "Визуализатор графа зависимостей для Alpine Linux (apk)"
        ),
    )
    parser.add_argument(
        "--config",
        required=True,
        type=Path,
        help="Путь к CSV-файлу конфигурации",
    )
    return parser


def _print_config(config: Config) -> None:
    """Вывести все параметры в формате ключ=значение."""
    print("== Конфигурация ==")
    for line in dump_config(config):
        print(line)


def main(argv: list[str] | None = None) -> int:
    """Точка входа программы."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1
    _print_config(config)
    return 0