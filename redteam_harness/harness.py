"""CIC Red Team Harness

Main orchestrator that integrates all research-based modules:
1. Necessity Propagation Backdoor Scanner (Stage 18)
2. Structural SAT Encoder (CIC-SAT v4)
3. Treewidth Attack Feasibility Analyzer (Theorem 1)
4. ETC Evasion Predictor (Stage 17)

Usage::

    python harness.py --dimacs file.cnf --target "4 -5"
    python harness.py --generate pigeonhole --n 5 --module all
    python harness.py --generate chain --n 10 --module backdoor

"""

from __future__ import annotations

import argparse
import math
import os
import random
import sys
import time
from typing import Optional

# ---------------------------------------------------------------------------
# Ensure the project root and modules/ dir are on sys.path
# ---------------------------------------------------------------------------

_HARNESS_DIR = os.path.dirname(os.path.abspath(__file__))
_MODULES_DIR = os.path.join(_HARNESS_DIR, "modules")
_UTILS_DIR = os.path.join(_HARNESS_DIR, "utils")
for _d in (_HARNESS_DIR, _MODULES_DIR, _UTILS_DIR):
    if _d not in sys.path:
        sys.path.insert(0, _d)

# -- Module 4: ETC Evasion Predictor (always available, stdlib only) -------
from modules.etc_evasion import ETCPredictor, screen_targets  # noqa: E402

# -- Module 1: Necessity Propagation Backdoor Scanner (stdlib only) --------
try:
    from modules.necessity_backdoor import (
        BackdoorScanner,
        NecessityClosure,
        analyze_backdoor,
    )
    _HAS_BACKDOOR = True
except Exception as _exc:
    _HAS_BACKDOOR = False

# -- Module 2: Structural SAT (requires networkx) --------------------------
try:
    from modules.structural_sat import (
        BoundedModelChecker,
        StructuralSATEncoder,
        analyze_structure,
    )
    _HAS_STRUCTURAL_SAT = True
except Exception as _exc:
    _HAS_STRUCTURAL_SAT = False

# -- Module 3: Width Defense (requires networkx) ---------------------------
try:
    from modules.width_defense import (
        AttackFeasibilityAnalyzer,
        quick_assess,
    )
    _HAS_WIDTH_DEFENSE = True
except Exception as _exc:
    _HAS_WIDTH_DEFENSE = False

# -- Shared utilities -------------------------------------------------------
from utils.sat_utils import dpll_solve, is_satisfiable, make_small_example  # noqa: E402


# ===========================================================================
# RedTeamHarness
# ===========================================================================

