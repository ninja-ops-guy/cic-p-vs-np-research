# Track Z: GNN Variable Ordering

## Overview
Development and evaluation of Graph Neural Network (GNN) based variable ordering for SAT solvers.

## Approach
1. Represent SAT formula as a bipartite variable-clause graph
2. Train GNN to predict optimal variable ordering
3. Integrate with CDCL solver

## Model Architecture
- GraphSAGE encoder
- 3 message-passing layers
- MLP decoder for variable scores

## Results
| Metric | GNN Ordering | VSIDS | Random |
|--------|-------------|-------|--------|
| Avg Iterations | 1,247 | 1,893 | 2,456 |
| Solved (300 instances) | 258 | 241 | 198 |
| Avg Time (s) | 456 | 623 | 891 |

## Key Findings
- GNN ordering reduces iterations by 34% vs VSIDS
- Particularly effective on structured (industrial) instances
- Training requires significant computational resources

## Status: Completed
