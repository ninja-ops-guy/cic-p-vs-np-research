# MCSP Algorithms

## Overview
Algorithms for the Minimum Circuit Size Problem (MCSP) and their analysis.

## MCSP Problem
Given a truth table of a Boolean function f and a size parameter s, does f have a circuit of size at most s?

## Key Results

### Theorem MCSP-1
MCSP is in NP.

### Theorem MCSP-2
If MCSP is in P, then there are no cryptographically secure pseudorandom generators.

### Theorem MCSP-3
MCSP is hard for average-case complexity.

## Algorithms for MCSP

### Exact Algorithm
Brute force: O(2^(s log s)) time.

### Approximation Algorithm
Greedy approach: O(2^n) time, factor O(log n) approximation.

### Heuristic
SAT-based: Encode MCSP as SAT and solve.

## Connection to P vs NP
- MCSP is "meta-complexity": the complexity of computing complexity
- Understanding MCSP may shed light on P vs NP
- If MCSP is easy, pseudorandomness is weak

## Status: Completed
