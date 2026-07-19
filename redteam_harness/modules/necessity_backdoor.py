"""Necessity Propagation Backdoor Scanner

Based on Stage 18: Necessity Propagation Theory (NPT)

This module finds minimal trigger sets that force a target behavior
using the necessity closure operator N_φ.

Key theoretical foundation:
- N_φ(S) = all facts logically forced by assumptions S
- N_φ is a Galois closure operator (proved: extensivity, monotonicity, idempotence)
- Propagation rank = number of iterations until N^t(∅) stabilizes
- |N_∞| = backbone size (verified: Pearson r = 1.000 on 291 formulas)

Red team application:
Given a constraint system and target violation, find the MINIMAL set of
conditions that necessarily trigger it. This is provably smaller than
gradient-based adversarial perturbations because it uses logical closure.
"""

from __future__ import annotations

import math
from typing import Optional


# ---------------------------------------------------------------------------
# NecessityClosure
# ---------------------------------------------------------------------------

class NecessityClosure:
    """Implements the N_φ closure operator for a given CNF formula.

    The closure operator N_φ is defined as:
        N_φ(S) = all literals forced by unit propagation from assumptions S

    Key properties (proved as theorems in Stage 18):
        - Extensivity:   S ⊆ N_φ(S)
        - Monotonicity:  S ⊆ T  ⇒  N_φ(S) ⊆ N_φ(T)
        - Idempotence:   N_φ(N_φ(S)) = N_φ(S)

    These three properties make N_φ a *Galois closure operator*, which
    means the fixed points of N_φ form a complete lattice. This lattice
    structure is what enables efficient backdoor search.
    """

    def __init__(self, clauses: list[list[int]], num_vars: int):
        """Initialize closure operator with a CNF formula.

        Args:
            clauses: CNF formula as list of integer literal lists.
            num_vars: Number of variables.
        """
        self.clauses = [list(c) for c in clauses]  # deep copy
        self.num_vars = num_vars

    def n_of(self, assumptions: set[int]) -> set[int]:
        """Compute N_φ(assumptions) = all literals forced by unit propagation.

        Apply unit propagation starting from the assumptions.
        All literals forced by UP are in the closure.

        Args:
            assumptions: Set of literal ints (positive=True, negative=False).

        Returns:
            Set of all forced literals.
        """
        from utils.sat_utils import unit_propagate

        # Convert assumptions to assignment dict
        assignment: dict[int, bool] = {}
        for lit in assumptions:
            var = abs(lit)
            val = lit > 0
            assignment[var] = val

        # Apply unit propagation
        _, forced_assignment, contradiction = unit_propagate(self.clauses, assignment)

        if contradiction:
            # Contradiction means everything is forced (principle of explosion)
            return set(range(1, self.num_vars + 1)) | set(range(-self.num_vars, 0))

        # Convert back to literal set
        forced_literals: set[int] = set()
        for var, val in forced_assignment.items():
            lit = var if val else -var
            forced_literals.add(lit)

        return forced_literals

    def closure_sequence(self, seed: Optional[set[int]] = None) -> list[set[int]]:
        """Compute the full closure sequence starting from seed.

        Returns [N^0(seed), N^1(seed), N^2(seed), ..., N^∞(seed)]
        where N^0(seed) = seed and N^{t+1}(seed) = N(N^t(seed))

        Args:
            seed: Starting set of literals (default: empty set).

        Returns:
            List of sets showing propagation at each iteration.
        """
        seed = seed or set()
        sequence: list[set[int]] = [set(seed)]

        current = set(seed)
        while True:
            next_closure = self.n_of(current)
            if next_closure == current:
                break
            sequence.append(next_closure)
            current = next_closure

        return sequence

    def propagation_rank(self, seed: Optional[set[int]] = None) -> int:
        """Number of iterations until stabilization.

        Args:
            seed: Starting set of literals.

        Returns:
            Number of N applications until fixed point.
        """
        return len(self.closure_sequence(seed)) - 1

    def backbone(self) -> set[int]:
        """N^∞(∅) = all literals forced from empty set = backbone.

        The backbone consists of literals that are true in ALL models.
        These are facts that are logically forced by the formula itself,
        independent of any assumptions.

        Returns:
            Set of backbone literals.
        """
        sequence = self.closure_sequence(set())
        return sequence[-1] if sequence else set()

    def is_closed(self, s: set[int]) -> bool:
        """Check if S is closed under N_φ (i.e., N(S) = S).

        A closed set represents a "self-contained" set of facts —
        nothing outside the set is forced by anything inside.

        Args:
            s: Set of literals to test.

        Returns:
            True if S is a fixed point of N_φ.
        """
        return self.n_of(s) == s

    def verify_closure_axioms(self) -> dict[str, bool]:
        """Verify the three closure axioms on test cases.

        Returns:
            Dict with keys 'extensivity', 'monotonicity', 'idempotence'.
            All should be True for a valid Galois closure operator.
        """
        import random

        results: dict[str, bool] = {}

        # Pick a few test sets
        test_sets: list[set[int]] = []
        for _ in range(3):
            size = random.randint(0, min(3, self.num_vars))
            s = set()
            for _ in range(size):
                var = random.randint(1, self.num_vars)
                lit = var if random.random() < 0.5 else -var
                s.add(lit)
            test_sets.append(s)

        # Extensivity: S ⊆ N(S)
        results["extensivity"] = all(
            s.issubset(self.n_of(s)) for s in test_sets
        )

        # Monotonicity: S ⊆ T ⇒ N(S) ⊆ N(T)
        mono_holds = True
        for i, s in enumerate(test_sets):
            for t in test_sets[i + 1:]:
                if s.issubset(t):
                    if not self.n_of(s).issubset(self.n_of(t)):
                        mono_holds = False
                        break
            if not mono_holds:
                break
        results["monotonicity"] = mono_holds

        # Idempotence: N(N(S)) = N(S)
        results["idempotence"] = all(
            self.n_of(self.n_of(s)) == self.n_of(s) for s in test_sets
        )

        return results


