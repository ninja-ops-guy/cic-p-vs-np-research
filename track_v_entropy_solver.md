# Track V: Entropy-Based SAT Solver

## Overview
Development of a SAT solver that uses entropy-based heuristics for variable and value selection.

## Key Idea
Use information-theoretic measures to guide the search process. Variables that maximally reduce the entropy of the solution space are preferred.

## Approach
1. Compute entropy of each variable's marginal distribution
2. Select variable that maximizes information gain
3. Use entropy decay as a measure of search progress

## Results
- Entropy-based branching reduces iterations by 15-20% on structured instances
- Less effective on random instances where entropy is uniform
- Complementary to VSIDS heuristic

## Status: Completed
