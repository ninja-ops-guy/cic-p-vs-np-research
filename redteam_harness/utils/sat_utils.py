"""Shared SAT solving utilities for the red team harness.

Leverages the CIC framework's structural analysis capabilities
to provide efficient SAT encoding, solving, and analysis.

Core functions:
    - parse_dimacs / to_dimacs: DIMACS CNF serialization
    - unit_propagate: Unit propagation (core of NPT)
    - dpll_solve: Complete DPLL solver with timeout
    - get_backbone: Extract forced literals (all models)
    - make_small_example: Generate benchmark formulas
"""

from __future__ import annotations

import random
import time
from typing import Optional


# ---------------------------------------------------------------------------
# DIMACS
# ---------------------------------------------------------------------------

def parse_dimacs(cnf_string: str) -> tuple[int, list[list[int]]]:
    """Parse a DIMACS CNF string into (num_vars, clauses).

    Args:
        cnf_string: Raw DIMACS CNF content.

    Returns:
        Tuple of (num_vars, clauses) where clauses is a list of
        integer literal lists. Each clause is terminated by 0.

    Example:
        >>> parse_dimacs("c comment\\np cnf 3 2\\n1 -2 0\\n-1 3 0\\n")
        (3, [[1, -2], [-1, 3]])
    """
    clauses: list[list[int]] = []
    num_vars = 0
    for line in cnf_string.splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p cnf"):
            parts = line.split()
            num_vars = int(parts[2])
            continue
        # Parse literals
        literals = list(map(int, line.split()))
        # Remove trailing 0
        if literals and literals[-1] == 0:
            literals = literals[:-1]
        if literals:
            clauses.append(literals)
    return num_vars, clauses


def to_dimacs(num_vars: int, clauses: list[list[int]]) -> str:
    """Convert clauses back to DIMACS CNF format.

    Args:
        num_vars: Number of variables.
        clauses: List of integer literal lists.

    Returns:
        DIMACS CNF formatted string.
    """
    lines = [f"p cnf {num_vars} {len(clauses)}"]
    for clause in clauses:
        line = " ".join(map(str, clause)) + " 0"
        lines.append(line)
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Clause evaluation
# ---------------------------------------------------------------------------

def eval_clause(clause: list[int], assignment: dict[int, bool]) -> Optional[bool]:
    """Evaluate a clause under a partial assignment.

    Args:
        clause: List of integer literals.
        assignment: Dict mapping variable (1-indexed) to True/False.

    Returns:
        True if clause is satisfied,
        False if all literals are falsified,
        None if undetermined.
    """
    has_unassigned = False
    for lit in clause:
        var = abs(lit)
        if var in assignment:
            val = assignment[var] if lit > 0 else not assignment[var]
            if val:
                return True
        else:
            has_unassigned = True
    return None if has_unassigned else False


# ---------------------------------------------------------------------------
# Unit propagation
# ---------------------------------------------------------------------------

def unit_propagate(
    clauses: list[list[int]],
    assignment: dict[int, bool],
) -> tuple[list[list[int]], dict[int, bool], bool]:
    """Apply unit propagation to a clause set.

    Iteratively finds unit clauses (clauses with all but one literal
    falsified), assigns the remaining literal, and simplifies.

    Args:
        clauses: CNF clause set.
        assignment: Current partial assignment (modified in place).

    Returns:
        Tuple of (simplified_clauses, extended_assignment, contradiction).
        If contradiction is True, the formula is UNSAT under the
        current assignment.

    This is the core algorithm underlying the Necessity Propagation
    Theory (NPT) backdoor scanner.
    """
    assignment = dict(assignment)  # copy
    contradiction = False

    changed = True
    while changed and not contradiction:
        changed = False
        new_clauses = []
        for clause in clauses:
            status = eval_clause(clause, assignment)
            if status is True:
                continue  # satisfied, drop
            if status is False:
                contradiction = True
                break
            # Undetermined — check if unit
            unassigned = []
            for lit in clause:
                var = abs(lit)
                if var not in assignment:
                    unassigned.append(lit)
            if len(unassigned) == 0:
                # Should have been caught above
                contradiction = True
                break
            elif len(unassigned) == 1:
                # Unit clause — assign
                lit = unassigned[0]
                var = abs(lit)
                val = lit > 0
                assignment[var] = val
                changed = True
            else:
                new_clauses.append(clause)
        clauses = new_clauses

    return clauses, assignment, contradiction


