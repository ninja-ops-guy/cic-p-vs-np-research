"""CIC Red Team Harness

Main orchestrator that integrates all research-based modules for
SAT-based security red teaming.

Usage::

    from harness import RedTeamHarness
    harness = RedTeamHarness()
    assessment = harness.full_assessment(clauses, num_vars)
    print(harness.report(assessment))
"""

__version__ = "0.1.0"
__all__ = ["RedTeamHarness"]
