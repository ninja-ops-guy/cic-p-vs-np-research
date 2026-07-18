# Track BB: MaxSAT Extension

## Overview
Extension of the CIC framework to Maximum Satisfiability (MaxSAT).

## MaxSAT Problem
Given a CNF formula, find an assignment that maximizes the number of satisfied clauses.

## Key Results

### Theorem BB-1
MaxSAT is NP-hard (even for approximation within factor 2).

### Theorem BB-2
The CIC of MaxSAT on n variables and m clauses is at least Omega(n + log m).

### Theorem BB-3 (Empirical)
Optimal solutions to MaxSAT tend to have low treewidth.

## Connection to SAT
- SAT asks "can all clauses be satisfied?"
- MaxSAT asks "how many clauses can be satisfied?"
- The CIC framework extends naturally from SAT to MaxSAT

## Algorithms
- Branch and bound with width-based pruning
- SDP relaxation for upper bounds
- Local search with structure-aware initialization

## Status: Completed
