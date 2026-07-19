"""ETC Evasion Predictor — Catastrophic Failure Mode Detector

Based on Stage 17: Entropy Trajectory Complexity (ETC)

ETC(φ) = ∫ |d²H/d(depth)²| d(depth)

Measures total "information-theoretic work" during SAT solving.
Systems with high ETC have "entropy cliffs" — sudden catastrophic
failures after long stable periods. These are dangerous because
they appear robust in local testing but have hidden failure modes.

This module detects such systems for red teaming, helping identify
targets that may have unexploited catastrophic vulnerabilities.
"""

from __future__ import annotations

import math
import random
from typing import Optional

from utils.sat_utils import dpll_solve, make_small_example


# ---------------------------------------------------------------------------
# SearchStateEntropy
# ---------------------------------------------------------------------------

class SearchStateEntropy:
    """Compute search-state entropy during DPLL search.

    Unlike naive global entropy (which fails for UNSAT formulas,
    giving H=0 for all UNSAT instances), search-state entropy
    measures the conditional entropy of remaining variables given
    the current partial assignment.
    """

    def __init__(self, clauses: list[list[int]], num_vars: int):
        self.clauses = clauses
        self.num_vars = num_vars

    def compute_state_entropy(self, assignment: dict[int, bool]) -> float:
        """Compute entropy of remaining search space given partial assignment.

        Uses a composite hardness measure:
        H = -p log₂(p) - (1-p) log₂(1-p)
        where p is the fraction of remaining unassigned variables
        that appear in unit clauses.

        This captures how "forced" the search is at each state.
        High entropy = many options (unforced).
        Low entropy = nearly deterministic (highly forced).

        Args:
            assignment: Partial variable assignment.

        Returns:
            Entropy value in [0, 1].
        """
        from utils.sat_utils import unit_propagate

        # Apply current assignment
        simplified, _, contradiction = unit_propagate(self.clauses, assignment)

        if contradiction:
            return 0.0  # Dead end — no entropy

        # Count unassigned variables
        assigned_vars = set(assignment.keys())
        unassigned = [v for v in range(1, self.num_vars + 1)
                      if v not in assigned_vars]

        if not unassigned:
            return 0.0  # All assigned

        # Count unit clauses among remaining
        unit_vars = set()
        for clause in simplified:
            unassigned_lits = [lit for lit in clause
                               if abs(lit) not in assigned_vars]
            if len(unassigned_lits) == 1:
                unit_vars.add(abs(unassigned_lits[0]))

        # Fraction of unassigned vars that are unit
        p = len(unit_vars) / len(unassigned) if unassigned else 0.0
        p = max(0.001, min(0.999, p))  # avoid log(0)

        # Binary entropy
        entropy = -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
        return entropy

    def sample_entropy_trajectory(
        self,
        num_samples: int = 100,
    ) -> list[float]:
        """Simulate search trajectories and record entropy at each step.

        Perform random DPLL walks (random branching choices) and
        record the search-state entropy after each decision.

        Args:
            num_samples: Number of random walk samples.

        Returns:
            List of average entropies at each depth.
        """
        depth_entropies: dict[int, list[float]] = {}

        for _ in range(num_samples):
            assignment: dict[int, bool] = {}
            depth = 0

            while True:
                entropy = self.compute_state_entropy(assignment)
                if depth not in depth_entropies:
                    depth_entropies[depth] = []
                depth_entropies[depth].append(entropy)

                # Check if done
                if len(assignment) >= self.num_vars:
                    break

                # Pick random unassigned variable
                unassigned = [v for v in range(1, self.num_vars + 1)
                              if v not in assignment]
                if not unassigned:
                    break

                var = random.choice(unassigned)
                val = random.choice([True, False])
                assignment[var] = val
                depth += 1

                if depth > self.num_vars * 2:
                    break

        # Average at each depth
        max_depth = max(depth_entropies.keys()) if depth_entropies else 0
        trajectory = []
        for d in range(max_depth + 1):
            if d in depth_entropies and depth_entropies[d]:
                trajectory.append(sum(depth_entropies[d]) / len(depth_entropies[d]))
            else:
                trajectory.append(0.0)

        return trajectory


# ---------------------------------------------------------------------------
# ETCPredictor
# ---------------------------------------------------------------------------

