"""Направленный граф зависимостей."""

from dataclasses import dataclass, field


@dataclass
class DependencyGraph:
    """Граф на списках смежности."""

    edges: dict[str, list[str]] = field(default_factory=dict)

    def add_edge(self, source: str, target: str) -> None:
        """Зарегистрировать ребро ``source -> target``."""
        self.edges.setdefault(source, [])
        if target not in self.edges[source]:
            self.edges[source].append(target)
        self.edges.setdefault(target, [])

    def nodes(self) -> list[str]:
        """Вернуть все узлы в порядке вставки."""
        return list(self.edges.keys())

    def neighbors(self, node: str) -> list[str]:
        """Вернуть прямые зависимости ``node``."""
        return list(self.edges.get(node, []))

    def reverse(self) -> "DependencyGraph":
        """Вернуть граф с обратными рёбрами."""
        reversed_graph = DependencyGraph()
        for node in self.nodes():
            reversed_graph.edges.setdefault(node, [])
        for source, targets in self.edges.items():
            for target in targets:
                reversed_graph.add_edge(target, source)
        return reversed_graph