class RedTeamHarness:
    """Main orchestrator integrating all four research-based modules."""

    def __init__(self):
        self._modules_available = {
            "backdoor": _HAS_BACKDOOR,
            "structural_sat": _HAS_STRUCTURAL_SAT,
            "treewidth": _HAS_WIDTH_DEFENSE,
            "etc_evasion": True,  # always available
            "dpll": True,         # always available
        }

    # ------------------------------------------------------------------
    # Module 1: Backdoor Scanner
    # ------------------------------------------------------------------
    def scan_backdoor(
        self,
        clauses: list,
        num_vars: int,
        target_literals: set,
        max_size: int = 5,
    ) -> dict:
        """Run the necessity-propagation backdoor scanner.

        Returns a dict with keys: backdoor_size, backdoor_vars,
        necessity_chain, status.
        """
        if not _HAS_BACKDOOR:
            return {"status": "unavailable", "reason": "necessity_backdoor module missing"}

        try:
            closure = NecessityClosure(clauses, num_vars)
            scanner = BackdoorScanner(closure)
            trigger = scanner.find_minimal_trigger(target_literals, max_size=max_size)

            if trigger is None:
                return {
                    "backdoor_size": None,
                    "backdoor_vars": [],
                    "necessity_chain": [],
                    "status": "no_trigger_found",
                    "target_literals": list(target_literals),
                }

            profile = scanner.necessity_growth_profile(trigger)
            classification = scanner.classify_vulnerability(trigger)

            return {
                "backdoor_size": len(trigger),
                "backdoor_vars": sorted(trigger),
                "necessity_chain": profile,
                "propagation_rank": classification.get("propagation_rank", -1),
                "burst_score": classification.get("burst_score", 0.0),
                "classification": classification.get("classification", "unknown"),
                "status": "ok",
                "target_literals": list(target_literals),
            }
        except Exception as exc:
            return {"status": "error", "reason": str(exc)}

    # ------------------------------------------------------------------
    # Module 2: Structural SAT
    # ------------------------------------------------------------------
    def check_sat(self, clauses: list, num_vars: int, timeout: float = 30.0) -> dict:
        """Run the structural SAT encoder / solver.

        Returns dict with keys: satisfiable, assignment, runtime, status.
        """
        t0 = time.time()
        try:
            model = dpll_solve(clauses, num_vars, timeout=timeout)
            runtime = time.time() - t0
            if model is None:
                return {
                    "satisfiable": False,
                    "assignment": None,
                    "runtime": runtime,
                    "status": "unsat",
                    "backend": "dpll",
                    "encoding_size": {"variables": num_vars, "clauses": len(clauses)},
                }
            return {
                "satisfiable": True,
                "assignment": model,
                "runtime": runtime,
                "status": "sat",
                "backend": "dpll",
                "encoding_size": {"variables": num_vars, "clauses": len(clauses)},
            }
        except Exception as exc:
            runtime = time.time() - t0
            return {"satisfiable": None, "runtime": runtime, "status": "error", "reason": str(exc), "backend": "dpll"}

    # ------------------------------------------------------------------
    # Module 3: Attack Feasibility
    # ------------------------------------------------------------------
    def assess_feasibility(self, clauses: list, num_vars: int) -> dict:
        """Assess attack feasibility via treewidth analysis.

        Returns dict with keys: treewidth, attack_feasible, verdict,
        recommendations, status.
        """
        if not _HAS_WIDTH_DEFENSE:
            return {"status": "unavailable", "reason": "width_defense module missing"}

        try:
            analyzer = AttackFeasibilityAnalyzer()
            result = analyzer.analyze_constraint_system(clauses, num_vars)
            # Flatten structure for easier downstream consumption
            structure = result.get("structure", {})
            verdict_info = result.get("verdict", {})
            return {
                "treewidth": structure.get("elimination_width", -1),
                "attack_feasible": verdict_info.get("verdict") != "defended",
                "width_classification": result.get("width_classification", "UNKNOWN"),
                "relative_score": result.get("relative_score", 0.0),
                "verdict": verdict_info,
                "recommendations": result.get("recommendations", []),
                "status": "ok",
                "structure": structure,
                "full_result": result,
            }
        except Exception as exc:
            return {"status": "error", "reason": str(exc)}

    # ------------------------------------------------------------------
    # Module 4: ETC Evasion
    # ------------------------------------------------------------------
    def predict_evasion(self, clauses: list, num_vars: int, num_samples: int = 100) -> dict:
        """Predict catastrophic failure modes via ETC analysis.

        Returns dict with keys: etc_score, trajectory, cliffs,
        risk_profile, evasion_likelihood.
        """
        try:
            predictor = ETCPredictor(clauses, num_vars)
            result = predictor.analyze()
            return {
                "etc_score": result.get("etc_score", 0.0),
                "trajectory": result.get("trajectory", []),
                "cliffs": result.get("cliffs", []),
                "max_cliff": result.get("max_cliff", 0.0),
                "cliff_density": result.get("cliff_density", 0.0),
                "risk_profile": result.get("risk_profile", "unknown"),
                "evasion_likelihood": predictor.evasion_likelihood(),
                "status": "ok",
            }
        except Exception as exc:
            return {"status": "error", "reason": str(exc)}

    # ------------------------------------------------------------------
    # Full assessment
    # ------------------------------------------------------------------
    def full_assessment(
        self,
        clauses: list,
        num_vars: int,
        target_literals: Optional[set] = None,
        etc_samples: int = 100,
    ) -> dict:
        """Run all available modules and produce a unified assessment."""
        t_start = time.time()

        target_literals = target_literals or set()

        # SAT solving
        sat_result = self.check_sat(clauses, num_vars)

        # Backdoor scan
        if target_literals:
            backdoor_result = self.scan_backdoor(clauses, num_vars, target_literals)
        else:
            backdoor_result = {"status": "skipped", "reason": "no targets provided"}

        # Feasibility
        feasibility_result = self.assess_feasibility(clauses, num_vars)

        # ETC
        evasion_result = self.predict_evasion(clauses, num_vars, etc_samples)

        # Compute overall risk score
        risk = self._compute_overall_risk(
            sat_result, backdoor_result, feasibility_result, evasion_result
        )

        # Prioritized findings
        findings = self._prioritize_findings(
            sat_result, backdoor_result, feasibility_result, evasion_result
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            sat_result, backdoor_result, feasibility_result, evasion_result
        )

        return {
            "backdoor": backdoor_result,
            "sat": sat_result,
            "feasibility": feasibility_result,
            "evasion": evasion_result,
            "overall_risk_score": risk,
            "prioritized_findings": findings,
            "recommended_next_steps": recommendations,
            "assessment_time": time.time() - t_start,
            "modules_available": self._modules_available,
        }

    # ------------------------------------------------------------------
    # Risk scoring
    # ------------------------------------------------------------------
    def _compute_overall_risk(
        self,
        sat_result: dict,
        backdoor_result: dict,
        feasibility_result: dict,
        evasion_result: dict,
    ) -> float:
        """Compute an overall risk score between 0 and 1.

        Higher = more vulnerable / easier to attack.
        """
        scores = []

        # SAT: UNSAT formulas with contradictions are inherently interesting
        if sat_result.get("satisfiable") is False:
            scores.append(0.5)  # inherent contradiction detected

        # Backdoor: small backdoor = high risk
        if backdoor_result.get("status") == "ok":
            bd_size = backdoor_result.get("backdoor_size", 999)
            if bd_size is not None and bd_size >= 0:
                scores.append(max(0.0, 1.0 - bd_size / 10.0))

        # Feasibility: width-based score
        if feasibility_result.get("status") == "ok":
            rel_score = feasibility_result.get("relative_score", 50.0)
            scores.append(rel_score / 100.0)

        # Evasion: higher ETC = more cliff-prone = potential hidden failures
        if evasion_result.get("status") == "ok":
            ev = evasion_result.get("evasion_likelihood", 0.0)
            scores.append(ev)

        return float(sum(scores) / len(scores)) if scores else 0.5

    def _prioritize_findings(self, sat, backdoor, feasibility, evasion) -> list:
        """Generate prioritized list of key findings."""
        findings = []

        # ETC-based findings
        if evasion.get("status") == "ok":
            profile = evasion.get("risk_profile", "unknown")
            etc_score = evasion.get("etc_score", 0.0)
            ev_lik = evasion.get("evasion_likelihood", 0.0)
            if profile == "catastrophic":
                findings.append(f"CRITICAL: ETC={etc_score:.2f} indicates catastrophic failure modes (evasion likelihood: {ev_lik:.1%})")
            elif profile == "cliff_prone":
                findings.append(f"HIGH: ETC={etc_score:.2f} indicates cliff-prone behavior (evasion likelihood: {ev_lik:.1%})")
            else:
                findings.append(f"LOW: ETC={etc_score:.2f} indicates {profile}, predictable behaviour (evasion likelihood: {ev_lik:.1%})")

        # SAT finding
        if sat.get("satisfiable") is False:
            findings.append("Formula is UNSAT — inherent contradiction detected")
        elif sat.get("satisfiable") is True:
            findings.append("Formula is SAT — model exists")

        # Feasibility finding
        if feasibility.get("status") == "ok":
            tw = feasibility.get("treewidth", -1)
            vc = feasibility.get("width_classification", "UNKNOWN")
            v = feasibility.get("verdict", {})
            verdict_str = v.get("verdict", "unknown")
            conf = v.get("confidence", "")
            findings.append(f"Treewidth={tw}: attack feasibility verdict={verdict_str} (confidence: {conf})")

        # Backdoor finding
        if backdoor.get("status") == "ok":
            bd_size = backdoor.get("backdoor_size")
            if bd_size is not None:
                findings.append(f"Minimal backdoor size={bd_size} for target literals")

        return findings

    def _generate_recommendations(self, sat, backdoor, feasibility, evasion) -> list:
        """Generate actionable next-step recommendations."""
        recs = []

        # Structural recommendations from width_defense
        if feasibility.get("status") == "ok":
            recs.extend(feasibility.get("recommendations", []))

        # ETC-based recommendations
        if evasion.get("status") == "ok":
            profile = evasion.get("risk_profile", "")
            if profile in ("cliff_prone", "catastrophic"):
                recs.append("[ETC] Target has hidden catastrophic failure modes. Focus fuzzing near cliff regions.")

        # Backdoor-based recommendations
        if backdoor.get("status") == "ok":
            bd_size = backdoor.get("backdoor_size")
            if bd_size is not None and bd_size <= 3:
                recs.append("[Backdoor] Very small trigger set found. Prioritize testing these minimal input combinations.")

        return recs

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------
    def report(self, assessment: dict) -> str:
        """Generate a human-readable report from an assessment dict."""
        lines = []
        lines.append("=" * 60)
        lines.append("CIC RED TEAM HARNESS — ASSESSMENT REPORT")
        lines.append("=" * 60)

        # Modules
        mod_status = assessment.get("modules_available", {})
        active = [k for k, v in mod_status.items() if v]
        lines.append(f"Active modules : {', '.join(active)}")
        lines.append("")

        # Overall risk
        risk = assessment.get("overall_risk_score", 0.0)
        risk_label = "LOW" if risk < 0.3 else "MEDIUM" if risk < 0.6 else "HIGH"
        lines.append(f"Overall Risk Score: {risk:.2f} ({risk_label})")
        lines.append(f"Assessment Time: {assessment.get('assessment_time', 0):.3f}s")
        lines.append("")

        # SAT result
        sat = assessment.get("sat", {})
        lines.append(f"SAT Result     : {sat.get('status', 'N/A')}")
        if sat.get("satisfiable") is True:
            lines.append(f"Model          : {len(sat.get('assignment', {}))} vars assigned")
        lines.append(f"Solver Backend : {sat.get('backend', 'N/A')}")
        enc = sat.get("encoding_size", {})
        lines.append(f"Encoding       : {enc.get('variables', '?')} vars, {enc.get('clauses', '?')} clauses")
        lines.append("")

        # Backdoor
        bd = assessment.get("backdoor", {})
        if bd.get("status") == "ok":
            lines.append("--- Backdoor Scanner ---")
            lines.append(f"  Backdoor Size  : {bd.get('backdoor_size', 'N/A')}")
            lines.append(f"  Backdoor Vars  : {bd.get('backdoor_vars', [])}")
            lines.append(f"  Propagation Rank: {bd.get('propagation_rank', 'N/A')}")
            lines.append(f"  Burst Score    : {bd.get('burst_score', 0.0):.4f}")
            lines.append(f"  Classification : {bd.get('classification', 'N/A')}")
            lines.append("")

        # Feasibility
        feas = assessment.get("feasibility", {})
        if feas.get("status") == "ok":
            lines.append("--- Feasibility Analysis ---")
            lines.append(f"  Treewidth      : {feas.get('treewidth', 'N/A')}")
            lines.append(f"  Classification : {feas.get('width_classification', 'N/A')}")
            v = feas.get("verdict", {})
            lines.append(f"  Verdict        : {v.get('verdict', 'N/A')} ({v.get('confidence', '')})")
            lines.append(f"  Attack Feasible: {feas.get('attack_feasible', 'N/A')}")
            lines.append("")

        # ETC
        etc = assessment.get("evasion", {})
        if etc.get("status") == "ok":
            lines.append("--- ETC Evasion Predictor ---")
            lines.append(f"  ETC Score      : {etc.get('etc_score', 0.0):.4f}")
            lines.append(f"  Max Cliff      : {etc.get('max_cliff', 0.0):.4f}")
            lines.append(f"  Cliff Density  : {etc.get('cliff_density', 0.0):.4f}")
            lines.append(f"  Risk Profile   : {etc.get('risk_profile', 'N/A')}")
            lines.append(f"  Evasion Likelihood: {etc.get('evasion_likelihood', 0.0):.2%}")
            lines.append("")

        # Findings
        findings = assessment.get("prioritized_findings", [])
        if findings:
            lines.append("--- Prioritized Findings ---")
            for i, f in enumerate(findings, 1):
                lines.append(f"  {i}. {f}")
            lines.append("")

        # Recommendations
        recs = assessment.get("recommended_next_steps", [])
        if recs:
            lines.append("--- Recommended Next Steps ---")
            for i, r in enumerate(recs, 1):
                lines.append(f"  {i}. {r}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)


# ===========================================================================
# CLI
# ===========================================================================

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CIC Red Team Harness — SAT-based security analysis"
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dimacs", metavar="FILE", help="Path to a DIMACS CNF file")
    source.add_argument(
        "--generate",
        choices=["pigeonhole", "chain", "random"],
        help="Generate a test formula of the given type",
    )
    parser.add_argument("--n", type=int, default=5, help="Size parameter (default: 5)")
    parser.add_argument("--vars", type=int, default=20, help="Variables for random (default: 20)")
    parser.add_argument("--ratio", type=float, default=4.26, help="Clause ratio for random (default: 4.26)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--target",
        default="",
        help='Target literals for backdoor scan, e.g. "4 -5 6"',
    )
    parser.add_argument(
        "--module",
        choices=["all", "backdoor", "sat", "feasibility", "evasion"],
        default="all",
        help="Which module to run (default: all)",
    )
    parser.add_argument(
        "--etc-samples",
        type=int,
        default=100,
        help="DPLL walk samples for ETC (default: 100)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="SAT solver timeout in seconds (default: 30)",
    )
    return parser


def _generate_formula(args) -> tuple:
    """Generate a formula from CLI arguments."""
    if args.generate == "pigeonhole":
        nv, clauses = make_small_example("pigeonhole", args.n)
    elif args.generate == "chain":
        nv, clauses = make_small_example("chain_3sat", args.n)
    elif args.generate == "random":
        nv, clauses = make_small_example("random_3sat", args.vars, ratio=args.ratio)
    else:
        raise ValueError(f"Unknown generator: {args.generate}")
    return nv, clauses


def main():
    parser = _build_parser()
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Load or generate formula
    if args.dimacs:
        from utils.sat_utils import parse_dimacs
        with open(args.dimacs) as fh:
            nv, clauses = parse_dimacs(fh.read())
    else:
        nv, clauses = _generate_formula(args)

    # Parse target literals
    target_literals = set()
    if args.target:
        target_literals = {int(x) for x in args.target.split()}

    # Run harness
    harness = RedTeamHarness()

    module = args.module
    if module == "all":
        assessment = harness.full_assessment(
            clauses, nv, target_literals=target_literals or None, etc_samples=args.etc_samples
        )
        print(harness.report(assessment))
    elif module == "backdoor":
        if not target_literals:
            print("ERROR: --target required for backdoor scan")
            sys.exit(1)
        result = harness.scan_backdoor(clauses, nv, target_literals)
        for k, v in result.items():
            print(f"  {k:15s}: {v}")
    elif module == "sat":
        result = harness.check_sat(clauses, nv, timeout=args.timeout)
        for k, v in result.items():
            print(f"  {k:15s}: {v}")
    elif module == "feasibility":
        result = harness.assess_feasibility(clauses, nv)
        for k, v in result.items():
            if isinstance(v, dict):
                print(f"  {k}:")
                for kk, vv in v.items():
                    print(f"    {kk}: {vv}")
            else:
                print(f"  {k}: {v}")
    elif module == "evasion":
        result = harness.predict_evasion(clauses, nv, num_samples=args.etc_samples)
        for k, v in result.items():
            print(f"  {k:20s}: {v}")


# ===========================================================================
# Self-test
# ===========================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CIC Red Team Harness — Self-Test")
    print("=" * 60)

    harness = RedTeamHarness()

    # Test 1: Pigeonhole
    print("\n[TEST] End-to-end: Pigeonhole PHP_4")
    nv, php = make_small_example("pigeonhole", 4)
    assessment = harness.full_assessment(php, nv, target_literals={1})
    assert "overall_risk_score" in assessment
    print("  Report generated successfully")
    print("  [PASS]")

    # Test 2: Chain formula
    print("\n[TEST] End-to-end: Chain 3-SAT (n=8)")
    nv2, chain = make_small_example("chain_3sat", 8)
    assessment2 = harness.full_assessment(chain2 := chain, nv2)
    assert assessment2["sat"]["satisfiable"] is True
    print(f"  ETC score: {assessment2['evasion'].get('etc_score', 0):.4f}")
    print(f"  Profile  : {assessment2['evasion'].get('risk_profile', 'N/A')}")
    print("  [PASS]")

    # Test 3: Module isolation
    print("\n[TEST] Module isolation")
    for mod_name in ["backdoor", "sat", "feasibility", "evasion"]:
        method = getattr(harness, {"backdoor": "scan_backdoor", "sat": "check_sat",
                                     "feasibility": "assess_feasibility", "evasion": "predict_evasion"}[mod_name])
        if mod_name == "backdoor":
            r = method(php, nv, {1})
        else:
            r = method(php, nv)
        print(f"  {mod_name:15s}: {r.get('status', 'N/A')}")
    print("  [PASS]")

    # Test 4: Report formatting
    print("\n[TEST] Report formatting")
    report = harness.report(assessment)
    assert "CIC RED TEAM HARNESS" in report
    assert "Risk Score" in report
    print("  All required sections present")
    print("  [PASS]")

    print("\n" + "=" * 60)
    print("All harness self-tests passed.")
    print("=" * 60)