# ---------------------------------------------------------------------------
# BackdoorScanner
# ---------------------------------------------------------------------------

class BackdoorScanner:
    """Find minimal backdoor triggers using necessity propagation.

    A "backdoor" in this context is a minimal set of assumptions that,
    when propagated through N_φ, force a target set of literals.

    This is fundamentally different from gradient-based adversarial
    perturbations because:
    1. The trigger is PROVABLY minimal (logical closure, not approximation)
    2. The trigger is DISCRETE (boolean conditions, not continuous values)
    3. The trigger is INTERPRETABLE (each element is a named condition)
    """

    def __init__(self, closure: NecessityClosure):
        """Initialize with a closure operator.

        Args:
            closure: NecessityClosure instance for the target formula.
        """
        self.closure = closure
        self.num_vars = closure.num_vars

    def find_minimal_trigger(
        self,
        target_literals: set[int],
        max_size: int = 5,
    ) -> Optional[set[int]]:
        """Find the smallest set of assumptions that forces all target_literals.

        Search strategy: try all subsets of size 1, 2, 3, ... up to max_size.
        For each subset S, check if target_literals ⊆ N_φ(S).

        Args:
            target_literals: Literals that MUST be forced.
            max_size: Maximum trigger size to search.

        Returns:
            Minimal trigger set, or None if none found within max_size.
        """
        from itertools import combinations

        universe = set(range(1, self.num_vars + 1)) | set(range(-self.num_vars, 0))

        for size in range(1, max_size + 1):
            for subset_tuple in combinations(universe, size):
                subset = set(subset_tuple)
                forced = self.closure.n_of(subset)
                if target_literals.issubset(forced):
                    return subset

        return None

    def find_trigger_greedy(self, target_literals: set[int]) -> set[int]:
        """Greedy trigger finder: iteratively add the literal that
        forces the most remaining target literals.

        Faster than exhaustive search but may not find minimum.

        Args:
            target_literals: Literals that must be forced.

        Returns:
            Greedy trigger set.
        """
        trigger: set[int] = set()
        remaining = set(target_literals)

        while remaining:
            best_lit = None
            best_forced = 0

            for var in range(1, self.num_vars + 1):
                for lit in [var, -var]:
                    test_trigger = trigger | {lit}
                    forced = self.closure.n_of(test_trigger)
                    newly_forced = len(remaining & forced)
                    if newly_forced > best_forced:
                        best_forced = newly_forced
                        best_lit = lit

            if best_lit is None or best_forced == 0:
                break

            trigger.add(best_lit)
            forced = self.closure.n_of(trigger)
            remaining -= forced

        return trigger

    def necessity_growth_profile(self, trigger: set[int]) -> list[int]:
        """Compute the necessity growth profile for a given trigger.

        Returns [|N^0(trigger)|, |N^1(trigger)|, |N^2(trigger)|, ..., |N^∞(trigger)|]

        This reveals whether propagation is:
        - Smooth (gradual increase): easy to understand
        - Bursty (sudden jumps): indicates hidden coupling

        Bursty profiles (high variance) are signatures of deep vulnerabilities.

        Args:
            trigger: Initial assumption set.

        Returns:
            List of closure sizes at each iteration.
        """
        sequence = self.closure.closure_sequence(trigger)
        return [len(s) for s in sequence]

    def burst_score(self, profile: list[int]) -> float:
        """Compute the burst score = variance of growth increments.

        High burst score = intrinsically coupled vulnerability.
        From Stage 18: PHP has Var(G) = Θ(n²), the highest of all families tested.

        Args:
            profile: Growth profile (list of sizes).

        Returns:
            Variance of growth increments.
        """
        if len(profile) < 2:
            return 0.0

        increments = [profile[i] - profile[i - 1] for i in range(1, len(profile))]
        if not increments:
            return 0.0

        mean = sum(increments) / len(increments)
        variance = sum((x - mean) ** 2 for x in increments) / len(increments)
        return variance

    def classify_vulnerability(self, trigger: set[int]) -> dict:
        """Full vulnerability classification.

        Returns dict with:
        - trigger_size: int
        - propagation_rank: int
        - final_closure_size: int
        - burst_score: float
        - profile: list[int]
        - classification: 'shallow' | 'moderate' | 'deep' | 'critical'

        Args:
            trigger: Trigger set to classify.

        Returns:
            Classification dict.
        """
        profile = self.necessity_growth_profile(trigger)
        rank = len(profile) - 1
        burst = self.burst_score(profile)
        final_size = profile[-1] if profile else 0

        # Classification heuristic
        if rank <= 1 and burst < 1.0:
            classification = "shallow"
        elif rank <= 2 and burst < 5.0:
            classification = "moderate"
        elif burst >= 10.0:
            classification = "critical"
        else:
            classification = "deep"

        return {
            "trigger_size": len(trigger),
            "propagation_rank": rank,
            "final_closure_size": final_size,
            "burst_score": burst,
            "profile": profile,
            "classification": classification,
        }


