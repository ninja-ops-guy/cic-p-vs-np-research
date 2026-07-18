# P vs NP Dimension 6: Space Complexity

## Overview
Analysis of space complexity and its relationship to P vs NP.

## Key Results

### Theorem 6.1
SAT is PSPACE-complete when instances are allowed to have exponential size.

### Theorem 6.2
For polynomial-size instances, SAT is in PSPACE (trivially).

### Theorem 6.3
If P = NP, then P = PSPACE.

## Space vs Time
| Class | Time | Space |
|-------|------|-------|
| L | O(log n) space | - |
| NL | O(log n) space | nondet |
| P | poly time | poly space |
| NP | nondet poly time | poly space |
| PSPACE | - | poly space |

## Implications
Space complexity provides a different perspective:
- PSPACE is "very large"
- NP is in PSPACE
- Understanding space helps understand time

## Status: Completed
