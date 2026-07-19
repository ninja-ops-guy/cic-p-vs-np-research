"""CIC Red Team Harness

A modular red teaming framework built on top of the CIC (Computational Information Complexity) research. Uses structural SAT analysis, necessity propagation theory, and entropy trajectory complexity to find vulnerabilities, assess attack feasibility, and predict catastrophic failure modes.

## Architecture

```
redteam_harness/
├── harness.py                      # Main orchestrator + CLI
├── modules/
│   ├── necessity_backdoor.py       # Module 1: NPT-based minimal trigger finder
│   ├── structural_sat.py           # Module 2: SAT encoder with width analysis
│   ├── width_defense.py            # Module 3: Treewidth attack feasibility
│   └── etc_evasion.py              # Module 4: ETC catastrophic failure predictor
├── utils/
│   ├── sat_utils.py                # DPLL solver, unit propagation, backbone
│   ├── graph_utils.py              # Primal graph construction
│   └── width_utils.py              # MinFill treewidth estimation
├── tests/
│   └── test_all.py                 # 31 unit/integration tests
└── README.md
```

## The Four Modules

### 1. Necessity Propagation Backdoor Scanner
**Based on Stage 18 research** — N_φ is a Galois closure operator.

Finds the **minimal set of conditions** that necessarily trigger a target behavior. Uses logical closure (unit propagation) rather than gradient descent, yielding **provably minimal** triggers.

Key capabilities:
- `find_minimal_trigger(target_literals)` — exhaustive search for smallest trigger
- `necessity_growth_profile(trigger)` — propagation trajectory revealing hidden coupling
- `burst_score(profile)` — detects intrinsically bursty vulnerabilities (Var(G) = Θ(n²) for PHP)
- `verify_closure_axioms()` — confirms extensivity, monotonicity, idempotence

### 2. Structural SAT Encoder
**Based on CIC-SAT v4 and Theorem 1** — width w implies resolution width ≤ max(w, k).

Encodes verification problems as SAT with structural difficulty analysis.

Key capabilities:
- `StructuralSATEncoder` — CNF formula builder with semantic variable naming
- `BoundedModelChecker` — unroll transition systems for vulnerability discovery
- `analyze_structure(clauses)` — full analysis: treewidth, difficulty, proof width bound

### 3. Treewidth Attack Feasibility Analyzer
**Based on Theorem 1 and Universal Tractability** — bounded width → polynomial proofs in 10 proof systems.

Assesses whether a system is structurally vulnerable to exhaustive attack.

| Width | Classification | Red-Team Verdict |
|-------|---------------|------------------|
| ≤ 3   | TRIVIAL       | Vulnerable (high confidence) |
| ≤ 10  | EASY          | Vulnerable (high confidence) |
| ≤ 25  | MODERATE      | Conditionally vulnerable |
| ≤ 50  | HARD          | Conditionally vulnerable |
| > 50  | EXTREME       | Defended |

### 4. ETC Evasion Predictor
**Based on Stage 17** — Entropy Trajectory Complexity.

Detects systems with "entropy cliffs" — sudden catastrophic failures after long stable periods. These systems appear robust in local testing but have hidden failure modes.

Key capabilities:
- `compute_etc(trajectory)` — total curvature of entropy trajectory
- `find_cliffs(trajectory)` — locate sudden entropy drops
- `risk_profile` — smooth / moderate / cliff_prone / catastrophic
- `evasion_likelihood()` — probability estimate based on ETC score

## Quick Start

### Requirements
- Python 3.9+
- networkx (`pip install networkx`)

### Run Tests
```bash
cd redteam_harness
python tests/test_all.py
```

### CLI Usage
```bash
# Full assessment of pigeonhole formula
python harness.py --generate pigeonhole --n 4 --module all

# Backdoor scan on chain formula
python harness.py --generate chain --n 8 --module backdoor --target "4"

# Feasibility analysis on random formula
python harness.py --generate random --n 20 --module feasibility

# ETC analysis with more samples
python harness.py --generate random --n 15 --module evasion --etc-samples 200

# From DIMACS file
python harness.py --dimacs file.cnf --module all --target "1 -2 3"
```

### Python API
```python
from harness import RedTeamHarness
from utils.sat_utils import make_small_example

harness = RedTeamHarness()

# Generate a test formula
nv, clauses = make_small_example("pigeonhole", 4)

# Run full assessment
assessment = harness.full_assessment(clauses, nv, target_literals={1})

# Generate report
print(harness.report(assessment))
```

### Module 1: Backdoor Scanner
```python
from modules.necessity_backdoor import NecessityClosure, BackdoorScanner

closure = NecessityClosure(clauses, num_vars)
scanner = BackdoorScanner(closure)

# Find minimal trigger for target behavior
trigger = scanner.find_minimal_trigger(target_literals={4}, max_size=5)
profile = scanner.necessity_growth_profile(trigger)
classification = scanner.classify_vulnerability(trigger)
```

### Module 3: Feasibility Analyzer
```python
from modules.width_defense import AttackFeasibilityAnalyzer

analyzer = AttackFeasibilityAnalyzer()
result = analyzer.analyze_constraint_system(clauses, num_vars, "TargetSystem")
# result['verdict'] = {'verdict': 'vulnerable', 'confidence': 'high', ...}
```

### Module 4: ETC Predictor
```python
from modules.etc_evasion import ETCPredictor

predictor = ETCPredictor(clauses, num_vars)
result = predictor.analyze()
# result = {'etc_score': 1.23, 'risk_profile': 'cliff_prone', ...}
```

## Research Foundation

| Module | Research Stage | Key Theorem |
|--------|---------------|-------------|
| Backdoor Scanner | Stage 18 | N_φ is a Galois closure operator |
| Structural SAT | Stages 1-8 | Theorem 1: width w → res-width ≤ max(w,k) |
| Feasibility | Stages 9-12 | Universal Tractability (10 proof systems) |
| ETC Predictor | Stage 17 | ETC(φ) = O(w·n) for treewidth w |

## Test Results

```
Ran 31 tests in 0.269s
OK
```

Tests cover:
- SAT solving (DPLL, unit propagation, backbone)
- Graph construction and width computation
- Galois closure operator axioms
- Minimal trigger finding
- Attack feasibility classification
- ETC computation and cliff detection
- Full harness integration
- Report generation

## License

Research prototype. Not for production security decisions without expert review.
"""