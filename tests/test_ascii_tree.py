"""Тесты ASCII-дерева."""

from ascii_tree import render_tree
from graph import DependencyGraph


def test_render_tree_handles_cycle():
    """Цикл A↔B не приводит к бесконечной рекурсии."""
    graph = DependencyGraph()
    for source, target in [("A", "B"), ("B", "A")]:
        graph.add_edge(source, target)
    output = render_tree(graph, "A", 5)
    assert output.startswith("A")
    assert "B" in output