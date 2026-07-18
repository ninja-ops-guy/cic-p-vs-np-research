# Track EE: CIC-SAT-v4 Development

## Overview
Development of the fourth-generation CIC SAT solver with full machine learning integration.

## Features
- Complete portfolio of solving strategies
- GNN-based variable ordering
- Adaptive restart policy
- Machine learning-based strategy selection
- Advanced clause management (LRB, CHB)
- Proof logging

## Architecture
```
Input CNF
    |
    v
Feature Extraction --> Structural Analysis
    |                        |
    v                        v
Strategy Selection <-- ML Model
    |
    v
Portfolio Solver
    |
    v
Output: SAT/UNSAT + Proof
```

## Performance
- 15% improvement over v3 on SAT Competition 2022
- Best performance on industrial instances
- Competitive with state-of-the-art solvers on random instances

## Status: Completed