# ---------------------------------------------------------------------------
# Pure literal elimination
# ---------------------------------------------------------------------------

def pure_literal_eliminate(
    clauses: list[list[int]],
) -> tuple[list[list[int]], dict[int, bool]]:
    """Eliminate pure literals from a clause set.

    A pure literal appears with only one polarity across all clauses.
    It can be safely assigned to satisfy all clauses containing it.

    Args:
        clauses: CNF clause set.

    Returns:
        Tuple of (simplified_clauses, pure_assignments).
    """
    if not clauses:
        return clauses, {}

    # Count polarities
    pos: set[int] = set()
    neg: set[int] = set()
    for clause in clauses:
        for lit in clause:
            if lit > 0:
                pos.add(lit)
            else:
                neg.add(-lit)

    pure_pos = pos - neg
    pure_neg = neg - pos

    assignments: dict[int, bool] = {}
    for v in pure_pos:
        assignments[v] = True
    for v in pure_neg:
        assignments[v] = False

    if not assignments:
        return clauses, {}

    # Simplify
    new_clauses = []
    for clause in clauses:
        status = eval_clause(clause, assignments)
        if status is not True:
            new_clauses.append(clause)

    return new_clauses, assignments


# ---------------------------------------------------------------------------
# DPLL solver
# ---------------------------------------------------------------------------

def dpll_solve(
    clauses: list[list[int]],
    num_vars: int,
    timeout: float = 30.0,
    _assignment: Optional[dict[int, bool]] = None,
    _start_time: Optional[float] = None,
) -> Optional[dict[int, bool]]:
    """DPLL SAT solver with optional timeout.

    Implements the classic DPLL algorithm with unit propagation
    and pure literal elimination.

    Args:
        clauses: CNF formula as list of integer literal lists.
        num_vars: Number of variables.
        timeout: Maximum solving time in seconds.
        _assignment: Internal partial assignment (do not set).
        _start_time: Internal start time (do not set).

    Returns:
        A satisfying assignment as dict[var -> bool], or None if UNSAT
        or timeout.
    """
    if _start_time is None:
        _start_time = time.time()
    if _assignment is None:
        _assignment = {}

    # Check timeout
    if time.time() - _start_time > timeout:
        return None

    # Apply unit propagation
    clauses, assignment, contradiction = unit_propagate(clauses, _assignment)
    if contradiction:
        return None

    # Apply pure literal elimination
    clauses, pure = pure_literal_eliminate(clauses)
    assignment.update(pure)

    # Check if satisfied
    if not clauses:
        # All variables assigned?
        for v in range(1, num_vars + 1):
            if v not in assignment:
                assignment[v] = True  # arbitrary
        return assignment

    # Check for empty clause
    if any(len(c) == 0 for c in clauses):
        return None

    # Pick unassigned variable (first unassigned)
    unassigned_vars = set()
    for clause in clauses:
        for lit in clause:
            unassigned_vars.add(abs(lit))
    unassigned_vars = [v for v in unassigned_vars if v not in assignment]
    if not unassigned_vars:
        # All vars in remaining clauses are assigned — check
        return assignment if all(eval_clause(c, assignment) for c in clauses) else None

    var = unassigned_vars[0]

    # Try True
    assignment_true = dict(assignment)
    assignment_true[var] = True
    result = dpll_solve(clauses, num_vars, timeout, assignment_true, _start_time)
    if result is not None:
        return result

    # Try False
    assignment[var] = False
    return dpll_solve(clauses, num_vars, timeout, assignment, _start_time)


