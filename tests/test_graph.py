"""Тесты графа зависимостей."""

from graph import DependencyGraph


def test_add_edge_deduplicates():
    """Повторное ребро не дублируется."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("A", "B")
    assert graph.neighbors("A") == ["B"]


def test_reverse_keeps_edges():
    """Обратный граф сохраняет все рёбра."""
    graph = DependencyGraph()
    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    reversed_graph = graph.reverse()
    assert reversed_graph.neighbors("C") == ["B"]
    assert reversed_graph.neighbors("B") == ["A"]