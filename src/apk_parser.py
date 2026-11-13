"""Минимальный парсер APKINDEX для Alpine Linux.

Не использует ``apk`` и сторонние библиотеки: только ``urllib``
и ``gzip`` из стандартной библиотеки.
"""

import gzip
import io
import urllib.request
from pathlib import Path

from errors import PackageNotFoundError, RepositoryError

APKINDEX_NAME = "APKINDEX.tar.gz"
BLOCK_SEPARATOR = "\n\n"
HTTP_TIMEOUT_SEC = 15


def _decompress(payload: bytes) -> str:
    """Распаковать gzip-содержимое APKINDEX в текст."""
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(payload)) as archive:
            return archive.read().decode("utf-8", errors="replace")
    except OSError as exc:
        raise RepositoryError(
            f"Не удалось распаковать APKINDEX: {exc}"
        ) from exc


def _download_index(repository: str) -> str:
    """Скачать APKINDEX.tar.gz по HTTP(S)."""
    url = repository.rstrip("/") + "/" + APKINDEX_NAME
    try:
        with urllib.request.urlopen(
            url, timeout=HTTP_TIMEOUT_SEC
        ) as response:
            payload = response.read()
    except OSError as exc:
        raise RepositoryError(
            f"Не удалось скачать {url}: {exc}"
        ) from exc
    return _decompress(payload)


def _read_local_index(path: Path) -> str:
    """Прочитать локальный APKINDEX.tar.gz."""
    return _decompress(path.read_bytes())


def _open_index(repository: str) -> str:
    """Загрузить APKINDEX по URL или из локального файла."""
    if repository.startswith(("http://", "https://")):
        return _download_index(repository)
    local = Path(repository)
    if not local.is_file():
        raise RepositoryError(f"Путь репозитория не найден: {repository}")
    return _read_local_index(local)


def _split_records(text: str) -> list[str]:
    """Разбить текст APKINDEX на записи."""
    return [
        block for block in text.split(BLOCK_SEPARATOR) if block.strip()
    ]


def _parse_record(record: str) -> dict[str, str]:
    """Разобрать одну запись APKINDEX в словарь."""
    parsed: dict[str, str] = {}
    for line in record.splitlines():
        if len(line) < 2 or line[1] != ":":
            continue
        parsed[line[0]] = line[2:]
    return parsed


def _extract_version(record: dict[str, str]) -> str:
    """Вернуть поле версии из записи."""
    return record.get("V", "")


def find_package_record(
    repository: str, package: str, version: str
) -> dict[str, str]:
    """Найти запись APKINDEX по имени и версии пакета."""
    text = _open_index(repository)
    for record_text in _split_records(text):
        record = _parse_record(record_text)
        name_matches = record.get("P") == package
        version_matches = _extract_version(record) == version
        if name_matches and version_matches:
            return record
    raise PackageNotFoundError(
        f"Пакет {package}={version} не найден в {repository}"
    )


def _strip_version_constraint(token: str) -> str:
    """Отбросить версионные ограничения у зависимости apk."""
    name = token.split("=", 1)[0]
    name = name.split(">", 1)[0]
    name = name.split("<", 1)[0]
    name = name.split("~", 1)[0]
    return name


def direct_dependencies(
    repository: str, package: str, version: str
) -> list[str]:
    """Вернуть прямые зависимости пакета из APKINDEX."""
    record = find_package_record(repository, package, version)
    raw = record.get("D", "").strip()
    if not raw:
        return []
    names: list[str] = []
    for token in raw.split():
        name = _strip_version_constraint(token)
        if name:
            names.append(name)
    return names