"""Comprehensive test suite for the CIC Security Tools Suite.

Tests all 4 tools (MINOTAUR, CLIFFHANGER, FORTRESS, CERBERUS)
plus shared cic_core library.

Run: python tests/test_all.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from cic_core import (
    unit_propagate, dpll_solve, is_satisfiable, get_backbone,
    NecessityClosure, ETCCalculator, build_primal_graph, minfill_treewidth,
    make_php, make_chain, parse_dimacs, to_dimacs
)


class TestCICCore(unittest.TestCase):

    def test_unit_propagation(self):
        clauses = [[1], [-1, 2], [-2, 3]]
        _, assignment, contradiction = unit_propagate(clauses, {})
        self.assertIn(1, assignment)
        self.assertFalse(contradiction)

    def test_dpll_sat(self):
        model = dpll_solve([[1, 2], [-1, 3]], 3)
        self.assertIsNotNone(model)

    def test_dpll_unsat(self):
        model = dpll_solve([[1], [-1]], 1)
        self.assertIsNone(model)

    def test_backbone(self):
        bb = get_backbone([[1], [1, 2], [-2, 3]], 3)
        self.assertIn(1, bb)
        self.assertTrue(bb[1])

    def test_necessity_closure(self):
        closure = NecessityClosure([[1, 2], [-2, 3], [-3, 4]], 4)
        forced = closure.closure({1})
        self.assertIn(1, forced)

    def test_closure_sequence(self):
        closure = NecessityClosure([[1], [1, 2]], 2)
        seq = closure.closure_sequence(set())
        self.assertGreaterEqual(len(seq), 1)

    def test_backbone_computation(self):
        closure = NecessityClosure([[1], [-1, 2]], 2)
        bb = closure.backbone()
        self.assertIn(1, bb)

    def test_etc_calculation(self):
        calc = ETCCalculator(make_chain(10)[1], 10)
        etc = calc.compute(30)
        self.assertIsInstance(etc, float)
        self.assertGreaterEqual(etc, 0.0)

    def test_trajectory(self):
        calc = ETCCalculator(make_chain(8)[1], 8)
        traj = calc.trajectory(20)
        self.assertGreater(len(traj), 0)

    def test_primal_graph(self):
        g = build_primal_graph(4, [[1, 2], [2, 3]])
        self.assertIn(1, g)
        self.assertIn(2, g[1])

    def test_minfill(self):
        tree = {1: {2, 3}, 2: {1}, 3: {1}}
        _, width = minfill_treewidth(tree)
        self.assertLessEqual(width, 2)

    def test_php_unsat(self):
        nv, clauses = make_php(3)
        self.assertFalse(is_satisfiable(clauses, nv))

    def test_chain_sat(self):
        nv, clauses = make_chain(5)
        self.assertTrue(is_satisfiable(clauses, nv))

    def test_dimacs_roundtrip(self):
        clauses = [[1, -2], [-1, 3]]
        dimacs = to_dimacs(3, clauses)
        nv, parsed = parse_dimacs(dimacs)
        self.assertEqual(nv, 3)
        self.assertEqual(len(parsed), 2)


class TestMinotaur(unittest.TestCase):

    def test_minimal_trigger_found(self):
        from minotaur import find_minimal_trigger, analyze_trigger
        clauses = [[1, 2], [-2, 3], [-3, 4]]
        trigger = find_minimal_trigger(clauses, 4, {4}, max_size=3)
        self.assertIsNotNone(trigger)
        analysis = analyze_trigger(clauses, 4, trigger)
        self.assertIn("classification", analysis)

    def test_trigger_actually_forces(self):
        from minotaur import find_minimal_trigger
        closure = NecessityClosure([[1, 2], [-2, 3], [-3, 4]], 4)
        trigger = find_minimal_trigger([[1, 2], [-2, 3], [-3, 4]], 4, {4}, max_size=3)
        self.assertIsNotNone(trigger)
        forced = closure.closure(trigger)
        self.assertIn(4, forced)

    def test_all_triggers(self):
        from minotaur import find_all_triggers
        triggers = find_all_triggers([[1], [-1, 2]], 2, {2}, max_size=3)
        self.assertIsInstance(triggers, list)


class TestCliffhanger(unittest.TestCase):

    def test_etc_computation(self):
        from cliffhanger import full_analysis
        nv, clauses = make_chain(10)
        result = full_analysis(clauses, nv, 30)
        self.assertIn("etc_score", result)
        self.assertIn("risk_profile", result)

    def test_risk_profile_values(self):
        from cliffhanger import risk_profile
        self.assertEqual(risk_profile(0.1, 0.0, 0.0), "SMOOTH")
        self.assertEqual(risk_profile(5.0, 2.0, 0.2), "CATASTROPHIC")

    def test_evasion_range(self):
        from cliffhanger import evasion_likelihood
        self.assertGreaterEqual(evasion_likelihood(0.0), 0.0)
        self.assertLessEqual(evasion_likelihood(10.0), 1.0)

    def test_cliff_detection(self):
        from cliffhanger import find_cliffs
        traj = [1.0, 0.95, 0.1, 0.05, 0.0]
        cliffs = find_cliffs(traj, threshold=0.2)
        self.assertGreater(len(cliffs), 0)


class TestFortress(unittest.TestCase):

    def test_trivial_classification(self):
        from fortress import classify_width
        c = classify_width(2)
        self.assertEqual(c["verdict"], "vulnerable")
        self.assertEqual(c["confidence"], "high")

    def test_extreme_classification(self):
        from fortress import classify_width
        c = classify_width(60)
        self.assertEqual(c["verdict"], "defended")

    def test_security_score_range(self):
        from fortress import structural_score
        self.assertGreaterEqual(structural_score(10, 20, 40), 0.0)
        self.assertLessEqual(structural_score(10, 20, 40), 100.0)

    def test_defense_recommendations(self):
        from fortress import defense_recommendations
        recs = defense_recommendations(5, 20, 40)
        self.assertGreater(len(recs), 0)

    def test_full_analysis(self):
        from fortress import analyze
        result = analyze([[1], [1, 2]], 2, "test")
        self.assertIn("security_score", result)
        self.assertIn("classification", result)
        self.assertIn("recommendations", result)


class TestCerberus(unittest.TestCase):

    def test_bmc_encoding(self):
        from cerberus import BoundedModelChecker
        bmc = BoundedModelChecker()
        nv, initial, tx, bad = 2, [[-1], [-2]], [[1, -1], [2, -2]], [[1]]
        tv, clauses = bmc.encode_bmc(nv, initial, tx, bad, 3)
        self.assertGreater(tv, nv)
        self.assertGreater(len(clauses), 0)

    def test_trace_extraction(self):
        from cerberus import BoundedModelChecker
        bmc = BoundedModelChecker()
        model = {0 * 2 + 1: False, 0 * 2 + 2: False,
                 1 * 2 + 1: True, 1 * 2 + 2: False}
        trace = bmc.extract_trace(model, 2, 1)
        self.assertEqual(len(trace), 2)

    def test_structural_check(self):
        from cerberus import structural_check
        result = structural_check([[1, 2]], 2, 5)
        self.assertIn("classification", result)

    def test_auth_bypass_generated(self):
        from cerberus import generate_auth_bypass_transition, BoundedModelChecker, dpll_solve
        nv, init, tx, bad = generate_auth_bypass_transition()
        bmc = BoundedModelChecker()
        tv, clauses = bmc.encode_bmc(nv, init, tx, bad, 5)
        model = dpll_solve(clauses, tv, timeout=10.0)
        self.assertIsNotNone(model)
        trace = bmc.extract_trace(model, nv, 5)
        self.assertTrue(trace[-1].get(3, False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