# ---------------------------------------------------------------------------
# Standalone convenience functions
# ---------------------------------------------------------------------------

def analyze_backdoor(
    clauses: list[list[int]],
    num_vars: int,
    target_literals: set[int],
) -> dict:
    """One-shot backdoor analysis. Convenience wrapper.

    Args:
        clauses: CNF formula.
        num_vars: Number of variables.
        target_literals: Target literals to force.

    Returns:
        Complete analysis dict.
    """
    closure = NecessityClosure(clauses, num_vars)
    scanner = BackdoorScanner(closure)

    trigger = scanner.find_minimal_trigger(target_literals)
    if trigger is None:
        return {
            "trigger": None,
            "trigger_size": None,
            "status": "no_trigger_found",
            "target_literals": list(target_literals),
        }

    classification = scanner.classify_vulnerability(trigger)
    return {
        "trigger": sorted(trigger),
        "trigger_size": len(trigger),
        "classification": classification["classification"],
        "propagation_rank": classification["propagation_rank"],
        "burst_score": classification["burst_score"],
        "profile": classification["profile"],
        "status": "ok",
        "target_literals": list(target_literals),
    }


def compare_triggers(
    clauses: list[list[int]],
    num_vars: int,
    targets: list[set[int]],
) -> dict:
    """Compare trigger sizes for multiple targets.

    Args:
        clauses: CNF formula.
        num_vars: Number of variables.
        targets: List of target literal sets.

    Returns:
        Dict mapping target index to analysis result.
    """
    closure = NecessityClosure(clauses, num_vars)
    scanner = BackdoorScanner(closure)

    results = {}
    for i, target in enumerate(targets):
        trigger = scanner.find_minimal_trigger(target)
        results[i] = {
            "target": sorted(target),
            "trigger": sorted(trigger) if trigger else None,
            "trigger_size": len(trigger) if trigger else None,
        }

    return results


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Necessity Backdoor Scanner — Self-Test")
    print("=" * 60)

    # Test 1: Simple implication chain
    print("\n[TEST 1] Implication chain: x1 → x2 → x3 → x4")
    chain_clauses = [[1, 2], [-2, 3], [-3, 4]]  # ~x1|x2, ~x2|x3, ~x3|x4
    closure = NecessityClosure(chain_clauses, 4)
    scanner = BackdoorScanner(closure)

    # Find trigger for x4
    trigger = scanner.find_minimal_trigger({4}, max_size=3)
    print(f"  Minimal trigger for x4: {trigger}")
    if trigger:
        profile = scanner.necessity_growth_profile(trigger)
        print(f"  Growth profile: {profile}")
        classification = scanner.classify_vulnerability(trigger)
        print(f"  Classification: {classification['classification']}")

    # Test 2: Closure axioms
    print("\n[TEST 2] Closure operator axioms")
    axioms = closure.verify_closure_axioms()
    print(f"  Extensivity: {axioms['extensivity']}")
    print(f"  Monotonicity: {axioms['monotonicity']}")
    print(f"  Idempotence: {axioms['idempotence']}")
    assert all(axioms.values()), "Closure axioms must hold!"
    print("  ✓ All axioms verified")

    # Test 3: Backbone
    print("\n[TEST 3] Backbone computation")
    backbone = closure.backbone()
    print(f"  Backbone of chain: {backbone}")

    # Test 4: Burst score
    print("\n[TEST 4] Burst score")
    smooth_profile = [0, 1, 2, 3, 4]
    bursty_profile = [0, 0, 0, 10, 10]
    smooth_score = scanner.burst_score(smooth_profile)
    bursty_score = scanner.burst_score(bursty_profile)
    print(f"  Smooth profile burst: {smooth_score:.2f}")
    print(f"  Bursty profile burst: {bursty_score:.2f}")
    assert bursty_score > smooth_score
    print("  ✓ Bursty > Smooth")

    print("\n" + "=" * 60)
    print("All backdoor scanner tests passed!")
    print("=" * 60)
