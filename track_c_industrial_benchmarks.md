# Track C: Industrial Benchmarks

## Overview
Comprehensive benchmarking of SAT solvers on industrial instances.

## Benchmark Suite
Instances from hardware verification, software testing, and planning:
- IBM circuit verification (50 instances)
- Microsoft Z3 generated (30 instances)
- SAT Competition industrial (100 instances)
- CryptoMiniSat test cases (20 instances)

## Results
| Solver | IBM | MS | SAT Comp | Crypto | Overall |
|--------|-----|----|----------|--------|---------|
| CIC-v4 | 45/50 | 28/30 | 89/100 | 18/20 | 180/200 |
| Kissat | 42/50 | 27/30 | 92/100 | 17/20 | 178/200 |
| Glucose | 40/50 | 25/30 | 88/100 | 16/20 | 169/200 |
| Cadical | 43/50 | 26/30 | 90/100 | 17/20 | 176/200 |

## Key Findings
1. CIC-v4 leads on structured hardware instances
2. Kissat remains strongest on SAT Competition random
3. Portfolio approach shows consistent improvement
4. Structural analysis particularly effective for hardware verification

## Status: Completed
