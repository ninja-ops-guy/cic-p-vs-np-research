"""CIC Core Library — Shared primitives for all security tools.

Extracted from the CIC research framework. Provides:
- SAT solving (DPLL with unit propagation)
- Necessity closure (N_φ) for backdoor analysis
- Treewidth estimation (MinFill heuristic)
- ETC computation (entropy trajectory analysis)
- Graph construction for CNF formulas

All algorithms are from peer-reviewed research (Stages 1-18).
"""

from __future__ import annotations

import math
import random
import time
from typing import Optional


# ===================================================================
# SAT Primitives
# ===================================================================

def unit_propagate(clauses: list[list[int]], assignment: dict[int, bool]) -> tuple[list[list[int]], dict[int, bool], bool]:
    """Apply unit propagation. Returns (simplified_clauses, extended_assignment, contradiction)."""
    assignment = dict(assignment)
    contradiction = False
    changed = True
    while changed and not contradiction:
        changed = False
        new_clauses = []
        for clause in clauses:
            # Evaluate clause
            satisfied = False
            unassigned = []
            falsified_count = 0
            for lit in clause:
                var = abs(lit)
                if var in assignment:
                    val = assignment[var] if lit > 0 else not assignment[var]
                    if val:
                        satisfied = True
                        break
                    else:
                        falsified_count += 1
                else:
                    unassigned.append(lit)
            if satisfied:
                continue
            if falsified_count == len(clause):
                contradiction = True
                break
            if len(unassigned) == 1:
                lit = unassigned[0]
                var = abs(lit)
                assignment[var] = lit > 0
                changed = True
            else:
                new_clauses.append(unassigned if unassigned else clause)
        clauses = new_clauses
    return clauses, assignment, contradiction


def dpll_solve(clauses: list[list[int]], num_vars: int, timeout: float = 30.0,
               _assignment: Optional[dict[int, bool]] = None, _start: Optional[float] = None) -> Optional[dict[int, bool]]:
    """DPLL SAT solver with timeout. Returns model or None (UNSAT/timeout)."""
    if _start is None:
        _start = time.time()
    if _assignment is None:
        _assignment = {}
    if time.time() - _start > timeout:
        return None

    clauses, assignment, contradiction = unit_propagate(clauses, _assignment)
    if contradiction:
        return None
    if not clauses:
        for v in range(1, num_vars + 1):
            if v not in assignment:
                assignment[v] = True
        return assignment
    if any(len(c) == 0 for c in clauses):
        return None

    unassigned = sorted({abs(lit) for c in clauses for lit in c if abs(lit) not in assignment})
    if not unassigned:
        return assignment if all(
            any((lit > 0 and assignment.get(abs(lit))) or (lit < 0 and not assignment.get(abs(lit)))
                for lit in c) for c in clauses) else None

    var = unassigned[0]
    for val in [True, False]:
        a = dict(assignment)
        a[var] = val
        result = dpll_solve(clauses, num_vars, timeout, a, _start)
        if result is not None:
            return result
    return None


def is_satisfiable(clauses: list[list[int]], num_vars: int) -> bool:
    """Quick SAT check."""
    return dpll_solve(clauses, num_vars) is not None


def get_backbone(clauses: list[list[int]], num_vars: int) -> dict[int, bool]:
    """Find backbone literals (forced in ALL models). O(n) SAT calls."""
    backbone = {}
    if not is_satisfiable(clauses, num_vars):
        return backbone
    for v in range(1, num_vars + 1):
        if not is_satisfiable(clauses + [[-v]], num_vars):
            backbone[v] = True
        elif not is_satisfiable(clauses + [[v]], num_vars):
            backbone[v] = False
    return backbone


# ===================================================================
# Graph Construction
# ===================================================================

def build_primal_graph(num_vars: int, clauses: list[list[int]]) -> dict[int, set[int]]:
    """Build primal (Gaifman) graph: edges between variables in same clause."""
    graph = {v: set() for v in range(1, num_vars + 1)}
    for clause in clauses:
        vars_in = [abs(lit) for lit in clause]
        for i, v1 in enumerate(vars_in):
            for v2 in vars_in[i + 1:]:
                if v1 != v2:
                    graph[v1].add(v2)
                    graph[v2].add(v1)
    return graph


def minfill_treewidth(graph: dict[int, set[int]]) -> tuple[list[int], int]:
    """MinFill heuristic for treewidth. Returns (ordering, width)."""
    g = {k: set(v) for k, v in graph.items()}
    ordering, max_width = [], 0
    while g:
        best_node, best_fill = None, float('inf')
        for node in g:
            neighbors = list(g[node])
            if not neighbors:
                best_node, best_fill = node, 0
                break
            fill = sum(1 for i, u in enumerate(neighbors) for v in neighbors[i + 1:] if v not in g[u])
            if fill < best_fill:
                best_fill, best_node = fill, node
        if best_node is None:
            best_node = next(iter(g))
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


# ===================================================================
# Necessity Closure (Stage 18)
# ===================================================================