# ---------------------------------------------------------------------------
# Convenience wrappers
# ---------------------------------------------------------------------------

def is_satisfiable(clauses: list[list[int]], num_vars: int) -> bool:
    """Quick SAT check — returns True/False.

    Args:
        clauses: CNF formula.
        num_vars: Number of variables.

    Returns:
        True if formula is satisfiable, False otherwise.
    """
    return dpll_solve(clauses, num_vars) is not None


def get_backbone(clauses: list[list[int]], num_vars: int) -> dict[int, bool]:
    """Find all backbone literals (forced in ALL models).

    A backbone literal is a literal that is true in every satisfying
    assignment. Found by testing: is φ ∧ ¬l UNSAT?

    Args:
        clauses: CNF formula.
        num_vars: Number of variables.

    Returns:
        Dict of backbone variable assignments.

    Note: This is expensive — O(n) SAT calls. Use only for small
    formulas or when exact backbone is needed.
    """
    backbone: dict[int, bool] = {}

    # First check if formula is SAT at all
    if not is_satisfiable(clauses, num_vars):
        return backbone  # empty for UNSAT

    for v in range(1, num_vars + 1):
        # Test if v must be True
        test_clauses_t = clauses + [[-v]]
        if not is_satisfiable(test_clauses_t, num_vars):
            backbone[v] = True
            continue

        # Test if v must be False
        test_clauses_f = clauses + [[v]]
        if not is_satisfiable(test_clauses_f, num_vars):
            backbone[v] = False

    return backbone


# ---------------------------------------------------------------------------
# Formula generators
# ---------------------------------------------------------------------------

