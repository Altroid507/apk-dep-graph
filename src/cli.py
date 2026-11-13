"""Точка входа CLI (этап 5: полный функционал)."""

import argparse
import sys
from pathlib import Path

from apk_parser import direct_dependencies
from ascii_tree import render_tree
from config import Config, dump_config, load_config
from errors import (
    ConfigError,
    GraphFileError,
    PackageNotFoundError,
    RepositoryError,
)
from graph import DependencyGraph
from traversal import bfs_recursive, reverse_dependencies
from visualizer import save_svg


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
    parser.add_argument(
        "--reverse",
        metavar="PACKAGE",
        help="Показать обратные зависимости для PACKAGE",
    )
    return parser


def _print_config(config: Config) -> None:
    """Вывести все параметры в формате ключ=значение."""
    print("== Конфигурация ==")
    for line in dump_config(config):
        print(line)


def _load_test_graph(config: Config) -> DependencyGraph:
    """Загрузить граф из локального текстового файла."""
    path = Path(config.repository)
    if not path.is_file():
        raise GraphFileError(f"Файл тестового графа не найден: {path}")
    graph = DependencyGraph()
    for lineno, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if " " not in line:
            raise GraphFileError(
                f"Строка {lineno}: ожидался формат 'A B'"
            )
        source, target = line.split(maxsplit=1)
        if not source.isupper() or not target.isupper():
            raise GraphFileError(
                f"Строка {lineno}: имена должны быть заглавными"
            )
        graph.add_edge(source, target)
    return graph


def _build_real_graph(config: Config) -> DependencyGraph:
    """Построить граф из реального apk-репозитория."""
    direct = direct_dependencies(
        config.repository, config.package, config.package_version
    )
    graph = DependencyGraph()
    graph.edges.setdefault(config.package, [])
    for dep in direct:
        graph.add_edge(config.package, dep)
    return graph


def _run_stage3(config: Config, graph: DependencyGraph) -> None:
    """Этап 3: вывести транзитивный граф зависимостей."""
    nodes = bfs_recursive(graph, config.package, config.max_depth)
    print("== Граф зависимостей ==")
    for node in nodes:
        deps = ", ".join(graph.neighbors(node)) or "-"
        print(f"{node}: {deps}")


def _run_stage4(
    config: Config, graph: DependencyGraph, target: str
) -> None:
    """Этап 4: вывести обратные зависимости."""
    reverse = reverse_dependencies(graph, target, config.max_depth)
    print(f"== Обратные зависимости {target} ==")
    for node in reverse:
        print(node)


def _run_stage5(config: Config, graph: DependencyGraph) -> None:
    """Этап 5: сохранить SVG и, опционально, ASCII-дерево."""
    save_svg(graph, Path(config.output_image))
    print(f"SVG сохранён в {config.output_image}")
    if config.ascii_tree:
        print("== ASCII-дерево ==")
        print(render_tree(graph, config.package, config.max_depth))


def main(argv: list[str] | None = None) -> int:
    """Точка входа программы."""
    args = _build_parser().parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    _print_config(config)

    if config.test_mode:
        try:
            graph = _load_test_graph(config)
        except GraphFileError as exc:
            print(f"Ошибка графа: {exc}", file=sys.stderr)
            return 1
        _run_stage3(config, graph)
        if args.reverse:
            _run_stage4(config, graph, args.reverse)
        _run_stage5(config, graph)
        return 0

    try:
        graph = _build_real_graph(config)
    except (RepositoryError, PackageNotFoundError) as exc:
        print(f"Ошибка репозитория: {exc}", file=sys.stderr)
        return 1
    _run_stage3(config, graph)
    if args.reverse:
        _run_stage4(config, graph, args.reverse)
    _run_stage5(config, graph)
    return 0