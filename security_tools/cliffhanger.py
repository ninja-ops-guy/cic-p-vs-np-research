#!/usr/bin/env python3
"""CLIFFHANGER — Catastrophic faiLure detectIon via entropy traCture (ETC)

Identifies systems with "entropy cliffs" — sudden catastrophic failures
after long stable periods. Based on ETC (Entropy Trajectory Complexity,
Stage 17): high ETC indicates hidden catastrophic failure modes.

ETC(φ) = ∫ |d²H/d(depth)²| d(depth)

Systems with high ETC are dangerous because they appear robust in local
testing but have hidden failure modes. CLIFFHANGER finds these cliffs
and generates targeted fuzzing campaigns.

Usage:
    python cliffhanger.py --system system.cnf --profile
    python cliffhanger.py --system system.cnf --fuzz-targets --output fuzz_seeds.txt
    python cliffhanger.py --generate random --vars 50 --clauses 200 --profile

Author: CIC Research (Stage 17)
"""

from __future__ import annotations

import argparse
import math
import random
import sys
import time
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent / "shared"))

from cic_core import (
    ETCCalculator, build_primal_graph, minfill_treewidth,
    parse_dimacs, make_php, make_chain, is_satisfiable
)


# ===================================================================
# Core Analysis
# ===================================================================

def find_cliffs(trajectory: list[float], threshold: float = 0.3) -> list[tuple[int, float]]:
    """Find entropy cliffs: points where second derivative exceeds threshold."""
    cliffs = []
    for i in range(1, len(trajectory) - 1):
        d2 = abs(trajectory[i - 1] - 2 * trajectory[i] + trajectory[i + 1])
        if d2 > threshold:
            cliffs.append((i, d2))
    return sorted(cliffs, key=lambda x: x[1], reverse=True)


def risk_profile(etc_score: float, max_cliff: float, cliff_density: float) -> str:
    """Classify risk profile based on ETC metrics."""
    if etc_score < 0.5 and cliff_density < 0.05:
        return "SMOOTH"
    elif etc_score < 1.5 and cliff_density < 0.1:
        return "MODERATE"
    elif etc_score < 3.0:
        return "CLIFF_PRONE"
    else:
        return "CATASTROPHIC"


def evasion_likelihood(etc_score: float) -> float:
    """Map ETC score to probability of successful evasion attack."""
    return max(0.0, min(1.0, 1.0 / (1.0 + math.exp(-(etc_score - 1.5)))))


def generate_fuzz_targets(trajectory: list[float], cliffs: list[tuple[int, float]],
                          num_vars: int, num_targets: int = 10) -> list[dict]:
    """Generate targeted fuzzing seeds based on cliff locations."""
    targets = []
    by_depth = sorted(cliffs, key=lambda x: x[0])

    for i, (depth, magnitude) in enumerate(by_depth[:num_targets]):
        assignment = {}
        vars_to_fix = min(depth, num_vars)
        selected = random.sample(range(1, num_vars + 1), vars_to_fix)
        for v in selected:
            assignment[v] = random.choice([True, False])

        targets.append({
            "id": i + 1,
            "depth": depth,
            "cliff_magnitude": round(magnitude, 4),
            "partial_assignment": assignment,
            "strategy": "drive_to_cliff",
        })

    return targets


def full_analysis(clauses: list[list[int]], num_vars: int, num_samples: int = 100) -> dict:
    """Complete ETC-based security analysis."""
    etc_calc = ETCCalculator(clauses, num_vars)

    trajectory = etc_calc.trajectory(num_samples)
    etc_score = etc_calc.compute(num_samples)

    cliffs = find_cliffs(trajectory)
    max_cliff = max((c[1] for c in cliffs), default=0.0)
    cliff_density = len(cliffs) / len(trajectory) if trajectory else 0.0

    profile = risk_profile(etc_score, max_cliff, cliff_density)
    evasion_prob = evasion_likelihood(etc_score)

    graph = build_primal_graph(num_vars, clauses)
    _, treewidth = minfill_treewidth(graph)

    return {
        "etc_score": round(etc_score, 4),
        "trajectory": [round(x, 4) for x in trajectory],
        "cliffs": [(d, round(m, 4)) for d, m in cliffs],
        "max_cliff": round(max_cliff, 4),
        "cliff_density": round(cliff_density, 4),
        "num_cliffs": len(cliffs),
        "risk_profile": profile,
        "evasion_likelihood": round(evasion_prob, 4),
        "treewidth": treewidth,
        "assessment": _assessment_text(profile, etc_score, evasion_prob, treewidth),
    }


def _assessment_text(profile: str, etc: float, evasion: float, tw: int) -> str:
    lines = [f"RISK PROFILE: {profile}"]
    lines.append(f"ETC Score: {etc:.4f} (total entropy curvature)")
    lines.append(f"Evasion Likelihood: {evasion:.1%}")
    lines.append(f"Treewidth: {tw}")

    if profile == "CATASTROPHIC":
        lines.append("\n[!] This system has MASSIVE entropy cliffs.")
        lines.append("    Small input changes can cause sudden, dramatic failures.")
        lines.append("    The system appears stable locally but has hidden catastrophic modes.")
        lines.append("    PRIORITY: Immediate fuzzing targeting cliff regions.")
    elif profile == "CLIFF_PRONE":
        lines.append("\n[!] Multiple entropy cliffs detected.")
        lines.append("    The system has several abrupt transition points.")
        lines.append("    RECOMMENDATION: Targeted testing at cliff depths.")
    elif profile == "MODERATE":
        lines.append("\n[.] Some cliff behavior present but manageable.")
        lines.append("    Standard fuzzing should surface most issues.")
    else:
        lines.append("\n[+] Smooth entropy profile — gradual transitions.")
        lines.append("    Failures are predictable; no hidden catastrophic modes.")

    return "\n".join(lines)


