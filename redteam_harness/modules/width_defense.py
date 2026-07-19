"""Treewidth-Based Attack Feasibility Analyzer

Based on CIC framework research:
- Bounded treewidth => polynomial-time proofs (Theorem 1)
- MinFill heuristic with proven approximation bounds
- Universal Tractability across 10 proof systems

This module assesses whether a target system is structurally
vulnerable to exhaustive red team analysis.
"""

from __future__ import annotations

from typing import Optional

try:
    from .structural_sat import analyze_structure
except ImportError:
    from structural_sat import analyze_structure


# ---------------------------------------------------------------------------
# Classification constants (from empirical CIC research)
# ---------------------------------------------------------------------------

_WIDTH_CLASSIFICATIONS = [
    (3, "TRIVIAL", "Exhaustive search guaranteed fast"),
    (10, "EASY", "Bounded-width algorithms win"),
    (25, "MODERATE", "Tractable with good heuristics"),
    (50, "HARD", "May need specialized solvers"),
    (float("inf"), "EXTREME", "Structural defense is strong"),
]


# ---------------------------------------------------------------------------
# AttackFeasibilityAnalyzer
# ---------------------------------------------------------------------------

class AttackFeasibilityAnalyzer:
    """Analyze whether a system is structurally vulnerable to attack.

    The core insight from CIC research: low treewidth means the
    constraint graph has a simple tree-like structure, which makes
    exhaustive analysis tractable. High treewidth means the graph
    is highly interconnected, providing structural defense.
    """

    def __init__(self):
        self.results: list[dict] = []

    def analyze_constraint_system(
        self,
        constraints: list[list[int]],
        num_vars: int,
        system_name: str = "unknown",
    ) -> dict:
        """Analyze a constraint system for attack feasibility.

        Computes treewidth, elimination width, and classifies
        the system by difficulty.

        Args:
            constraints: CNF constraint system.
            num_vars: Number of variables.
            system_name: Optional name for reporting.

        Returns:
            Dict with width, difficulty, feasibility verdict, recommendations.
        """
        structure = analyze_structure(constraints, num_vars)
        width = structure["elimination_width"]
        difficulty = structure["difficulty"]

        verdict = self.verdict(width, num_vars)
        recommendations = self.defense_recommendation(width, num_vars)

        result = {
            "system_name": system_name,
            "structure": structure,
            "width_classification": structure["difficulty"].upper(),
            "verdict": verdict,
            "recommendations": recommendations,
            "relative_score": self._compute_score(width, num_vars),
        }
        self.results.append(result)
        return result

    def verdict(self, width: int, num_vars: int) -> dict:
        """Produce a red-team feasibility verdict.

        Width classifications (based on our research):
        - w <= 3:   TRIVIAL — exhaustive search guaranteed fast
        - w <= 10:  EASY — bounded-width algorithms win
        - w <= 25:  MODERATE — tractable with good heuristics
        - w <= 50:  HARD — may need specialized solvers
        - w > 50:   EXTREME — structural defense is strong

        Args:
            width: Estimated elimination width.
            num_vars: Number of variables.

        Returns dict:
        - verdict: 'vulnerable' | 'conditionally_vulnerable' | 'defended'
        - confidence: 'high' | 'medium' | 'low'
        - reasoning: str
        - recommended_budget: str
        - alternative_approaches: list[str]
        """
        for threshold, classification, description in _WIDTH_CLASSIFICATIONS:
            if width <= threshold:
                break

        if width <= 10:
            return {
                "verdict": "vulnerable",
                "confidence": "high",
                "reasoning": (
                    f"Width {width} is extremely low. The constraint graph is nearly "
                    f"tree-like. Bounded-width dynamic programming or even brute-force "
                    f"enumeration will succeed in polynomial time. The system offers "
                    f"essentially no structural defense."
                ),
                "recommended_budget": "Minimal — hours to days for full analysis",
                "alternative_approaches": [
                    "direct_sat",
                    "enumeration",
                    "dp_on_decomposition",
                ],
            }
        elif width <= 25:
            return {
                "verdict": "conditionally_vulnerable",
                "confidence": "medium",
                "reasoning": (
                    f"Width {width} is moderate. Modern SAT heuristics (VSIDS, phase "
                    f"saving) combined with structural decomposition may succeed, but "
                    f"runtime is less predictable. The system has some structural "
                    f"defense but is not strongly protected."
                ),
                "recommended_budget": "Moderate — weeks to months",
                "alternative_approaches": [
                    "parallel_sat",
                    "structural_decomposition",
                    "smt",
                ],
            }
        elif width <= 50:
            return {
                "verdict": "conditionally_vulnerable",
                "confidence": "low",
                "reasoning": (
                    f"Width {width} is high. The constraint graph is densely "
                    f"interconnected. Exhaustive analysis faces significant "
                    f"structural barriers. Success requires either specialized "
                    f"solvers or structural simplification."
                ),
                "recommended_budget": "High — months to years",
                "alternative_approaches": [
                    "symmetry_breaking",
                    "preprocessing",
                    "hybrid_approaches",
                ],
            }
        else:
            return {
                "verdict": "defended",
                "confidence": "high",
                "reasoning": (
                    f"Width {width} is very high. The constraint graph has "
                    f"expander-like properties. Treewidth-based approaches are "
                    f"theoretically infeasible. The system has strong structural "
                    f"defense against exhaustive analysis."
                ),
                "recommended_budget": "Not recommended — try alternative approaches",
                "alternative_approaches": [
                    "fuzzing",
                    "symbolic_execution",
                    "manual_analysis",
                ],
            }

    def compare_systems(
        self,
        systems: list[tuple[str, list[list[int]], int]],
    ) -> list[dict]:
        """Compare multiple systems and rank by vulnerability.

        Args:
            systems: List of (name, constraints, num_vars) tuples.

        Returns sorted list from most to least vulnerable.
        """
        results = []
        for name, constraints, nv in systems:
            result = self.analyze_constraint_system(constraints, nv, name)
            results.append(result)

        # Sort by relative_score descending (most vulnerable first)
        results.sort(key=lambda r: r["relative_score"], reverse=True)
        return results

    def defense_recommendation(self, width: int, num_vars: int) -> list[str]:
        """Recommend structural defenses to increase width.

        Based on our research:
        1. Increase variable coupling (more cross-constraints)
        2. Add parity/checksum constraints (increase treewidth)
        3. Use expander-graph structure (proven high treewidth)
        4. Introduce auxiliary variables that create cliques

        Args:
            width: Current elimination width.
            num_vars: Number of variables.

        Returns:
            List of recommendation strings.
        """
        recs = []

        if width <= 10:
            recs.append(
                "CRITICAL: Add parity constraints (XOR clauses) over large variable sets. "
                "Parity constraints on n variables force treewidth Ω(n) in the worst case."
            )
            recs.append(
                "CRITICAL: Introduce auxiliary check variables connected to 10+ "
                "existing variables each. Each such variable creates a clique-like "
                "structure in the primal graph."
            )
        elif width <= 25:
            recs.append(
                "HIGH: Add checksum/guard variables that depend on multiple independent "
                "state components. This creates high-fill edges."
            )
            recs.append(
                "HIGH: Cross-link previously independent subsystems with mutual constraints. "
                "Merging components raises treewidth."
            )
        elif width <= 50:
            recs.append(
                "MEDIUM: Add non-local constraints that span multiple subsystems. "
                "Long-range dependencies increase treewidth."
            )

        # Universal recommendations
        recs.append(
            "UNIVERSAL: Avoid constraint patterns that decompose cleanly — "
            "tree-like, path-like, or grid-like structures have low treewidth."
        )
        recs.append(
            "UNIVERSAL: Ensure no small separator sets exist. A separator of size k "
            "implies treewidth ≥ k; keep all separators large."
        )

        return recs

    def _compute_score(self, width: int, num_vars: int) -> float:
        """Compute a vulnerability score (0-100, higher = more vulnerable)."""
        if num_vars == 0:
            return 50.0
        # Lower width / more variables = higher score
        width_ratio = 1.0 - min(width / 50.0, 1.0)
        size_factor = min(num_vars / 100.0, 1.0)
        return (width_ratio * 0.7 + size_factor * 0.3) * 100


