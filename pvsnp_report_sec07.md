# Section 7: Machine Learning Approaches

## Overview
Application of machine learning to SAT solving and complexity analysis.

## GNN Variable Ordering

### Problem
Choose the next variable to branch on in CDCL.

### Approach
Represent the formula as a bipartite graph and use Graph Neural Networks to score variables.

### Architecture
- Input: Variable-clause bipartite graph
- Encoder: 3-layer GraphSAGE
- Decoder: MLP scoring function
- Output: Variable scores

### Results
- 34% reduction in solving iterations
- 82% accuracy on variable selection
- Particularly effective on structured instances

## Runtime Prediction

### Features
- n_vars, n_clauses, density
- Treewidth estimate
- Entropy measures
- Graph spectral properties

### Model
Random Forest with 100 trees

### Results
- R^2 = 0.78 on test set
- Useful for portfolio selection
- Identifies key structural features

## Portfolio Selection

### Approach
Train a classifier to select the best solver for each instance.

### Features
Same as runtime prediction plus solver performance history.

### Results
- 12% improvement over best single solver
- Reduces timeout rate by 40%
- Learns to match instances to solvers

## Conclusion
ML provides significant practical improvements and reveals structural insights about SAT instances.
