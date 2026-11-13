"""Загрузчик CSV-конфигурации.

Файл конфигурации — CSV с двумя столбцами ``key,value``.
Неизвестные ключи вызывают ``ConfigError``. Список допустимых
ключей — в ``KNOWN_KEYS``.
"""

import csv
from dataclasses import dataclass, field
from pathlib import Path

from errors import ConfigError

MIN_DEPTH = 1
MAX_DEPTH = 64
DEFAULT_DEPTH = 10
DEFAULT_IMAGE = "graph.svg"

KNOWN_KEYS = {
    "package",
    "repository",
    "test_mode",
    "package_version",
    "output_image",
    "ascii_tree",
    "max_depth",
}


@dataclass
class Config:
    """Пользовательская конфигурация."""

    package: str = ""
    repository: str = ""
    test_mode: bool = False
    package_version: str = ""
    output_image: str = DEFAULT_IMAGE
    ascii_tree: bool = False
    max_depth: int = DEFAULT_DEPTH
    raw: dict = field(default_factory=dict)


def _parse_bool(value: str, key: str) -> bool:
    """Разобрать булево значение из ячейки CSV."""
    lowered = value.strip().lower()
    if lowered in {"true", "1", "yes"}:
        return True
    if lowered in {"false", "0", "no"}:
        return False
    raise ConfigError(f"Некорректное булево значение '{key}': {value!r}")


def _parse_depth(value: str) -> int:
    """Разобрать max_depth (целое в диапазоне [MIN_DEPTH, MAX_DEPTH])."""
    try:
        depth = int(value)
    except ValueError as exc:
        raise ConfigError(
            f"max_depth должен быть целым: {value!r}"
        ) from exc
    if depth < MIN_DEPTH or depth > MAX_DEPTH:
        raise ConfigError(
            f"max_depth должен быть в [{MIN_DEPTH}, {MAX_DEPTH}], "
            f"получено {depth}"
        )
    return depth


def _require_file(path: Path) -> None:
    """Проверить существование файла."""
    if not path.is_file():
        raise ConfigError(f"Конфигурационный файл не найден: {path}")


def _read_rows(path: Path) -> dict[str, str]:
    """Прочитать CSV и вернуть словарь ключ → значение."""
    raw: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        for lineno, row in enumerate(reader, start=1):
            if not row or row[0].strip().startswith("#"):
                continue
            if len(row) != 2:
                raise ConfigError(
                    f"Строка {lineno}: ожидалось 2 столбца, "
                    f"получено {len(row)}"
                )
            key = row[0].strip()
            if key not in KNOWN_KEYS:
                raise ConfigError(
                    f"Строка {lineno}: неизвестный ключ '{key}'"
                )
            raw[key] = row[1].strip()
    return raw


def _build_config(raw: dict[str, str]) -> Config:
    """Собрать и провалидировать ``Config`` из сырых CSV-значений."""
    if not raw.get("package"):
        raise ConfigError("'package' не должен быть пустым")
    if not raw.get("repository"):
        raise ConfigError("'repository' не должен быть пустым")
    if not raw.get("package_version"):
        raise ConfigError("'package_version' не должен быть пустым")

    cfg = Config(raw=dict(raw))
    cfg.package = raw["package"]
    cfg.repository = raw["repository"]
    cfg.package_version = raw["package_version"]
    cfg.test_mode = _parse_bool(
        raw.get("test_mode", "false"), "test_mode"
    )
    cfg.ascii_tree = _parse_bool(
        raw.get("ascii_tree", "false"), "ascii_tree"
    )
    cfg.output_image = raw.get("output_image", DEFAULT_IMAGE)
    cfg.max_depth = _parse_depth(raw.get("max_depth", str(DEFAULT_DEPTH)))
    return cfg


def load_config(path: Path) -> Config:
    """Загрузить и провалидировать конфигурацию из CSV-файла."""
    _require_file(path)
    return _build_config(_read_rows(path))


def dump_config(cfg: Config) -> list[str]:
    """Вернуть строки ``key=value`` текущей конфигурации."""
    return [
        f"package={cfg.package}",
        f"repository={cfg.repository}",
        f"test_mode={cfg.test_mode}",
        f"package_version={cfg.package_version}",
        f"output_image={cfg.output_image}",
        f"ascii_tree={cfg.ascii_tree}",
        f"max_depth={cfg.max_depth}",
    ]