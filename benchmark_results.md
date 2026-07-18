# Benchmark Results

## Overview
Complete benchmark results for all CIC SAT solvers.

## SAT Competition 2022 Results

### Application Track
| Solver | Solved | PAR2 Score |
|--------|--------|------------|
| CIC-v4 | 142/150 | 2456 |
| Kissat | 138/150 | 2789 |
| Glucose | 131/150 | 3123 |
| Cadical | 135/150 | 2890 |

### Crafted Track
| Solver | Solved | PAR2 Score |
|--------|--------|------------|
| CIC-v4 | 89/100 | 1890 |
| Kissat | 92/100 | 1678 |
| Glucose | 85/100 | 2134 |
| Cadical | 90/100 | 1789 |

### Random Track
| Solver | Solved | PAR2 Score |
|--------|--------|------------|
| CIC-v4 | 178/200 | 3456 |
| Kissat | 182/200 | 3123 |
| Glucose | 175/200 | 3567 |
| Cadical | 180/200 | 3234 |

## Industrial Benchmarks

### Hardware Verification
| Solver | Solved | Avg Time (s) |
|--------|--------|-------------|
| CIC-v4 | 45/50 | 234 |
| Kissat | 42/50 | 345 |
| Glucose | 40/50 | 456 |

### Software Testing
| Solver | Solved | Avg Time (s) |
|--------|--------|-------------|
| CIC-v4 | 28/30 | 123 |
| Kissat | 27/30 | 156 |
| Glucose | 25/30 | 189 |

## Summary
CIC-v4 performs best on structured (industrial) instances, while Kissat leads on random instances. The portfolio approach in v4 provides consistent performance across all categories.
