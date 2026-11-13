"""Отрисовка графа зависимостей в виде ASCII-дерева."""

from graph import DependencyGraph

INDENT = "  "


def render_tree(
    graph: DependencyGraph, root: str, max_depth: int
) -> str:
    """Отрисовать граф в виде ASCII-дерева от ``root``."""
    lines: list[str] = [root]
    _render_children(graph, root, 1, max_depth, "", lines, set())
    return "\n".join(lines)


def _render_children(
    graph: DependencyGraph,
    node: str,
    depth: int,
    max_depth: int,
    prefix: str,
    lines: list[str],
    ancestors: set[str],
) -> None:
    """Рекурсивно отрисовать потомков ``node``."""
    if depth > max_depth or node in ancestors:
        return
    children = graph.neighbors(node)
    if not children:
        return
    ancestors = ancestors | {node}
    for index, child in enumerate(children):
        last = index == len(children) - 1
        connector = "└── " if last else "├── "
        lines.append(prefix + connector + child)
        child_prefix = prefix + ("    " if last else "│   ")
        _render_children(
            graph, child, depth + 1, max_depth,
            child_prefix, lines, ancestors,
        )