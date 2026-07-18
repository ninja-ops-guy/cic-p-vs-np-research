# Information Theory Dimension 2: Conditional Information Complexity

## Overview
Analysis of conditional information complexity in computational problems.

## Conditional Information Complexity
For problems P and Q:
IC(P | Q) = IC(P, Q) - IC(Q)

This measures the additional information needed to solve P given a solution to Q.

## Applications to SAT

### Result 2.1
IC(SAT_n | SAT_{n-1}) >= Omega(1)

Each additional variable adds at least constant information complexity.

### Result 2.2
If P = NP, then IC(SAT | any P problem) <= poly(log n).

### Result 2.3 (Empirical)
Conditional information measures predict incremental solving difficulty.

## Chain Rule
The chain rule for CIC:
IC(P_1, P_2, ..., P_k) <= sum_i IC(P_i | P_1, ..., P_{i-1})

This is an inequality (not equality) for CIC, unlike Shannon information.

## Status: Completed
