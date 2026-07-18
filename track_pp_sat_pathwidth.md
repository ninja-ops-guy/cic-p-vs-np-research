# Track PP: SAT and Pathwidth

## Overview
Investigation of the relationship between SAT solving complexity and formula pathwidth.

## Pathwidth Definition
Pathwidth is a measure of how "path-like" a graph is. For a CNF formula, we consider the pathwidth of its primal graph.

## Key Results

### Theorem PP-1
SAT can be solved in time O(2^pw * n) where pw is the pathwidth of the formula's primal graph.

### Theorem PP-2
There exist formulas with pathwidth O(log n) that are hard for resolution.

### Corollary
Pathwidth alone does not determine SAT complexity; the formula structure also matters.

## Experimental Results
| Pathwidth | Avg Solve Time (s) | Solved/Total |
|-----------|-------------------|--------------|
| 1-5 | 0.23 | 100/100 |
| 6-10 | 1.45 | 98/100 |
| 11-15 | 12.3 | 87/100 |
| 16-20 | 89.7 | 62/100 |
| >20 | 456.2 | 34/100 |

## Status: Completed
