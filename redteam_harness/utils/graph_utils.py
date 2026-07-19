"""Graph utilities for constructing primal graphs of SAT formulas
and computing structural properties.

The primal (Gaifman) graph of a CNF formula has variables as nodes
and edges between variables that appear together in a clause.
Treewidth of this graph controls proof complexity (CIC Theorem 1).
"""

from __future__ import annotations

from typing import Optional


def build_variable_graph(clauses: list[list[int]]) -> dict[int, set[int]]:
    """Build adjacency-list representation of the primal graph.

    Args:
        clauses: CNF formula as list of integer literal lists.

    Returns:
        Dict mapping each variable to its set of neighbors.

    Example:
        >>> build_variable_graph([[1, 2], [2, 3]])
        {1: {2}, 2: {1, 3}, 3: {2}}
    """
    graph: dict[int, set[int]] = {}
    for clause in clauses:
        vars_in_clause = [abs(lit) for lit in clause]
        for v in vars_in_clause:
            if v not in graph:
                graph[v] = set()
        # Add edges between all pairs
        for i, v1 in enumerate(vars_in_clause):
            for v2 in vars_in_clause[i + 1:]:
                if v1 != v2:
                    graph[v1].add(v2)
                    graph[v2].add(v1)
    return graph


def build_primal_graph(
    num_vars: int,
    clauses: list[list[int]],
) -> dict[int, set[int]]:
    """Build primal (Gaifman) graph of a CNF formula.

    Alias for build_variable_graph with explicit num_vars parameter.
    Ensures all variables appear in the graph even if isolated.

    Args:
        num_vars: Total number of variables.
        clauses: CNF formula.

    Returns:
        Adjacency dict with all variables 1..num_vars as keys.
    """
    graph = build_variable_graph(clauses)
    for v in range(1, num_vars + 1):
        if v not in graph:
            graph[v] = set()
    return graph


def build_incidence_graph(
    num_vars: int,
    clauses: list[list[int]],
) -> dict[int, set[int]]:
    """Build bipartite incidence graph (variables <-> clauses).

    Args:
        num_vars: Number of variables.
        clauses: CNF formula.

    Returns:
        Adjacency dict. Variables are 1..num_vars, clauses are
        num_vars+1..num_vars+len(clauses).
    """
    graph: dict[int, set[int]] = {}
    for v in range(1, num_vars + 1):
        graph[v] = set()

    for ci, clause in enumerate(clauses):
        clause_node = num_vars + 1 + ci
        graph[clause_node] = set()
        for lit in clause:
            var = abs(lit)
            graph[var].add(clause_node)
            graph[clause_node].add(var)

    return graph


def get_connected_components(graph: dict[int, set[int]]) -> list[set[int]]:
    """Find connected components of a graph.

    Args:
        graph: Adjacency dict.

    Returns:
        List of component sets.
    """
    visited: set[int] = set()
    components: list[set[int]] = []

    def dfs(node: int, component: set[int]) -> None:
        component.add(node)
        visited.add(node)
        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                dfs(neighbor, component)

    for node in graph:
        if node not in visited:
            component: set[int] = set()
            dfs(node, component)
            if component:
                components.append(component)

    return components


def graph_stats(graph: dict[int, set[int]]) -> dict:
    """Compute basic statistics of a graph.

    Args:
        graph: Adjacency dict.

    Returns:
        Dict with keys: num_nodes, num_edges, avg_degree, max_degree, density.
    """
    nodes = list(graph.keys())
    num_nodes = len(nodes)
    if num_nodes == 0:
        return {
            "num_nodes": 0,
            "num_edges": 0,
            "avg_degree": 0.0,
            "max_degree": 0,
            "density": 0.0,
        }

    # Count edges (undirected)
    edge_set: set[tuple[int, int]] = set()
    for node, neighbors in graph.items():
        for neighbor in neighbors:
            edge = tuple(sorted((node, neighbor)))
            edge_set.add(edge)
    num_edges = len(edge_set)

    degrees = [len(graph.get(node, set())) for node in nodes]
    avg_degree = sum(degrees) / num_nodes if num_nodes > 0 else 0.0
    max_degree = max(degrees) if degrees else 0

    # Density = 2*E / (V*(V-1))
    max_edges = num_nodes * (num_nodes - 1) / 2
    density = num_edges / max_edges if max_edges > 0 else 0.0

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "avg_degree": avg_degree,
        "max_degree": max_degree,
        "density": density,
    }


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Graph Utils — Self-Test")
    print("=" * 60)

    # Test primal graph
    print("\n--- Primal graph ---")
    clauses = [[1, 2], [2, 3], [3, 4, 5]]
    g = build_primal_graph(5, clauses)
    print(f"  Graph: {dict((k, sorted(v)) for k, v in sorted(g.items()))}")
    assert g[1] == {2}
    assert g[2] == {1, 3}
    assert g[4] == {3, 5}
    print("  Structure: OK")

    # Test components
    print("\n--- Connected components ---")
    disconnected = {1: {2}, 2: {1}, 3: {4}, 4: {3}}
    comps = get_connected_components(disconnected)
    assert len(comps) == 2
    print(f"  Components: {[sorted(c) for c in comps]}")

    # Test stats
    print("\n--- Graph stats ---")
    stats = graph_stats(g)
    print(f"  Stats: {stats}")
    assert stats["num_nodes"] == 5
    assert stats["num_edges"] == 4

    print("\n" + "=" * 60)
    print("All graph utils tests passed!")
    print("=" * 60)