# ---------------------------------------------------------------------------
# quick_assess
# ---------------------------------------------------------------------------

def quick_assess(dimacs_string: str) -> dict:
    """One-shot assessment from DIMACS string.

    Parse, analyze structure, return verdict.

    Args:
        dimacs_string: DIMACS CNF formula as string.

    Returns:
        Analysis result dict.
    """
    from utils.sat_utils import parse_dimacs

    num_vars, clauses = parse_dimacs(dimacs_string)
    analyzer = AttackFeasibilityAnalyzer()
    return analyzer.analyze_constraint_system(clauses, num_vars)


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Width Defense — Self-Test")
    print("=" * 60)

    # Test verdicts
    print("\n--- verdict tests ---")
    analyzer = AttackFeasibilityAnalyzer()
    v_trivial = analyzer.verdict(2, 10)
    assert v_trivial["verdict"] == "vulnerable"
    assert v_trivial["confidence"] == "high"
    print(f"  Width 2: {v_trivial['verdict']} ({v_trivial['confidence']})")

    v_extreme = analyzer.verdict(60, 100)
    assert v_extreme["verdict"] == "defended"
    print(f"  Width 60: {v_extreme['verdict']} ({v_extreme['confidence']})")

    # Test compare_systems
    print("\n--- compare_systems ---")
    systems = [
        ("SimpleAuth", [[1], [1, 2]], 2),
        ("ComplexAuth", [[1, 2], [2, 3], [3, 4], [4, 5]], 5),
        ("CryptoModule", [[1, 2, 3], [2, 3, 4], [3, 4, 5], [1, 5]], 5),
    ]
    results = analyzer.compare_systems(systems)
    for r in results:
        print(f"  {r['system_name']:15s}: width={r['structure']['elimination_width']:3d} "
              f"score={r['relative_score']:.1f}")

    # Test defense recommendations
    print("\n--- defense_recommendation ---")
    recs = analyzer.defense_recommendation(5, 20)
    for rec in recs[:3]:
        print(f"  - {rec[:70]}...")

    print("\n" + "=" * 60)
    print("All width defense tests passed!")
    print("=" * 60)
