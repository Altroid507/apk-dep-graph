"""BFS с рекурсией, ограничение глубины и обработка циклов."""

from graph import DependencyGraph

ROOT_DEPTH = 0


def bfs_recursive(
    graph: DependencyGraph, start: str, max_depth: int
) -> list[str]:
    """Вернуть узлы, достижимые из ``start`` рекурсивным BFS.

    Устойчив к циклам: узел попадает в результат только
    на минимальной глубине.
    """
    if start not in graph.edges:
        return []
    visited: dict[str, int] = {}
    result: list[str] = []
    _bfs_level(graph, [start], ROOT_DEPTH, max_depth, visited, result)
    return result


def _bfs_level(
    graph: DependencyGraph,
    frontier: list[str],
    depth: int,
    max_depth: int,
    visited: dict[str, int],
    result: list[str],
) -> None:
    """Обработать один уровень BFS и рекурсивно перейти к следующему."""
    next_frontier: list[str] = []
    for node in frontier:
        if node in visited and visited[node] <= depth:
            continue
        visited[node] = depth
        result.append(node)
        if depth >= max_depth:
            continue
        for neighbor in graph.neighbors(node):
            next_frontier.append(neighbor)
    if next_frontier:
        _bfs_level(
            graph, next_frontier, depth + 1, max_depth, visited, result
        )