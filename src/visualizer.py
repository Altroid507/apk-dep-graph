"""Генерация PlantUML и сохранение SVG."""

import base64
import urllib.request
import zlib
from pathlib import Path

from errors import RepositoryError
from graph import DependencyGraph

PUML_HEADER = "@startuml\n"
PUML_FOOTER = "@enduml\n"
PLANTUML_SERVER = "https://www.plantuml.com/plantuml/svg/"
HTTP_TIMEOUT_SEC = 30


def to_plantuml(graph: DependencyGraph) -> str:
    """Преобразовать граф в текст PlantUML."""
    lines: list[str] = [PUML_HEADER]
    for source, targets in graph.edges.items():
        for target in targets:
            lines.append(f'"{source}" --> "{target}"\n')
    lines.append(PUML_FOOTER)
    return "".join(lines)


def _encode_puml(puml_text: str) -> str:
    """Закодировать PlantUML-текст для сервера (deflate + base64)."""
    compressor = zlib.compressobj(9)
    data = puml_text.encode("utf-8")
    compressed = compressor.compress(data) + compressor.flush()
    return base64.b64encode(compressed).decode("ascii")


def save_svg(graph: DependencyGraph, output: Path) -> None:
    """Сохранить граф как SVG через PlantUML-сервер."""
    puml_text = to_plantuml(graph)
    encoded = _encode_puml(puml_text)
    url = PLANTUML_SERVER + encoded
    try:
        with urllib.request.urlopen(
            url, timeout=HTTP_TIMEOUT_SEC
        ) as response:
            svg = response.read()
    except OSError as exc:
        raise RepositoryError(
            f"Ошибка PlantUML-сервера: {exc}"
        ) from exc
    output.write_bytes(svg)