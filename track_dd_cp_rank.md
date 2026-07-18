# Track DD: Constraint Propagation Rank

## Overview
Analysis of constraint propagation rank and its relationship to SAT solving complexity.

## Propagation Rank
The propagation rank of a formula is the minimum number of rounds of unit propagation needed to either find a solution or prove unsatisfiability.

## Key Results

### Theorem DD-1
If a formula has propagation rank r, then it can be solved in time n^O(r).

### Theorem DD-2
Random k-SAT formulas at the satisfiability threshold have propagation rank Omega(n).

### Theorem DD-3 (Empirical)
Industrial instances typically have propagation rank O(log n).

## Connection to Treewidth
Propagation rank is related to but distinct from treewidth:
- rank(F) <= treewidth(F) + 1
- rank(F) can be much smaller than treewidth(F)

## Implications
Low propagation rank explains why CDCL solvers are effective on industrial instances.

## Status: Completed
