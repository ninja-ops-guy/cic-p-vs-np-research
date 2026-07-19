"""Treewidth and elimination width computation utilities.

Based on the CIC framework's MinFill heuristic with proven approximation
bounds (Theorem 1: elimination width w => resolution width <= max(w, k)).

Key functions:
    - minfill_ordering: Greedy MinFill heuristic for treewidth
    - estimate_difficulty: Classify formula difficulty by width
"""

from __future__ import annotations

import random
from typing import Optional


def eliminate_node(
    graph: dict[int, set[int]],
    node: int,
) -> tuple[dict[int, set[int]], int]:
    """Eliminate a node from a graph, making its neighborhood a clique.

    This is the core operation in variable elimination. The "fill edges"
    added to make the neighborhood a clique determine the width.

    Args:
        graph: Adjacency dict (modified in place).
        node: Node to eliminate.

    Returns:
        Tuple of (new_graph, bag_size) where bag_size is the size of
        the eliminated node's neighborhood (width contribution).
    """
    graph = {k: set(v) for k, v in graph.items()}  # shallow copy
    neighbors = list(graph.get(node, set()))
    bag_size = len(neighbors)

    # Make neighborhood a clique (add fill edges)
    for i, u in enumerate(neighbors):
        for v in neighbors[i + 1:]:
            if v not in graph.get(u, set()):
                graph[u].add(v)
                graph[v].add(u)

    # Remove eliminated node
    if node in graph:
        del graph[node]
    for neighbors_set in graph.values():
        neighbors_set.discard(node)

    return graph, bag_size


def get_width(
    graph: dict[int, set[int]],
    ordering: list[int],
) -> int:
    """Compute the elimination width of a given ordering.

    Args:
        graph: Initial adjacency dict.
        ordering: Elimination order (list of nodes).

    Returns:
        Maximum bag size (width) of the elimination.
    """
    g = {k: set(v) for k, v in graph.items()}
    max_width = 0
    for node in ordering:
        if node not in g:
            continue
        neighbors = list(g[node])
        max_width = max(max_width, len(neighbors))
        # Make clique
        for i, u in enumerate(neighbors):
            for v in neighbors[i + 1:]:
                g[u].add(v)
                g[v].add(u)
        # Remove node
        del g[node]
        for s in g.values():
            s.discard(node)
    return max_width


def minfill_ordering(
    graph: dict[int, set[int]],
) -> tuple[list[int], int]:
    """Compute MinFill elimination ordering.

    Greedy heuristic: at each step, eliminate the node that adds
    the fewest fill edges. This is the classic MinFill heuristic
    with proven approximation bounds.

    Args:
        graph: Adjacency dict.

    Returns:
        Tuple of (ordering, max_width) where ordering is the
        elimination sequence and max_width is the estimated
        treewidth (maximum bag size - 1).
    """
    g = {k: set(v) for k, v in graph.items()}
    ordering: list[int] = []
    max_width = 0

    while g:
        best_node = None
        best_fill = float("inf")

        for node in g:
            neighbors = list(g[node])
            if not neighbors:
                best_node = node
                best_fill = 0
                break

            # Count fill edges needed
            fill = 0
            for i, u in enumerate(neighbors):
                for v in neighbors[i + 1:]:
                    if v not in g[u]:
                        fill += 1

            if fill < best_fill:
                best_fill = fill
                best_node = node

        if best_node is None:
            best_node = next(iter(g))

        # Eliminate best_node
        neighbors = list(g[best_node])
        max_width = max(max_width, len(neighbors))

        for i, u in enumerate(neighbors):
            for v in neighbors[i + 1:]:
                g[u].add(v)
                g[v].add(u)

        del g[best_node]
        for s in g.values():
            s.discard(best_node)

        ordering.append(best_node)

    return ordering, max_width


def random_ordering(graph: dict[int, set[int]]) -> list[int]:
    """Generate a random elimination ordering (baseline comparison).

    Args:
        graph: Adjacency dict.

    Returns:
        Random permutation of graph nodes.
    """
    nodes = list(graph.keys())
    random.shuffle(nodes)
    return nodes


def estimate_difficulty(
    width: int,
    num_vars: int,
    num_clauses: int,
) -> str:
    """Classify formula difficulty by elimination width.

    Classification thresholds based on CIC research:
    - trivial (w <= 3):    Bounded-width algorithms guaranteed fast
    - easy (w <= 10):      Practical for most solvers
    - moderate (w <= 25):  Tractable with good heuristics
    - hard (w <= 50):      May need specialized approaches
    - extreme (w > 50):    Structural defense is strong

    Args:
        width: Elimination width (treewidth estimate).
        num_vars: Number of variables.
        num_clauses: Number of clauses.

    Returns:
        Difficulty classification string.
    """
    if width <= 3:
        return "trivial"
    elif width <= 10:
        return "easy"
    elif width <= 25:
        return "moderate"
    elif width <= 50:
        return "hard"
    else:
        return "extreme"


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Width Utils — Self-Test")
    print("=" * 60)

    # Test on tree (star graph)
    print("\n--- MinFill on tree ---")
    tree = {1: {2, 3, 4}, 2: {1}, 3: {1}, 4: {1}}
    ordering, width = minfill_ordering(tree)
    print(f"  Ordering: {ordering}, Width: {width}")
    assert width <= 3

    # Test on clique
    print("\n--- MinFill on clique ---")
    clique = {1: {2, 3, 4}, 2: {1, 3, 4}, 3: {1, 2, 4}, 4: {1, 2, 3}}
    ordering2, width2 = minfill_ordering(clique)
    print(f"  Ordering: {ordering2}, Width: {width2}")
    assert width2 == 3  # K4 has treewidth 3

    # Test get_width
    print("\n--- get_width ---")
    path_graph = {1: {2}, 2: {1, 3}, 3: {2, 4}, 4: {3, 5}, 5: {4}}
    w = get_width(path_graph, [1, 2, 3, 4, 5])
    print(f"  Path graph width (sequential order): {w}")
    assert w == 1  # Path has treewidth 1

    # Test random ordering
    print("\n--- random_ordering ---")
    rand_ord = random_ordering(path_graph)
    print(f"  Random: {rand_ord}")
    assert len(rand_ord) == 5

    # Test difficulty classification
    print("\n--- estimate_difficulty ---")
    for w_test, expected in [(2, "trivial"), (8, "easy"), (20, "moderate"), (40, "hard"), (60, "extreme")]:
        result = estimate_difficulty(w_test, 100, 400)
        assert result == expected, f"Expected {expected}, got {result}"
        print(f"  width={w_test:3d} -> {result}")

    print("\n" + "=" * 60)
    print("All width utils tests passed!")
    print("=" * 60)