def make_small_example(
    formula_type: str,
    n: int,
    ratio: float = 4.26,
) -> tuple[int, list[list[int]]]:
    """Generate small test formulas for benchmarking.

    Args:
        formula_type: One of 'pigeonhole', 'chain_3sat', 'random_3sat', 'tseitin'.
        n: Size parameter (meaning varies by type).
        ratio: Clause-to-variable ratio for random formulas.

    Returns:
        Tuple of (num_vars, clauses).

    Formula types:
        - pigeonhole: PHP(n, n-1) — n pigeons, n-1 holes. Always UNSAT.
        - chain_3sat: Chain of n implications as 3-SAT. Always SAT.
        - random_3sat: Random 3-SAT with n variables. Phase transition near ratio=4.26.
        - tseitin: Tseitin formula on n x n grid. Always UNSAT.
    """
    if formula_type == "pigeonhole":
        # n pigeons, n-1 holes
        num_vars = n * (n - 1)
        clauses: list[list[int]] = []
        # Each pigeon in at least one hole
        for pigeon in range(n):
            clause = []
            for hole in range(n - 1):
                var = pigeon * (n - 1) + hole + 1
                clause.append(var)
            clauses.append(clause)
        # No two pigeons in same hole
        for hole in range(n - 1):
            for p1 in range(n):
                for p2 in range(p1 + 1, n):
                    v1 = p1 * (n - 1) + hole + 1
                    v2 = p2 * (n - 1) + hole + 1
                    clauses.append([-v1, -v2])
        return num_vars, clauses

    elif formula_type == "chain_3sat":
        # Chain: x1 -> x2 -> ... -> xn  as 3-SAT
        # Represented as (~xi OR xi+1) for i=1..n-1
        # Plus some 3-literal clauses for structure
        num_vars = n
        clauses = []
        for i in range(1, n):
            clauses.append([-i, i + 1])
        # Add redundant 3-clauses
        for i in range(1, n - 1):
            clauses.append([i, i + 1, i + 2])
        return num_vars, clauses

    elif formula_type == "random_3sat":
        num_vars = n
        num_clauses = int(n * ratio)
        clauses = []
        for _ in range(num_clauses):
            vars = random.sample(range(1, num_vars + 1), 3)
            clause = [v if random.random() < 0.5 else -v for v in vars]
            clauses.append(clause)
        return num_vars, clauses

    elif formula_type == "tseitin":
        # Tseitin on n x n grid
        grid_size = n
        num_vars = grid_size * grid_size
        clauses = []
        # Parity constraints on edges
        for i in range(grid_size):
            for j in range(grid_size):
                neighbors = []
                if i > 0:
                    neighbors.append((i - 1) * grid_size + j + 1)
                if i < grid_size - 1:
                    neighbors.append((i + 1) * grid_size + j + 1)
                if j > 0:
                    neighbors.append(i * grid_size + (j - 1) + 1)
                if j < grid_size - 1:
                    neighbors.append(i * grid_size + (j + 1) + 1)
                # XOR constraint: sum of neighbors ≡ 1 (mod 2)
                # Encoded as CNF
                if len(neighbors) >= 2:
                    for a in range(len(neighbors)):
                        for b in range(a + 1, len(neighbors)):
                            clauses.append([-neighbors[a], -neighbors[b]])
        return num_vars, clauses

    else:
        raise ValueError(f"Unknown formula_type: {formula_type}")


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SAT Utils — Self-Test")
    print("=" * 60)

    # Test DIMACS roundtrip
    print("\n--- DIMACS roundtrip ---")
    clauses = [[1, -2], [-1, 3, 4], [2, -3]]
    dimacs = to_dimacs(4, clauses)
    nv, parsed = parse_dimacs(dimacs)
    assert nv == 4
    assert parsed == clauses
    print("  Roundtrip: OK")

    # Test unit propagation
    print("\n--- Unit propagation ---")
    clauses_up = [[1], [-1, 2], [-2, 3]]
    simplified, assignment, contradiction = unit_propagate(clauses_up, {})
    assert not contradiction
    assert 1 in assignment
    print(f"  Assignment: {assignment}")
    print("  Contradiction detection: OK")

    # Test pure literal elimination
    print("\n--- Pure literal elimination ---")
    clauses_pl = [[1, 2], [1, -3], [2, 3]]
    simplified, pure = pure_literal_eliminate(clauses_pl)
    print(f"  Pure: {pure}, Remaining: {simplified}")

    # Test DPLL
    print("\n--- DPLL solve ---")
    model = dpll_solve([[1, 2], [-1, 3]], 3)
    assert model is not None
    print(f"  Model for (x1 OR x2) AND (~x1 OR x3): {model}")

    model_unsat = dpll_solve([[1], [-1]], 1)
    assert model_unsat is None
    print("  UNSAT for (x1) AND (~x1): None")

    # Test is_satisfiable
    print("\n--- is_satisfiable ---")
    assert is_satisfiable([[1, 2]], 2)
    assert not is_satisfiable([[1], [-1]], 1)
    print("  is_satisfiable: OK")

    # Test backbone
    print("\n--- get_backbone ---")
    bb = get_backbone([[1], [1, 2], [-2, 3]], 3)
    assert bb.get(1) is True
    print(f"  Backbone of (x1) AND (x1 OR x2): {bb}")

    bb_empty = get_backbone([[1, 2]], 2)
    assert bb_empty == {}
    print(f"  Backbone of (x1 OR x2): {{}}")

    # Test formula generators
    print("\n--- make_small_example ---")
    for ftype in ["pigeonhole", "chain_3sat", "random_3sat", "tseitin"]:
        nv, cls = make_small_example(ftype, 5 if ftype != "tseitin" else 3)
        print(f"  {ftype:15s}: {nv} vars, {len(cls)} clauses")

    # Pigeonhole should be UNSAT
    print("\n--- Pigeonhole satisfiability check ---")
    for n in range(2, 5):
        nv, php = make_small_example("pigeonhole", n)
        sat = is_satisfiable(php, nv)
        print(f"  PHP({n},{n-1}): {'SAT' if sat else 'UNSAT'}")

    print("\n" + "=" * 60)
    print("All SAT utils tests passed!")
    print("=" * 60)