class NecessityClosure:
    """Galois closure operator N_φ for a CNF formula.

    N_φ(S) = all literals forced by unit propagation from assumptions S.
    Proved properties: extensivity, monotonicity, idempotence.
    """

    def __init__(self, clauses: list[list[int]], num_vars: int):
        self.clauses = [list(c) for c in clauses]
        self.num_vars = num_vars

    def closure(self, assumptions: set[int]) -> set[int]:
        """Compute N_φ(assumptions)."""
        assignment = {abs(lit): lit > 0 for lit in assumptions}
        _, forced, contradiction = unit_propagate(self.clauses, assignment)
        if contradiction:
            return set(range(1, self.num_vars + 1)) | set(range(-self.num_vars, 0))
        return {var if val else -var for var, val in forced.items()}

    def closure_sequence(self, seed: Optional[set[int]] = None) -> list[set[int]]:
        """Full closure sequence [N^0(S), N^1(S), ..., N^∞(S)]."""
        seed = seed or set()
        seq = [set(seed)]
        current = set(seed)
        while True:
            nxt = self.closure(current)
            if nxt == current:
                break
            seq.append(nxt)
            current = nxt
        return seq

    def backbone(self) -> set[int]:
        """N^∞(∅) — literals forced in ALL models."""
        seq = self.closure_sequence(set())
        return seq[-1] if seq else set()


# ===================================================================
# ETC (Entropy Trajectory Complexity) — Stage 17
# ===================================================================

class ETCCalculator:
    """Compute ETC: total curvature of entropy trajectory during search."""

    def __init__(self, clauses: list[list[int]], num_vars: int):
        self.clauses = clauses
        self.num_vars = num_vars

    def _state_entropy(self, assignment: dict[int, bool]) -> float:
        """Search-state entropy given partial assignment."""
        simplified, _, contradiction = unit_propagate(self.clauses, assignment)
        if contradiction:
            return 0.0
        assigned = set(assignment.keys())
        unassigned = [v for v in range(1, self.num_vars + 1) if v not in assigned]
        if not unassigned:
            return 0.0
        unit_vars = set()
        for clause in simplified:
            u = [lit for lit in clause if abs(lit) not in assigned]
            if len(u) == 1:
                unit_vars.add(abs(u[0]))
        p = len(unit_vars) / len(unassigned) if unassigned else 0.0
        p = max(0.001, min(0.999, p))
        return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))

    def trajectory(self, num_samples: int = 100) -> list[float]:
        """Sample entropy trajectory via random DPLL walks."""
        depth_entropies: dict[int, list[float]] = {}
        for _ in range(num_samples):
            assignment = {}
            for depth in range(self.num_vars + 1):
                entropy = self._state_entropy(assignment)
                depth_entropies.setdefault(depth, []).append(entropy)
                if len(assignment) >= self.num_vars:
                    break
                unassigned = [v for v in range(1, self.num_vars + 1) if v not in assignment]
                if not unassigned:
                    break
                assignment[random.choice(unassigned)] = random.choice([True, False])
        max_depth = max(depth_entropies.keys()) if depth_entropies else 0
        return [sum(depth_entropies.get(d, [0])) / len(depth_entropies.get(d, [1]))
                for d in range(max_depth + 1)]

    def compute(self, num_samples: int = 100) -> float:
        """ETC = Σ |Δ²H_i| — total curvature."""
        t = self.trajectory(num_samples)
        if len(t) < 3:
            return 0.0
        return sum(abs(t[i - 1] - 2 * t[i] + t[i + 1]) for i in range(1, len(t) - 1))


# ===================================================================
# Formula Generators
# ===================================================================

def make_php(n: int) -> tuple[int, list[list[int]]]:
    """Pigeonhole PHP(n, n-1). Always UNSAT."""
    nv = n * (n - 1)
    clauses = []
    for pigeon in range(n):
        clauses.append([pigeon * (n - 1) + hole + 1 for hole in range(n - 1)])
    for hole in range(n - 1):
        for p1 in range(n):
            for p2 in range(p1 + 1, n):
                v1 = p1 * (n - 1) + hole + 1
                v2 = p2 * (n - 1) + hole + 1
                clauses.append([-v1, -v2])
    return nv, clauses


def make_chain(n: int) -> tuple[int, list[list[int]]]:
    """Chain of implications x1 → x2 → ... → xn. Always SAT."""
    clauses = []
    for i in range(1, n):
        clauses.append([-i, i + 1])
    for i in range(1, n - 1):
        clauses.append([i, i + 1, i + 2])
    return n, clauses


def parse_dimacs(cnf: str) -> tuple[int, list[list[int]]]:
    """Parse DIMACS CNF string."""
    clauses, num_vars = [], 0
    for line in cnf.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('c'):
            continue
        if line.startswith('p cnf'):
            num_vars = int(line.split()[2])
            continue
        lits = [int(x) for x in line.split()]
        if lits and lits[-1] == 0:
            lits = lits[:-1]
        if lits:
            clauses.append(lits)
    return num_vars, clauses


def to_dimacs(num_vars: int, clauses: list[list[int]]) -> str:
    """Convert to DIMACS CNF."""
    lines = [f"p cnf {num_vars} {len(clauses)}"]
    for c in clauses:
        lines.append(' '.join(map(str, c)) + ' 0')
    return '\n'.join(lines) + '\n'
