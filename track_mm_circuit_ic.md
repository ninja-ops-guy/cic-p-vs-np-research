# Track MM: Circuit Information Complexity

## Overview
Application of information complexity measures to circuit complexity analysis.

## Circuit Information Complexity
For a circuit C computing function f:
IC(C) = Sum over all gates of the information processed

## Key Results

### Theorem MM-1
Any circuit computing PARITY_n has IC >= Omega(n).

### Theorem MM-2
If NP has polynomial-size circuits, then IC(SAT_n) <= poly(n).

### Theorem MM-3 (Conjecture)
IC(SAT_n) >= Omega(n^2) for all circuit families.

## Approach
1. Define information complexity for circuits
2. Prove lower bounds using information-theoretic arguments
3. Connect to traditional circuit complexity measures

## Implications
If the conjecture holds, then NP does not have polynomial-size circuits, implying P != NP.

## Status: Ongoing
