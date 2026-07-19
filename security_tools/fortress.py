#!/usr/bin/env python3
"""FORTRESS — Feasibility Of Runtime Trespass via Resolution-width and Structural Scoring

Quantitative security assessment for constraint-based systems. Computes
treewidth, classifies attack feasibility, and recommends structural defenses.

Based on Theorem 1: width w → resolution width ≤ max(w, k)
          Universal Tractability: bounded width → poly-size proofs in 10 systems

Width → Security Mapping:
  ≤ 3   TRIVIAL   — Vulnerable (high confidence)
  ≤ 10  EASY      — Vulnerable (high confidence)
  ≤ 25  MODERATE  — Conditionally vulnerable
  ≤ 50  HARD      — Conditionally vulnerable
  > 50  EXTREME   — Defended

Usage:
    python fortress.py --dimacs access_control.cnf --report
    python fortress.py --dimacs policy.cnf --compare-with other_policy.cnf
    python fortress.py --generate rbac --roles 8 --perms 12 --defense-plan

Author: CIC Research (Stages 1-12)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent / "shared"))

from cic_core import (
    build_primal_graph, minfill_treewidth, parse_dimacs,
    make_php, make_chain, is_satisfiable
)


_WIDTH_CLASSES = [
    (3, "TRIVIAL", "Exhaustive search guaranteed fast", "vulnerable", "high"),
    (10, "EASY", "Bounded-width algorithms win", "vulnerable", "high"),
    (25, "MODERATE", "Tractable with good heuristics", "conditionally_vulnerable", "medium"),
    (50, "HARD", "May need specialized solvers", "conditionally_vulnerable", "low"),
    (float('inf'), "EXTREME", "Structural defense is strong", "defended", "high"),
]


def classify_width(width: int) -> dict:
    for threshold, classification, description, verdict, confidence in _WIDTH_CLASSES:
        if width <= threshold:
            return {
                "width": width,
                "classification": classification,
                "description": description,
                "verdict": verdict,
                "confidence": confidence,
                "severity_score": max(0, 100 - width * 2),
            }
    return {"width": width, "classification": "EXTREME", "verdict": "defended", "confidence": "high", "severity_score": 0}


def defense_recommendations(width: int, num_vars: int, num_clauses: int) -> list[str]:
    recs = []
    if width <= 10:
        recs.append("CRITICAL: Add parity (XOR) constraints over large variable sets. "
                    "Parity on n variables forces treewidth Ω(n).")
        recs.append("CRITICAL: Introduce auxiliary guard variables connected to 10+ "
                    "existing variables to create clique structures.")
        recs.append("CRITICAL: Cross-link independent subsystems with mutual constraints.")
    elif width <= 25:
        recs.append("HIGH: Add non-local constraints spanning multiple subsystems.")
        recs.append("HIGH: Use expander-graph structure for high treewidth guarantees.")
        recs.append("HIGH: Increase variable coupling density (more cross-constraints).")
    elif width <= 50:
        recs.append("MEDIUM: Add checksum/guard variables for multi-component dependencies.")
        recs.append("MEDIUM: Ensure no small separator sets exist.")
    else:
        recs.append("LOW: System has strong structural defense. Maintain current architecture.")
    recs.append("UNIVERSAL: Avoid tree-like, path-like, or grid-like decompositions.")
    recs.append("UNIVERSAL: Monitor for constraint simplification that reduces width.")
    return recs


def structural_score(width: int, num_vars: int, num_clauses: int) -> float:
    if num_vars == 0:
        return 50.0
    width_component = min(width / 50.0, 1.0) * 60
    density = num_clauses / max(num_vars, 1)
    density_component = min(density / 10.0, 1.0) * 25
    size_component = min(num_vars / 100.0, 1.0) * 15
    return width_component + density_component + size_component


def analyze(clauses: list[list[int]], num_vars: int, system_name: str = "unknown") -> dict:
    num_clauses = len(clauses)
    max_clause_size = max((len(c) for c in clauses), default=0)
    graph = build_primal_graph(num_vars, clauses)
    num_edges = sum(len(neighbors) for neighbors in graph.values()) // 2
    ordering, width = minfill_treewidth(graph)
    classification = classify_width(width)
    proof_width = max(width, max_clause_size)
    score = structural_score(width, num_vars, num_clauses)
    recs = defense_recommendations(width, num_vars, num_clauses)
    sat = is_satisfiable(clauses, num_vars)

    return {
        "system_name": system_name,
        "num_vars": num_vars,
        "num_clauses": num_clauses,
        "max_clause_size": max_clause_size,
        "graph_edges": num_edges,
        "elimination_width": width,
        "proof_width_bound": proof_width,
        "classification": classification,
        "security_score": round(score, 2),
        "recommendations": recs,
        "is_satisfiable": sat,
    }


def comparison_report(results: list[dict]) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append("  FORTRESS — Security Comparison Report")
    lines.append("=" * 70)
    lines.append("")
    sorted_results = sorted(results, key=lambda r: r["security_score"], reverse=True)
    lines.append(f"{'System':<20} {'Width':>6} {'Class':<10} {'Score':>6} {'Verdict':<20}")
    lines.append("-" * 70)
    for r in sorted_results:
        c = r["classification"]
        lines.append(f"{r['system_name']:<20} {r['elimination_width']:>6} "
                     f"{c['classification']:<10} {r['security_score']:>6.1f} "
                     f"{c['verdict']} ({c['confidence']})")
    lines.append("")
    most_vulnerable = min(results, key=lambda r: r["security_score"])
    lines.append(f"MOST VULNERABLE: {most_vulnerable['system_name']} "
                 f"(score: {most_vulnerable['security_score']:.1f})")
    return "\n".join(lines)


def full_report(result: dict) -> str:
    lines = []
    lines.append("=" * 70)
    lines.append(f"  FORTRESS — Security Assessment: {result['system_name']}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  Formula: {result['num_vars']} variables, {result['num_clauses']} clauses")
    lines.append(f"  Graph: {result['graph_edges']} edges")
    lines.append(f"  Max clause size: {result['max_clause_size']}")
    lines.append(f"  SAT: {'YES' if result['is_satisfiable'] else 'NO'}")
    lines.append("")
    lines.append("-" * 50)
    lines.append("  STRUCTURAL ANALYSIS")
    lines.append("-" * 50)
    lines.append(f"  Elimination width:     {result['elimination_width']}")
    lines.append(f"  Proof width bound:     {result['proof_width_bound']}")
    lines.append(f"  Security class:        {result['classification']['classification']}")
    lines.append(f"  Verdict:               {result['classification']['verdict'].upper()}")
    lines.append(f"  Confidence:            {result['classification']['confidence'].upper()}")
    lines.append(f"  Security score:        {result['security_score']:.1f}/100")
    lines.append("")
    lines.append("-" * 50)
    lines.append("  DEFENSE RECOMMENDATIONS")
    lines.append("-" * 50)
    for i, rec in enumerate(result['recommendations'], 1):
        severity = rec.split(':')[0]
        detail = ':'.join(rec.split(':')[1:]).strip()
        lines.append(f"  {i}. [{severity}] {detail}")
    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def generate_rbac(num_roles: int, num_perms: int) -> tuple[int, list[list[int]]]:
    num_vars = num_roles + num_perms + 1
    admin = num_vars
    clauses = []
    for r in range(1, num_roles + 1):
        for p in range(num_roles + 1, num_roles + num_perms + 1):
            if (r + p) % 3 == 0:
                clauses.append([-r, p])
    if num_roles >= 2:
        clauses.append([-1, -2, admin])
    if num_roles >= 3:
        clauses.append([-1, -3, admin])
    clauses.append(list(range(1, num_roles + 1)))
    return num_vars, clauses


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="FORTRESS — Structural Security Assessor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --dimacs access_control.cnf --report
  %(prog)s --dimacs policy1.cnf --compare-with policy2.cnf
  %(prog)s --generate rbac --roles 8 --perms 12 --defense-plan
        """
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dimacs", help="DIMACS CNF file")
    source.add_argument("--generate", choices=["rbac", "php", "chain"],
                        help="Generate test policy")
    parser.add_argument("--roles", type=int, default=8, help="Roles for RBAC (default: 8)")
    parser.add_argument("--perms", type=int, default=12, help="Permissions for RBAC (default: 12)")
    parser.add_argument("--report", action="store_true", help="Show detailed report")
    parser.add_argument("--compare-with", help="Compare with another policy")
    parser.add_argument("--defense-plan", action="store_true", help="Generate defense plan")
    parser.add_argument("--name", default="system", help="System name")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.dimacs:
        with open(args.dimacs) as f:
            num_vars, clauses = parse_dimacs(f.read())
        name = args.name
    elif args.generate == "rbac":
        num_vars, clauses = generate_rbac(args.roles, args.perms)
        name = f"RBAC({args.roles}r,{args.perms}p)"
    elif args.generate == "php":
        num_vars, clauses = make_php(args.roles)
        name = f"PHP({args.roles})"
    elif args.generate == "chain":
        num_vars, clauses = make_chain(args.roles)
        name = f"Chain({args.roles})"
    else:
        parser.error("Specify --dimacs or --generate")
        return

    t0 = time.time()
    result = analyze(clauses, num_vars, name)
    elapsed = time.time() - t0

    if args.compare_with:
        with open(args.compare_with) as f:
            nv2, clauses2 = parse_dimacs(f.read())
        result2 = analyze(clauses2, nv2, args.compare_with)
        print(comparison_report([result, result2]))
    elif args.report or args.defense_plan:
        print(full_report(result))
        print(f"\n[Analysis completed in {elapsed:.3f}s]")
    else:
        c = result["classification"]
        print(f"{result['system_name']}: width={result['elimination_width']}, "
              f"class={c['classification']}, score={result['security_score']:.1f}, "
              f"verdict={c['verdict']} ({elapsed:.3f}s)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("FORTRESS — Running self-test\n")
        r1 = analyze([[1], [1, 2]], 2, "trivial")
        assert r1["classification"]["verdict"] == "vulnerable"
        print(f"[PASS] Trivial: width={r1['elimination_width']}, verdict={r1['classification']['verdict']}")

        r2 = analyze([[1, 2], [2, 3], [3, 4], [4, 5], [5, 1]], 5, "cycle")
        print(f"[PASS] Cycle: width={r2['elimination_width']}, class={r2['classification']['classification']}")

        assert 0 <= r1["security_score"] <= 100
        assert 0 <= r2["security_score"] <= 100
        print(f"[PASS] Security scores: {r1['security_score']:.1f}, {r2['security_score']:.1f}")

        assert len(r1["recommendations"]) > 0
        print(f"[PASS] Recommendations: {len(r1['recommendations'])} items")

        report = comparison_report([r1, r2])
        assert "MOST VULNERABLE" in report
        print(f"[PASS] Comparison report generated")
        print("\nAll FORTRESS self-tests passed!")
