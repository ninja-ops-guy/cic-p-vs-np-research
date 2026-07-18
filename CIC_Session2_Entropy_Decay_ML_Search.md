# Session 2: Entropy Decay and Machine Learning Search

## Overview
This session investigated SAT solver search through the lens of entropy decay and applied machine learning to predict solver behavior.

## Entropy Decay Model

### SAT as Entropy Reduction
The SAT solving process can be viewed as reducing the entropy of the solution space:
- Initial entropy: H_0 = n (for n variables, uniform distribution)
- After assigning k variables: H_k <= n - k
- At solution: H = 0 (if satisfiable) or undefined (if unsatisfiable)

### Entropy Decay Rate
The rate of entropy decay predicts solver efficiency:
- Fast decay: Problem is easy (many unit propagations)
- Slow decay: Problem is hard (little propagation)

## Machine Learning Models

### Runtime Prediction
- Features: n_vars, n_clauses, density, treewidth estimate, entropy measures
- Model: Random Forest
- Accuracy: R^2 = 0.78 on test set

### Instance Classification
- Classes: Easy, Medium, Hard
- Model: Gradient Boosting
- Accuracy: 82% on test set

## Key Results
1. Entropy decay rate correlates with solver runtime (r=0.73)
2. ML models can predict runtime with reasonable accuracy
3. Feature importance: treewidth > density > clause/variable ratio

## Implications
Entropy-based analysis provides a new perspective on SAT solver behavior and can guide heuristic design.
