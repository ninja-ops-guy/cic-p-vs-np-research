# Session 3: Quantum vs Classical Comparison

## Overview
Comparison of quantum and classical approaches to SAT solving and complexity analysis.

## Classical SAT Solving

### State of the Art
- CDCL solvers (Glucose, Kissat, etc.)
- Runtime: Exponential in worst case, efficient in practice
- Best known algorithm: PPSZ (O(2^0.386n))

### Limitations
- No known polynomial-time algorithm
- Exponential lower bounds for restricted classes
- Barriers: Relativization, Natural Proofs, Algebrization

## Quantum SAT Solving

### Approaches
1. **Grover's Algorithm**: O(2^(n/2)) queries
2. **Amplitude Amplification**: O(2^(n/2)) queries
3. **Quantum Walks**: O(2^(n/3)) queries (conjectured)
4. **Adiabatic**: D-Wave approach (heuristic)

### Advantages
- Quadratic speedup (Grover) proven
- Potential for super-quadratic speedups
- Different computational model

### Limitations
- Requires quantum hardware (not yet available at scale)
- Query complexity != time complexity
- Error correction overhead

## Complexity Class Implications
| Class | Classical | Quantum |
|-------|-----------|---------|
| P | Deterministic poly-time | BQP |
| NP | Nondet poly-time | QMA |
| PSPACE | Poly space | Same |

## Conclusion
Quantum computing offers interesting perspectives but does not directly resolve P vs NP. The question remains whether BQP contains NP, which is a related but distinct open problem.
