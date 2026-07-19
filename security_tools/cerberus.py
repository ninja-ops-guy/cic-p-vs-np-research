#!/usr/bin/env python3
"""CERBERUS — Constraint-driven Exploit Research via Bounded-width Enumeration
            and Resolution for Unsatisfiability Search

Finds concrete attack traces from an initial state to a violation within
a bounded number of steps. Leverages the CIC Universal Tractability theorem:
bounded treewidth → polynomial-size proofs → tractable BMC.

Based on: Theorem 1 (width w → res-width ≤ max(w, k))
          Universal Tractability (10 proof systems, Stages 5-8)
          Bounded treewidth BMC (Stage 2)

Usage:
    python cerberus.py --transition tx.cnf --initial init.cnf --bad bad.cnf --bound 10
    python cerberus.py --generate auth_bypass --steps 5 --find-attack
    python cerberus.py --transition tx.cnf --initial init.cnf --bad bad.cnf --bound 10 --structural-check

Author: CIC Research (Stages 1-8)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent / "shared"))

from cic_core import (
    dpll_solve, is_satisfiable, build_primal_graph, minfill_treewidth,
    parse_dimacs, make_php, make_chain, to_dimacs
)


# ===================================================================
# Bounded Model Checker
# ===================================================================

class BoundedModelChecker:
    """BMC for finding bounded attack traces."""

    def __init__(self):
        self.all_clauses: list[list[int]] = []
        self.var_map: dict[str, int] = {}
        self.next_var_id = 1

    def _fresh_var(self, name: str) -> int:
        if name in self.var_map:
            return self.var_map[name]
        vid = self.next_var_id
        self.var_map[name] = vid
        self.next_var_id += 1
        return vid

    def encode_bmc(
        self,
        num_state_vars: int,
        initial: list[list[int]],
        transition: list[list[int]],
        bad_state: list[list[int]],
        bound: int,
    ) -> tuple[int, list[list[int]]]:
        """Encode BMC problem as single CNF."""
        clauses: list[list[int]] = []

        def var_at(step: int, state_var: int) -> int:
            return step * num_state_vars + state_var

        total_vars = (bound + 1) * num_state_vars

        for clause in initial:
            new_clause = [var_at(0, abs(lit)) if lit > 0 else -var_at(0, abs(lit))
                          for lit in clause]
            clauses.append(new_clause)

        for step in range(bound):
            for clause in transition:
                new_clause = []
                for lit in clause:
                    var = abs(lit)
                    is_next = lit < 0
                    actual_lit = lit if not is_next else -lit
                    if is_next:
                        new_clause.append(var_at(step + 1, abs(actual_lit))
                                          if actual_lit > 0 else
                                          -var_at(step + 1, abs(actual_lit)))
                    else:
                        new_clause.append(var_at(step, var)
                                          if lit > 0 else -var_at(step, var))
                clauses.append(new_clause)

        for clause in bad_state:
            new_clause = [var_at(bound, abs(lit)) if lit > 0 else -var_at(bound, abs(lit))
                          for lit in clause]
            clauses.append(new_clause)

        return total_vars, clauses

    def extract_trace(self, model: dict[int, bool], num_state_vars: int, bound: int) -> list[dict[int, bool]]:
        """Extract state sequence from model."""
        trace = []
        for step in range(bound + 1):
            state = {}
            for v in range(1, num_state_vars + 1):
                var_id = step * num_state_vars + v
                if var_id in model:
                    state[v] = model[var_id]
            trace.append(state)
        return trace


def structural_check(clauses: list[list[int]], num_vars: int, bound: int) -> dict:
    """Check if BMC is structurally tractable."""
    graph = build_primal_graph(num_vars, clauses)
    _, width = minfill_treewidth(graph)
    estimated_width = min(width, num_vars)
    classification = "tractable" if estimated_width <= 25 else "challenging" if estimated_width <= 50 else "intractable"
    return {
        "unrolled_vars": num_vars,
        "elimination_width": width,
        "estimated_width": estimated_width,
        "classification": classification,
        "bmc_bound": bound,
    }


def generate_auth_bypass_transition(num_roles: int = 4) -> tuple[int, list[list[int]], list[list[int]], list[list[int]]]:
    """Generate a simple authentication bypass example.

    State variables:
        1: logged_in
        2: has_token
        3: is_admin
        4: bypass_active
    """
    num_vars = 4
    initial = [[-1], [-2], [-3], [-4]]
    transition = [
        [-3, 2],
        [-2, 1],
        [4, -3],
        [-4, 3],
        [-1, 1],
    ]
    bad_state = [[3]]
    return num_vars, initial, transition, bad_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CERBERUS — Bounded Exploit Path Discovery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --transition tx.cnf --initial init.cnf --bad bad.cnf --bound 10
  %(prog)s --generate auth_bypass --steps 5 --find-attack
  %(prog)s --transition tx.cnf --initial init.cnf --bad bad.cnf --bound 10 --structural-check
        """
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--transition", help="DIMACS CNF for transition relation")
    source.add_argument("--generate", choices=["auth_bypass"],
                        help="Generate example transition system")
    parser.add_argument("--initial", help="DIMACS CNF for initial state")
    parser.add_argument("--bad", help="DIMACS CNF for bad state predicate")
    parser.add_argument("--bound", type=int, default=5, help="BMC bound (default: 5)")
    parser.add_argument("--find-attack", action="store_true", help="Find concrete attack trace")
    parser.add_argument("--structural-check", action="store_true", help="Check structural tractability")
    parser.add_argument("--steps", type=int, default=5, help="Steps for generated example")
    parser.add_argument("--timeout", type=float, default=30.0, help="Solver timeout (default: 30s)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    print("=" * 70)
    print("  CERBERUS — Bounded Exploit Path Discovery")
    print("  Based on Universal Tractability + BMC")
    print("=" * 70)

    if args.generate == "auth_bypass":
        print("\n[GENERATE] Authentication bypass example")
        num_vars, initial, transition, bad_state = generate_auth_bypass_transition()
        bound = args.steps
    elif args.transition and args.initial and args.bad:
        with open(args.initial) as f:
            _, initial = parse_dimacs(f.read())
        with open(args.transition) as f:
            _, transition = parse_dimacs(f.read())
        with open(args.bad) as f:
            _, bad_state = parse_dimacs(f.read())
        num_vars = max((abs(lit) for c in initial for lit in c), default=1)
        bound = args.bound
    else:
        parser.error("Need --transition, --initial, --bad OR --generate")
        return

    print(f"[SETUP] {num_vars} state vars, bound={bound}")

    bmc = BoundedModelChecker()
    total_vars, clauses = bmc.encode_bmc(num_vars, initial, transition, bad_state, bound)
    print(f"[ENCODE] {total_vars} total vars, {len(clauses)} clauses")

    if args.structural_check:
        struct = structural_check(clauses, total_vars, bound)
        print(f"\n[STRUCTURAL] Width: {struct['elimination_width']}")
        print(f"             Classification: {struct['classification']}")

    t0 = time.time()
    model = dpll_solve(clauses, total_vars, timeout=args.timeout)
    elapsed = time.time() - t0

    if model is not None:
        print(f"\n[!] ATTACK FOUND in {elapsed:.2f}s")
        print(f"    Bound: {bound} steps")
        trace = bmc.extract_trace(model, num_vars, bound)
        print(f"\n    Attack Trace:")
        for i, state in enumerate(trace):
            vars_str = ", ".join(f"x{k}={'T' if v else 'F'}" for k, v in sorted(state.items()))
            print(f"      Step {i}: {vars_str}")

        for shorter_bound in range(1, bound):
            sv, sc = bmc.encode_bmc(num_vars, initial, transition, bad_state, shorter_bound)
            if dpll_solve(sc, sv, timeout=args.timeout / 2) is not None:
                print(f"\n    [INFO] Attack also possible in {shorter_bound} steps (shorter)")
                break
    else:
        print(f"\n[+] NO ATTACK within {bound} steps ({elapsed:.2f}s)")
        print(f"    System is safe up to bound {bound}.")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("CERBERUS — Running self-test\n")
        nv, initial, transition, bad = generate_auth_bypass_transition()
        bmc = BoundedModelChecker()
        tv, clauses = bmc.encode_bmc(nv, initial, transition, bad, 5)
        model = dpll_solve(clauses, tv, timeout=10.0)
        assert model is not None, "Auth bypass should be found"
        print("[PASS] Attack trace found for auth bypass")

        trace = bmc.extract_trace(model, nv, 5)
        assert len(trace) == 6
        assert trace[-1].get(3, False), "Final state should be admin"
        print(f"[PASS] Final state: admin={trace[-1].get(3)}")

        struct = structural_check(clauses, tv, 5)
        assert "classification" in struct
        print(f"[PASS] Structural classification: {struct['classification']}")

        tv2, clauses2 = bmc.encode_bmc(nv, initial, transition, [[-3]], 5)
        model2 = dpll_solve(clauses2, tv2, timeout=10.0)
        assert model2 is not None, "Non-admin trace should exist"
        print("[PASS] Non-attack trace verified")
        print("\nAll CERBERUS self-tests passed!")