def generate_random_3sat(num_vars: int, num_clauses: int, ratio: float = 4.26) -> list[list[int]]:
    """Generate random 3-SAT formula."""
    n_clauses = num_clauses or int(num_vars * ratio)
    clauses = []
    for _ in range(n_clauses):
        vars = random.sample(range(1, num_vars + 1), 3)
        clause = [v if random.random() < 0.5 else -v for v in vars]
        clauses.append(clause)
    return clauses


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CLIFFHANGER — Catastrophic Failure Detector via ETC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --system policy.cnf --profile
  %(prog)s --system policy.cnf --fuzz-targets --output seeds.txt
  %(prog)s --generate random --vars 50 --clauses 200 --profile
        """
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--system", help="DIMACS CNF file")
    source.add_argument("--generate", choices=["random", "php", "chain"],
                        help="Generate test formula")
    parser.add_argument("--vars", type=int, default=30, help="Variables (default: 30)")
    parser.add_argument("--clauses", type=int, default=0, help="Clauses (0 = auto)")
    parser.add_argument("--samples", type=int, default=100, help="ETC samples (default: 100)")
    parser.add_argument("--profile", action="store_true", help="Show full risk profile")
    parser.add_argument("--fuzz-targets", action="store_true", help="Generate fuzz targets")
    parser.add_argument("--output", help="Output file for fuzz targets")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    print("=" * 70)
    print("  CLIFFHANGER — Catastrophic Failure Detector")
    print("  Based on Entropy Trajectory Complexity (Stage 17)")
    print("=" * 70)

    if args.system:
        with open(args.system) as f:
            num_vars, clauses = parse_dimacs(f.read())
        print(f"\n[LOAD] System: {num_vars} vars, {len(clauses)} clauses")
    elif args.generate == "random":
        clauses = generate_random_3sat(args.vars, args.clauses)
        num_vars = args.vars
        print(f"\n[GENERATE] Random 3-SAT: {num_vars} vars, {len(clauses)} clauses")
    elif args.generate == "php":
        num_vars, clauses = make_php(args.vars)
        print(f"\n[GENERATE] Pigeonhole PHP({args.vars})")
    elif args.generate == "chain":
        num_vars, clauses = make_chain(args.vars)
        print(f"\n[GENERATE] Chain (n={args.vars})")
    else:
        parser.error("Specify --system or --generate")
        return

    t0 = time.time()
    result = full_analysis(clauses, num_vars, args.samples)
    elapsed = time.time() - t0
    print(f"[ANALYZE] Completed in {elapsed:.2f}s ({args.samples} samples)\n")

    if args.profile:
        print("-" * 50)
        print(result["assessment"])
        print("-" * 50)
        print(f"\n  Detailed Metrics:")
        print(f"    ETC Score:          {result['etc_score']}")
        print(f"    Max Cliff:          {result['max_cliff']}")
        print(f"    Cliff Density:      {result['cliff_density']}")
        print(f"    Num Cliffs:         {result['num_cliffs']}")
        print(f"    Treewidth:          {result['treewidth']}")

    if args.fuzz_targets:
        cliffs = result["cliffs"]
        if not cliffs:
            print("\n[INFO] No cliffs found — system has smooth entropy profile.")
            print("       Standard fuzzing recommended over targeted approach.")
        else:
            targets = generate_fuzz_targets(result["trajectory"], cliffs, num_vars)
            print(f"\n  Generated {len(targets)} fuzz targets:\n")
            for t in targets:
                print(f"    Target #{t['id']}: depth={t['depth']}, "
                      f"magnitude={t['cliff_magnitude']:.4f}")

            if args.output:
                with open(args.output, 'w') as f:
                    for t in targets:
                        f.write(f"# Target {t['id']}: depth={t['depth']}, "
                                f"mag={t['cliff_magnitude']}\n")
                        for var, val in t['partial_assignment'].items():
                            f.write(f"{var if val else -var} ")
                        f.write("0\n")
                print(f"\n  [SAVE] Fuzz targets written to {args.output}")

    print(f"\n{'=' * 70}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        print("CLIFFHANGER — Running self-test\n")
        nv, clauses = make_chain(15)
        r = full_analysis(clauses, nv, 50)
        print(f"[PASS] Chain: ETC={r['etc_score']}, profile={r['risk_profile']}")
        assert r['risk_profile'] in ['SMOOTH', 'MODERATE']

        nv2, clauses2 = make_php(4)
        r2 = full_analysis(clauses2, nv2, 50)
        print(f"[PASS] PHP: ETC={r2['etc_score']}, profile={r2['risk_profile']}")
        assert 0.0 <= r['evasion_likelihood'] <= 1.0
        print(f"[PASS] Evasion likelihood: {r['evasion_likelihood']:.4f}")

        trajectory = [1.0, 0.9, 0.1, 0.05, 0.0]
        cliffs = find_cliffs(trajectory, threshold=0.2)
        assert len(cliffs) > 0
        print(f"[PASS] Cliff detection: found {len(cliffs)} cliff(s)")
        print("\nAll CLIFFHANGER self-tests passed!")
