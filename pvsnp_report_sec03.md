# Section 3: Theoretical Framework

## Computational Information Complexity (CIC)

### Motivation
Traditional complexity measures (time, space) describe resources used by algorithms. CIC measures the information that must be processed, which is a fundamental characteristic of the problem itself.

### Formal Definition
**Definition 3.1** (Computational Information Complexity). For a computational problem P and algorithm A solving P:

IC(A) = max_{instance x} IC(A, x)

where IC(A, x) is the information content of the computational transcript of A on x.

The CIC of P is:
IC(P) = inf_{A solves P} IC(A)

### Properties
1. **Monotonicity**: If P reduces to Q, then IC(P) <= IC(Q) + O(log n)
2. **Composition**: IC(P o Q) <= IC(P) + IC(Q)
3. **Lower bound**: IC(P) >= log |P^{-1}(1)| for decision problems

### Connection to Existing Measures
| Measure | Relationship to CIC |
|---------|-------------------|
| Time | Time >= IC (information must be processed) |
| Space | Space >= IC / depth |
| Circuit Size | Size >= IC / log size |
| Query Complexity | Queries >= IC / log answers |

## Propagation Tightness

### Definition
**Definition 3.2** (Propagation Tightness). For a CNF formula F:

pt(F) = min_{variable ordering pi} |{clauses activated by unit propagation under pi}|

### Properties
1. pt(F) <= treewidth(F) + 1
2. pt(F) >= minimum vertex cover of the conflict graph
3. pt(F) is NP-hard to compute exactly

## Width Measures

### Treewidth
The treewidth of a formula's primal graph is a fundamental structural parameter.

### Pathwidth
Pathwidth is a restricted form of treewidth where the tree decomposition must be a path.

### Relationship
pathwidth(F) >= treewidth(F) >= branchwidth(F)

## Summary
The CIC framework provides a unified view of computational complexity through information-theoretic and structural measures.
