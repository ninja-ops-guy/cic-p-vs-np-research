# Information Theory Dimension 1: Entropy of Formula Distributions

## Overview
Analysis of the entropy of probability distributions over SAT formula instances.

## Formula Distributions

### Random k-SAT
The distribution of random k-CNF formulas with n variables and m clauses.

### Industrial Distribution
The distribution of SAT instances arising from practical applications.

## Entropy Analysis

### Definition
For a distribution D over formulas:
H(D) = -E_{F~D}[log P(F)]

### Key Results

#### Result 1.1
Random k-SAT at density alpha has entropy H = Theta(n log n).

#### Result 1.2
Industrial formula distributions have lower entropy than random distributions.

#### Result 1.3 (Empirical)
Entropy of the formula distribution correlates with average solving difficulty.

## Applications
1. **Instance Generation**: Generate formulas with desired entropy
2. **Hardness Prediction**: Use entropy to predict difficulty
3. **Benchmark Design**: Create balanced benchmark sets

## Status: Completed
