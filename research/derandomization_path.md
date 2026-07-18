# Derandomization Path

## Overview
Analysis of derandomization techniques and their implications for P vs NP.

## Key Conjectures

### Conjecture 1: P = BPP
If P = BPP, then randomness doesn't help polynomial-time computation.

### Conjecture 2: Circuit Lower Bounds Imply Derandomization
If E requires exponential circuits, then P = BPP.

### Conjecture 3: Hardness Amplification
Weak hardness can be amplified to strong hardness.

## Current State
- **Pseudorandom Generators**: Constructed from hardness assumptions
- **Derandomization**: Partial results for specific algorithms
- **BPP vs P**: Widely believed to be equal

## Implications for P vs NP
1. If P = BPP and BPP = NP, then P = NP
2. Derandomization requires circuit lower bounds
3. Circuit lower bounds imply P != NP

## The CIC Perspective
Information complexity provides a lens:
- Randomness provides information
- Derandomization simulates this information deterministically
- If information can be compressed, derandomization is possible

## Status: Completed
