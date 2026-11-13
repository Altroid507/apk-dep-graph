"""Точка входа CLI (этап 2: конфигурация + прямые зависимости)."""

import argparse
import sys
from pathlib import Path

from apk_parser import direct_dependencies
from config import Config, dump_config, load_config
from errors import ConfigError, PackageNotFoundError, RepositoryError


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


def _run_stage2(config: Config) -> None:
    """Этап 2: вывести прямые зависимости пакета."""
    direct = direct_dependencies(
        config.repository, config.package, config.package_version
    )
    print("== Прямые зависимости ==")
    for dep in direct:
        print(dep)


def main(argv: list[str] | None = None) -> int:
    """Точка входа программы."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    _print_config(config)

    try:
        _run_stage2(config)
    except (RepositoryError, PackageNotFoundError) as exc:
        print(f"Ошибка репозитория: {exc}", file=sys.stderr)
        return 1
    return 0