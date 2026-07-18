# P vs NP Dimension 12: Parameterized Complexity

## Overview
Parameterized complexity provides a framework for analyzing NP-hard problems by isolating a parameter of the problem.

## Key Concepts

### Parameterized Problem
A problem with an additional parameter k, denoted (I, k).

### FPT (Fixed-Parameter Tractable)
A problem is FPT if it can be solved in time f(k) * |I|^O(1).

### W-Hierarchy
W[1], W[2], ... form a hierarchy of parameterized complexity classes.

## Key Results

### Theorem 12.1
SAT parameterized by treewidth is FPT.

### Theorem 12.2
SAT parameterized by vertex cover number is FPT.

### Theorem 12.3
SAT parameterized by solution size is W[P]-hard.

## Connection to P vs NP

### Observation
If P = NP, then all parameterized NP problems are in P (and thus FPT).

### Converse
Showing that certain parameterized problems are not FPT would imply P != NP.

## The CIC Perspective

### Parameterized Information Complexity
IC(F, k) = information complexity of solving F with parameter k.

### Conjecture
IC(F, tw) <= O(tw * log n) for formulas with treewidth tw.

## Applications
1. **Algorithm Design**: FPT algorithms for structured instances
2. **Hardness Proofs**: W-hardness implies no FPT algorithm
3. **Practical Solving**: Use parameters to guide solver selection

## Status: Completed
