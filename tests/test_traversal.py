"""Тесты BFS-обхода с рекурсией."""

from graph import DependencyGraph
from traversal import bfs_recursive


def _simple_graph():
    """Построить простой граф A→B→D→E, A→C→D."""
    graph = DependencyGraph()
    for source, target in [
        ("A", "B"), ("A", "C"), ("B", "D"), ("C", "D"), ("D", "E"),
    ]:
        graph.add_edge(source, target)
    return graph


def test_bfs_respects_depth():
    """Глубина ограничивает результат."""
    graph = _simple_graph()
    result = bfs_recursive(graph, "A", 1)
    assert result == ["A", "B", "C"]


def test_bfs_handles_cycles():
    """Цикл A→B→C→A не зацикливает обход."""
    graph = DependencyGraph()
    for source, target in [("A", "B"), ("B", "C"), ("C", "A")]:
        graph.add_edge(source, target)
    result = bfs_recursive(graph, "A", 10)
    assert result == ["A", "B", "C"]


def test_bfs_unknown_start():
    """Неизвестный стартовый узел даёт пустой результат."""
    graph = _simple_graph()
    assert bfs_recursive(graph, "Z", 5) == []