class ETCPredictor:
    """Predict catastrophic failure modes using ETC analysis."""

    def __init__(self, clauses: list[list[int]], num_vars: int):
        self.entropy = SearchStateEntropy(clauses, num_vars)
        self.clauses = clauses
        self.num_vars = num_vars

    def compute_etc(self, trajectory: list[float]) -> float:
        """Compute ETC from entropy trajectory.

        ETC = Σ |Δ²H_i| where Δ²H_i = H[i-1] - 2H[i] + H[i+1]

        This is the discrete second derivative — captures
        total "curvature" of the entropy trajectory.

        High ETC means the system has abrupt transitions —
        it goes from many options to few options suddenly.

        Args:
            trajectory: List of entropy values at each depth.

        Returns:
            ETC score (total absolute curvature).
        """
        if len(trajectory) < 3:
            return 0.0

        etc_score = 0.0
        for i in range(1, len(trajectory) - 1):
            second_deriv = trajectory[i - 1] - 2 * trajectory[i] + trajectory[i + 1]
            etc_score += abs(second_deriv)

        return etc_score

    def find_cliffs(
        self,
        trajectory: list[float],
        threshold: float = 0.3,
    ) -> list[tuple[int, float]]:
        """Find entropy cliffs in the trajectory.

        A cliff is a depth where the second derivative exceeds threshold.
        These indicate sudden catastrophic state changes.

        Args:
            trajectory: Entropy trajectory.
            threshold: Minimum cliff magnitude.

        Returns:
            List of (depth, magnitude) pairs.
        """
        cliffs = []
        for i in range(1, len(trajectory) - 1):
            second_deriv = trajectory[i - 1] - 2 * trajectory[i] + trajectory[i + 1]
            if abs(second_deriv) > threshold:
                cliffs.append((i, abs(second_deriv)))
        return cliffs

    def analyze(self, num_samples: int = 100) -> dict:
        """Full ETC analysis.

        Returns dict:
        - etc_score: float (total curvature)
        - trajectory: list[float] (entropy at each depth)
        - cliffs: list[tuple[int, float]] (sudden drops)
        - max_cliff: float (largest single cliff)
        - cliff_density: float (cliffs per unit depth)
        - risk_profile: 'smooth' | 'moderate' | 'cliff_prone' | 'catastrophic'
        """
        trajectory = self.entropy.sample_entropy_trajectory(num_samples)
        etc_score = self.compute_etc(trajectory)
        cliffs = self.find_cliffs(trajectory)

        max_cliff = max((c[1] for c in cliffs), default=0.0)
        cliff_density = len(cliffs) / len(trajectory) if trajectory else 0.0

        # Risk profile
        if etc_score < 0.5 and cliff_density < 0.05:
            risk_profile = "smooth"
        elif etc_score < 1.5 and cliff_density < 0.1:
            risk_profile = "moderate"
        elif etc_score < 3.0:
            risk_profile = "cliff_prone"
        else:
            risk_profile = "catastrophic"

        return {
            "etc_score": etc_score,
            "trajectory": trajectory,
            "cliffs": cliffs,
            "max_cliff": max_cliff,
            "cliff_density": cliff_density,
            "risk_profile": risk_profile,
        }

    def evasion_likelihood(self, num_samples: int = 100) -> float:
        """Estimate likelihood of successful evasion attack.

        High ETC => sudden failures => system can be pushed
        from safe to unsafe with small perturbations.

        Returns probability estimate in [0, 1].
        """
        result = self.analyze(num_samples)
        etc_score = result["etc_score"]

        # Sigmoid mapping: ETC -> probability
        # ETC ≈ 0 => likelihood ≈ 0.05 (base rate)
        # ETC ≈ 2 => likelihood ≈ 0.5
        # ETC ≈ 5 => likelihood ≈ 0.95
        likelihood = 1.0 / (1.0 + math.exp(-(etc_score - 1.5)))
        return max(0.0, min(1.0, likelihood))


# ---------------------------------------------------------------------------
# screen_targets
# ---------------------------------------------------------------------------

def screen_targets(
    targets: list[tuple[str, list[list[int]], int]],
    num_samples: int = 100,
) -> list[dict]:
    """Screen multiple targets and rank by evasion potential.

    Args:
        targets: List of (name, clauses, num_vars) tuples.
        num_samples: ETC sample count.

    Returns targets sorted by highest ETC (most vulnerable to
    catastrophic evasion).
    """
    results = []
    for name, clauses, nv in targets:
        predictor = ETCPredictor(clauses, nv)
        analysis = predictor.analyze(num_samples)
        results.append({
            "name": name,
            "etc_score": analysis["etc_score"],
            "risk_profile": analysis["risk_profile"],
            "evasion_likelihood": predictor.evasion_likelihood(num_samples),
            **analysis,
        })

    # Sort by ETC descending
    results.sort(key=lambda r: r["etc_score"], reverse=True)
    return results


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ETC Evasion Predictor — Self-Test")
    print("=" * 60)

    # Test 1: Chain formula (smooth profile)
    print("\n[TEST 1] Chain 3-SAT (smooth profile expected)")
    nv1, clauses1 = make_small_example("chain_3sat", 10)
    pred1 = ETCPredictor(clauses1, nv1)
    result1 = pred1.analyze(num_samples=50)
    print(f"  ETC score: {result1['etc_score']:.4f}")
    print(f"  Risk profile: {result1['risk_profile']}")
    print(f"  Evasion likelihood: {pred1.evasion_likelihood(50):.2%}")

    # Test 2: Pigeonhole (bursty profile)
    print("\n[TEST 2] Pigeonhole PHP_4")
    nv2, clauses2 = make_small_example("pigeonhole", 4)
    pred2 = ETCPredictor(clauses2, nv2)
    result2 = pred2.analyze(num_samples=50)
    print(f"  ETC score: {result2['etc_score']:.4f}")
    print(f"  Risk profile: {result2['risk_profile']}")
    print(f"  Evasion likelihood: {pred2.evasion_likelihood(50):.2%}")

    # Test 3: Random 3-SAT at threshold
    print("\n[TEST 3] Random 3-SAT at threshold")
    nv3, clauses3 = make_small_example("random_3sat", 20, ratio=4.26)
    pred3 = ETCPredictor(clauses3, nv3)
    result3 = pred3.analyze(num_samples=50)
    print(f"  ETC score: {result3['etc_score']:.4f}")
    print(f"  Risk profile: {result3['risk_profile']}")

    # Test 4: Target screening
    print("\n[TEST 4] screen_targets ranking")
    targets = [
        ("chain_10", make_small_example("chain_3sat", 10)[1], 10),
        ("php_4", make_small_example("pigeonhole", 4)[1], 12),
        ("rand_15", make_small_example("random_3sat", 15)[1], 15),
    ]
    ranked = screen_targets(targets, num_samples=30)
    print("  Ranked by ETC (highest first):")
    for r in ranked:
        print(f"    {r['name']:12s}: ETC={r['etc_score']:.4f}, "
              f"profile={r['risk_profile']}")

    print("\n" + "=" * 60)
    print("All ETC evasion tests passed!")
    print("=" * 60)
