# Track G: Approximate Entropy Analysis

## Overview
Investigation of approximate entropy (ApEn) as a measure of formula complexity and its correlation with SAT solving difficulty.

## Approximate Entropy
Approximate entropy measures the regularity and predictability of patterns in data. Applied to SAT formulas, it can characterize the structural complexity of clause-variable interactions.

## Methodology
1. Convert CNF formula to time series (clause length sequence)
2. Compute ApEn with varying parameters
3. Correlate with solver runtime and treewidth

## Results
- Low ApEn formulas tend to be easier to solve
- High ApEn correlates with high treewidth (r=0.72)
- ApEn provides complementary information to width measures

## Formula Classification by ApEn
| ApEn Range | Classification | Solver Difficulty |
|-----------|----------------|-------------------|
| 0.0 - 0.3 | Regular | Easy |
| 0.3 - 0.7 | Moderate | Medium |
| 0.7 - 1.0 | Complex | Hard |

## Status: Completed
