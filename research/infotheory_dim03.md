# Information Theory Dimension 3: Kolmogorov Complexity of Instances

## Overview
Analysis of the Kolmogorov complexity of SAT formula instances.

## Kolmogorov Complexity
K(x) = length of the shortest program that outputs x.

## Applications to SAT

### Result 3.1
Random SAT instances have high Kolmogorov complexity (K(F) = Theta(|F|)).

### Result 3.2
Industrial SAT instances have lower Kolmogorov complexity due to structure.

### Result 3.3
Instances with low K(F) are easier to solve (exploit structure).

## Relationship to CIC
Kolmogorov complexity and CIC are related but distinct:
- K(F) measures description length of the formula
- IC(F) measures information processed during solving
- K(F) can bound IC(F) but not vice versa

## Key Insight
The gap between K(F) and IC(F) is where computational complexity "lives".

## Status: Completed
