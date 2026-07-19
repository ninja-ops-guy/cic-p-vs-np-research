"""Comprehensive test suite for the CIC Red Team Harness.

Tests all 4 modules plus the main harness with known-formula benchmarks.
Run: python tests/test_all.py
"""

import sys
import time
import unittest

sys.path.insert(0, "/mnt/agents/output/redteam_harness")

from utils.sat_utils import (
    dpll_solve, get_backbone, is_satisfiable, make_small_example,
    unit_propagate, parse_dimacs, to_dimacs
)
from utils.graph_utils import build_variable_graph, graph_stats
from utils.width_utils import minfill_ordering, estimate_difficulty
from modules.necessity_backdoor import NecessityClosure, BackdoorScanner
from modules.width_defense import AttackFeasibilityAnalyzer
from modules.etc_evasion import ETCPredictor
from harness import RedTeamHarness


# ---------------------------------------------------------------------------
# SAT Utils Tests
# ---------------------------------------------------------------------------
class TestSATUtils(unittest.TestCase):

    def test_unit_propagation_basic(self):
        clauses = [[1], [-1, 2], [-2, 3]]
        simplified, assignment, contradiction = unit_propagate(clauses, {})
        self.assertTrue(1 in assignment)
        self.assertFalse(contradiction)

    def test_dpll_sat(self):
        clauses = [[1, 2], [-1, 3]]
        model = dpll_solve(clauses, 3)
        self.assertIsNotNone(model)

    def test_dpll_unsat(self):
        clauses = [[1], [-1]]
        model = dpll_solve(clauses, 1)
        self.assertIsNone(model)

    def test_backbone(self):
        clauses = [[1], [1, 2], [-2, 3]]
        backbone = get_backbone(clauses, 3)
        self.assertIn(1, backbone)
        self.assertTrue(backbone[1])

    def test_is_satisfiable(self):
        self.assertTrue(is_satisfiable([[1, 2]], 2))
        self.assertFalse(is_satisfiable([[1], [-1]], 1))

    def test_dimacs_roundtrip(self):
        clauses = [[1, 2], [-1, 3], [2, -3]]
        cnf = to_dimacs(3, clauses)
        nv, parsed = parse_dimacs(cnf)
        self.assertEqual(nv, 3)
        self.assertEqual(len(parsed), 3)

    def test_pigeonhole_unsat(self):
        nv, clauses = make_small_example("pigeonhole", 3)
        self.assertFalse(is_satisfiable(clauses, nv))

    def test_chain_sat(self):
        nv, clauses = make_small_example("chain_3sat", 5)
        self.assertTrue(is_satisfiable(clauses, nv))


# ---------------------------------------------------------------------------
# Graph & Width Utils Tests
# ---------------------------------------------------------------------------
class TestGraphWidthUtils(unittest.TestCase):

    def test_build_variable_graph(self):
        clauses = [[1, 2], [2, 3], [3, 4]]
        g = build_variable_graph(clauses)
        self.assertIn(1, g)
        self.assertIn(2, g[1])

    def test_graph_stats(self):
        clauses = [[1, 2], [2, 3]]
        g = build_variable_graph(clauses)
        stats = graph_stats(g)
        self.assertEqual(stats["num_nodes"], 3)
        self.assertEqual(stats["num_edges"], 2)

    def test_minfill_on_tree(self):
        # Star graph (tree): width should be small
        graph = {1: {2, 3, 4}, 2: {1}, 3: {1}, 4: {1}}
        ordering, width = minfill_ordering(graph)
        self.assertLessEqual(width, 3)

    def test_difficulty_classification(self):
        self.assertEqual(estimate_difficulty(2, 10, 20), "trivial")
        self.assertEqual(estimate_difficulty(8, 50, 100), "easy")
        self.assertEqual(estimate_difficulty(30, 100, 400), "hard")


# ---------------------------------------------------------------------------
# Necessity Backdoor Tests
# ---------------------------------------------------------------------------
class TestNecessityBackdoor(unittest.TestCase):

    def test_closure_axioms(self):
        """Verify N_φ is a Galois closure operator."""
        clauses = [[1, 2], [-2, 3], [-3, 4]]
        closure = NecessityClosure(clauses, 4)
        axioms = closure.verify_closure_axioms()
        self.assertTrue(axioms["extensivity"])
        self.assertTrue(axioms["monotonicity"])
        self.assertTrue(axioms["idempotence"])

    def test_minimal_trigger(self):
        """Find minimal trigger for implication chain."""
        clauses = [[1, 2], [-2, 3], [-3, 4]]
        closure = NecessityClosure(clauses, 4)
        scanner = BackdoorScanner(closure)
        trigger = scanner.find_minimal_trigger({4}, max_size=4)
        self.assertIsNotNone(trigger)
        # Verify trigger actually forces target
        forced = closure.n_of(trigger)
        self.assertIn(4, forced)

    def test_propagation_rank(self):
        """Rank should be non-negative integer."""
        clauses = [[1, 2], [-2, 3]]
        closure = NecessityClosure(clauses, 3)
        rank = closure.propagation_rank()
        self.assertIsInstance(rank, int)
        self.assertGreaterEqual(rank, 0)

    def test_backbone(self):
        """Backbone of formula with unit clause."""
        clauses = [[1], [1, 2], [-2, 3]]
        closure = NecessityClosure(clauses, 3)
        backbone = closure.backbone()
        self.assertIn(1, backbone)

    def test_burst_score(self):
        """Bursty profiles have higher variance."""
        scanner = BackdoorScanner(NecessityClosure([[1]], 1))
        smooth = [0, 1, 2, 3, 4]
        bursty = [0, 0, 0, 5, 5]
        self.assertGreater(scanner.burst_score(bursty),
                          scanner.burst_score(smooth))

    def test_vulnerability_classification(self):
        """Classification produces valid output."""
        clauses = [[1], [-1, 2]]
        closure = NecessityClosure(clauses, 2)
        scanner = BackdoorScanner(closure)
        classification = scanner.classify_vulnerability({1})
        self.assertIn("classification", classification)
        self.assertIn(classification["classification"],
                      ["shallow", "moderate", "deep", "critical"])


# ---------------------------------------------------------------------------
# Width Defense Tests
# ---------------------------------------------------------------------------
class TestWidthDefense(unittest.TestCase):

    def test_verdict_trivial(self):
        analyzer = AttackFeasibilityAnalyzer()
        v = analyzer.verdict(2, 10)
        self.assertEqual(v["verdict"], "vulnerable")
        self.assertEqual(v["confidence"], "high")

    def test_verdict_extreme(self):
        analyzer = AttackFeasibilityAnalyzer()
        v = analyzer.verdict(60, 100)
        self.assertEqual(v["verdict"], "defended")

    def test_compare_systems(self):
        analyzer = AttackFeasibilityAnalyzer()
        systems = [
            ("A", [[1], [1, 2]], 2),
            ("B", [[1, 2], [2, 3], [3, 4], [4, 5]], 5),
        ]
        results = analyzer.compare_systems(systems)
        self.assertEqual(len(results), 2)
        # Results should be sorted by vulnerability
        self.assertLessEqual(results[0]["relative_score"],
                           results[1]["relative_score"])

    def test_defense_recommendations(self):
        analyzer = AttackFeasibilityAnalyzer()
        recs = analyzer.defense_recommendation(5, 20)
        self.assertTrue(len(recs) > 0)


# ---------------------------------------------------------------------------
# ETC Evasion Tests
# ---------------------------------------------------------------------------
class TestETCEvasion(unittest.TestCase):

    def test_chain_etc_low(self):
        """Chain formulas have smooth entropy profiles."""
        nv, clauses = make_small_example("chain_3sat", 10)
        predictor = ETCPredictor(clauses, nv)
        result = predictor.analyze(num_samples=30)
        self.assertIn("etc_score", result)
        self.assertIn("risk_profile", result)
        self.assertIn(result["risk_profile"],
                      ["smooth", "moderate", "cliff_prone", "catastrophic"])

    def test_php_etc(self):
        """PHP formulas produce valid ETC analysis."""
        nv, clauses = make_small_example("pigeonhole", 4)
        predictor = ETCPredictor(clauses, nv)
        result = predictor.analyze(num_samples=30)
        self.assertGreaterEqual(result["etc_score"], 0.0)

    def test_evasion_likelihood_range(self):
        """Evasion likelihood should be in [0, 1]."""
        nv, clauses = make_small_example("chain_3sat", 8)
        predictor = ETCPredictor(clauses, nv)
        likelihood = predictor.evasion_likelihood(num_samples=30)
        self.assertGreaterEqual(likelihood, 0.0)
        self.assertLessEqual(likelihood, 1.0)

    def test_screen_targets(self):
        """Target screening ranks by ETC."""
        from modules.etc_evasion import screen_targets
        targets = [
            ("chain", make_small_example("chain_3sat", 10)[1], 10),
            ("php", make_small_example("pigeonhole", 4)[1], 12),
        ]
        ranked = screen_targets(targets, num_samples=20)
        self.assertEqual(len(ranked), 2)


# ---------------------------------------------------------------------------
# Harness Integration Tests
# ---------------------------------------------------------------------------
class TestHarnessIntegration(unittest.TestCase):

    def test_full_assessment_php(self):
        """End-to-end: Pigeonhole formula."""
        harness = RedTeamHarness()
        nv, clauses = make_small_example("pigeonhole", 3)
        assessment = harness.full_assessment(clauses, nv)
        self.assertIn("overall_risk_score", assessment)
        self.assertIn("sat", assessment)
        self.assertIn("feasibility", assessment)
        self.assertIn("evasion", assessment)

    def test_full_assessment_chain(self):
        """End-to-end: Chain formula."""
        harness = RedTeamHarness()
        nv, clauses = make_small_example("chain_3sat", 8)
        assessment = harness.full_assessment(clauses, nv)
        self.assertGreaterEqual(assessment["overall_risk_score"], 0.0)
        self.assertLessEqual(assessment["overall_risk_score"], 1.0)

    def test_report_generation(self):
        """Report is non-empty and well-formatted."""
        harness = RedTeamHarness()
        nv, clauses = make_small_example("pigeonhole", 3)
        assessment = harness.full_assessment(clauses, nv)
        report = harness.report(assessment)
        self.assertIn("CIC RED TEAM HARNESS", report)
        self.assertIn("Risk Score", report)
        self.assertTrue(len(report) > 200)

    def test_backdoor_integration(self):
        """Backdoor scanner finds triggers via harness."""
        harness = RedTeamHarness()
        clauses = [[1, 2], [-2, 3], [-3, 4]]
        result = harness.scan_backdoor(clauses, 4, {4})
        self.assertIn("backdoor_size", result)

    def test_assessment_timing(self):
        """Assessment completes in reasonable time."""
        harness = RedTeamHarness()
        nv, clauses = make_small_example("pigeonhole", 3)
        t0 = time.time()
        harness.full_assessment(clauses, nv)
        elapsed = time.time() - t0
        self.assertLess(elapsed, 30.0)


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main(verbosity=2)
